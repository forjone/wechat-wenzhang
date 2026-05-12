# 东京固定 IP 微信出口代理开发与部署说明

本文档说明：东京固定 IP 服务器上需要开发什么、如何部署、如何和 NAS 上的 `superfa-ai-agent` 对接。

目标架构：

```text
NAS / Hermes 本地机器
  ├─ 采集 AIHot / RSS
  ├─ 生成公众号文章 Markdown / HTML / metadata
  ├─ 保存 SQLite 和 outputs/articles/*
  └─ 调用东京服务器代理接口

东京固定 IP 服务器
  └─ 只做微信公众号 API 出口代理
      ├─ 保存 WECHAT_APPID / WECHAT_APPSECRET
      ├─ 获取并缓存 access_token
      ├─ 创建微信公众号草稿
      └─ 可选：提交发布/freepublish
```

东京服务器不负责采集、不负责生成文章、不负责保存知识库。它只负责从固定公网 IP 调用微信接口。

---

## 1. 东京服务器需要开发的服务

建议开发一个很小的 FastAPI 服务，提供 3 个接口：

| 接口 | 方法 | 用途 |
|---|---:|---|
| `/healthz` | GET | 健康检查 |
| `/wechat/draft/add` | POST | 创建微信公众号草稿 |
| `/wechat/freepublish/submit` | POST | 可选：提交发布/群发 |

NAS 已经按这个协议实现了客户端。

### 1.1 鉴权方式

使用共享密钥即可：

```http
Authorization: Bearer <PROXY_API_KEY>
```

东京服务器检查请求头，不正确就返回 401。

### 1.2 多公众号账号

NAS 请求体里会传：

```json
{
  "account": "hao1",
  "article": { ... }
}
```

东京服务器根据 `account` 找到对应的微信公众号 `appid` 和 `appsecret`。

建议东京服务器 `.env` 配置：

```env
PROXY_API_KEY=replace-with-long-random-token
WECHAT_ACCOUNTS=hao1:appid1:secret1,hao2:appid2:secret2
TOKEN_DIR=/opt/wechat-proxy/tokens
```

如果只有一个公众号，也可以只配置一个账号：

```env
WECHAT_ACCOUNTS=default:appid:secret
```

---

## 2. 微信代理接口协议

### 2.1 创建草稿

NAS 请求：

```http
POST /wechat/draft/add
Authorization: Bearer <PROXY_API_KEY>
Content-Type: application/json
```

请求体：

```json
{
  "account": "hao1",
  "article": {
    "title": "AI简报001｜2026年5月9日：今日AI信号源",
    "author": "超级发",
    "digest": "摘要，可为空",
    "content_html": "<section>...</section>",
    "thumb_media_id": "",
    "content_source_url": "",
    "need_open_comment": 1,
    "only_fans_can_comment": 0
  }
}
```

东京代理调用微信：

```text
POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=<ACCESS_TOKEN>
```

微信请求体：

```json
{
  "articles": [
    {
      "title": "...",
      "author": "超级发",
      "digest": "...",
      "content": "<section>...</section>",
      "thumb_media_id": "...",
      "content_source_url": "",
      "need_open_comment": 1,
      "only_fans_can_comment": 0
    }
  ]
}
```

东京代理返回给 NAS：

```json
{
  "media_id": "微信返回的草稿 media_id"
}
```

> 注意：微信草稿一般要求 `thumb_media_id`。如果为空，微信可能报错。第一阶段可以先用已经上传好的封面素材 ID 配置一个默认值，或者后续再实现封面上传接口。

### 2.2 提交发布 / freepublish，可选

NAS 请求：

```http
POST /wechat/freepublish/submit
Authorization: Bearer <PROXY_API_KEY>
Content-Type: application/json
```

请求体：

```json
{
  "account": "hao1",
  "media_id": "草稿 media_id",
  "draft_id": "草稿 media_id"
}
```

东京代理调用微信：

```text
POST https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token=<ACCESS_TOKEN>
```

微信请求体：

```json
{
  "media_id": "草稿 media_id"
}
```

东京代理返回：

```json
{
  "publish_id": "微信返回的 publish_id"
}
```

> NAS 侧仍然需要 `AUTO_PUBLISH=true` 加 `--publish-confirm` 才会调用这个接口。默认只创建草稿。

---

## 3. 推荐目录结构

东京服务器上建议放在：

```text
/opt/wechat-proxy/
├── app.py
├── requirements.txt
├── .env
├── tokens/
└── systemd/
    └── wechat-proxy.service
```

---

## 4. 最小可用 FastAPI 实现

### 4.1 requirements.txt

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-dotenv==1.0.1
requests==2.32.3
```

### 4.2 app.py

```python
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

PROXY_API_KEY = os.getenv("PROXY_API_KEY", "")
TOKEN_DIR = Path(os.getenv("TOKEN_DIR", "/opt/wechat-proxy/tokens"))
TOKEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Superfa WeChat Fixed-IP Proxy")


class WeChatAccount(BaseModel):
    name: str
    appid: str
    appsecret: str


class ArticlePayload(BaseModel):
    title: str
    author: str = "超级发"
    digest: str = ""
    content_html: str
    thumb_media_id: str = ""
    content_source_url: str = ""
    need_open_comment: int = 1
    only_fans_can_comment: int = 0


class DraftAddRequest(BaseModel):
    account: str = "default"
    article: ArticlePayload


class PublishRequest(BaseModel):
    account: str = "default"
    media_id: str = ""
    draft_id: str = ""


def parse_accounts(raw: str) -> dict[str, WeChatAccount]:
    accounts: dict[str, WeChatAccount] = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":", 2)
        if len(parts) != 3:
            raise RuntimeError(f"Invalid WECHAT_ACCOUNTS item: {chunk}")
        name, appid, appsecret = [p.strip() for p in parts]
        accounts[name] = WeChatAccount(name=name, appid=appid, appsecret=appsecret)
    return accounts


ACCOUNTS = parse_accounts(os.getenv("WECHAT_ACCOUNTS", ""))


def require_auth(authorization: str = Header(default="")) -> None:
    if not PROXY_API_KEY:
        raise HTTPException(status_code=500, detail="PROXY_API_KEY is not configured")
    expected = f"Bearer {PROXY_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="unauthorized")


def get_account(name: str) -> WeChatAccount:
    account = ACCOUNTS.get(name)
    if not account:
        available = ", ".join(sorted(ACCOUNTS)) or "none"
        raise HTTPException(status_code=400, detail=f"WECHAT_ACCOUNT_NOT_FOUND: {name}. Available: {available}")
    return account


def token_file(account_name: str) -> Path:
    safe = "".join(ch for ch in account_name if ch.isalnum() or ch in "-_") or "default"
    return TOKEN_DIR / f"token_{safe}.json"


def read_cached_token(account_name: str) -> str | None:
    path = token_file(account_name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if data.get("access_token") and int(data.get("expires_at", 0)) > int(time.time()):
        return str(data["access_token"])
    return None


def get_access_token(account: WeChatAccount, force_refresh: bool = False) -> str:
    if not force_refresh:
        cached = read_cached_token(account.name)
        if cached:
            return cached

    resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": account.appid,
            "secret": account.appsecret,
        },
        timeout=20,
    )
    data = resp.json()
    if "access_token" not in data:
        raise HTTPException(status_code=502, detail={"error": "WECHAT_TOKEN_FAILED", "wechat": data})

    expires_at = int(time.time()) + int(data.get("expires_in", 7200)) - 300
    token_file(account.name).write_text(
        json.dumps({"access_token": data["access_token"], "expires_at": expires_at}, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(data["access_token"])


def post_wechat_json(path: str, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
    resp = requests.post(
        f"https://api.weixin.qq.com{path}",
        params={"access_token": access_token},
        json=payload,
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"error": "WECHAT_INVALID_JSON", "body": resp.text[:500]}) from exc
    return data


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return {"status": "ok", "accounts": sorted(ACCOUNTS.keys())}


@app.post("/wechat/draft/add", dependencies=[Depends(require_auth)])
def add_draft(req: DraftAddRequest) -> dict[str, Any]:
    account = get_account(req.account)
    access_token = get_access_token(account)
    article = req.article

    payload = {
        "articles": [
            {
                "title": article.title,
                "author": article.author,
                "digest": article.digest[:120],
                "content": article.content_html,
                "thumb_media_id": article.thumb_media_id,
                "content_source_url": article.content_source_url,
                "need_open_comment": article.need_open_comment,
                "only_fans_can_comment": article.only_fans_can_comment,
            }
        ]
    }
    data = post_wechat_json("/cgi-bin/draft/add", access_token, payload)
    if "media_id" not in data:
        raise HTTPException(status_code=502, detail={"error": "WECHAT_DRAFT_CREATE_FAILED", "wechat": data})
    return {"media_id": data["media_id"]}


@app.post("/wechat/freepublish/submit", dependencies=[Depends(require_auth)])
def freepublish_submit(req: PublishRequest) -> dict[str, Any]:
    account = get_account(req.account)
    media_id = req.media_id or req.draft_id
    if not media_id:
        raise HTTPException(status_code=400, detail="media_id is required")

    access_token = get_access_token(account)
    data = post_wechat_json("/cgi-bin/freepublish/submit", access_token, {"media_id": media_id})
    if "publish_id" not in data:
        raise HTTPException(status_code=502, detail={"error": "WECHAT_PUBLISH_FAILED", "wechat": data})
    return {"publish_id": data["publish_id"]}
```

---

## 5. 东京服务器部署步骤

以下假设服务器是 Ubuntu 22.04/24.04。

### 5.1 安装系统依赖

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx curl
```

### 5.2 创建目录和用户

```bash
sudo useradd --system --home /opt/wechat-proxy --shell /usr/sbin/nologin wechat-proxy || true
sudo mkdir -p /opt/wechat-proxy/tokens
sudo chown -R wechat-proxy:wechat-proxy /opt/wechat-proxy
```

### 5.3 放置代码

```bash
cd /opt/wechat-proxy
sudo vi requirements.txt
sudo vi app.py
sudo vi .env
```

`.env` 示例：

```env
PROXY_API_KEY=请换成一串很长的随机密钥
WECHAT_ACCOUNTS=hao1:微信公众号appid1:微信公众号secret1,hao2:微信公众号appid2:微信公众号secret2
TOKEN_DIR=/opt/wechat-proxy/tokens
```

权限：

```bash
sudo chown -R wechat-proxy:wechat-proxy /opt/wechat-proxy
sudo chmod 600 /opt/wechat-proxy/.env
```

### 5.4 创建虚拟环境

```bash
cd /opt/wechat-proxy
sudo -u wechat-proxy python3 -m venv .venv
sudo -u wechat-proxy /opt/wechat-proxy/.venv/bin/pip install -r requirements.txt
```

### 5.5 本地启动测试

```bash
sudo -u wechat-proxy /opt/wechat-proxy/.venv/bin/uvicorn app:app --host 127.0.0.1 --port 18080
```

另开一个终端测试：

```bash
curl http://127.0.0.1:18080/healthz
```

应该返回：

```json
{"status":"ok","accounts":["hao1","hao2"]}
```

---

## 6. systemd 服务

创建：

```bash
sudo vi /etc/systemd/system/wechat-proxy.service
```

内容：

```ini
[Unit]
Description=Superfa WeChat Fixed-IP Proxy
After=network.target

[Service]
Type=simple
User=wechat-proxy
Group=wechat-proxy
WorkingDirectory=/opt/wechat-proxy
EnvironmentFile=/opt/wechat-proxy/.env
ExecStart=/opt/wechat-proxy/.venv/bin/uvicorn app:app --host 127.0.0.1 --port 18080
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wechat-proxy
sudo systemctl status wechat-proxy
```

查看日志：

```bash
journalctl -u wechat-proxy -f
```

---

## 7. Nginx 反向代理和 HTTPS

建议只暴露 HTTPS，不直接暴露 uvicorn。

### 7.1 Nginx 配置

```bash
sudo vi /etc/nginx/sites-available/wechat-proxy
```

内容：

```nginx
server {
    listen 80;
    server_name tokyo.example.com;

    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用：

```bash
sudo ln -sf /etc/nginx/sites-available/wechat-proxy /etc/nginx/sites-enabled/wechat-proxy
sudo nginx -t
sudo systemctl reload nginx
```

### 7.2 配置 HTTPS

如果有域名，推荐用 certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tokyo.example.com
```

---

## 8. 微信后台 IP 白名单

在微信公众号后台，把东京服务器公网 IP 加入 IP 白名单。

在东京服务器上查询出口 IP：

```bash
curl https://ifconfig.me
```

把输出的 IP 填到微信公众平台后台。

---

## 9. 从 NAS 测试代理

NAS 上 `.env` 配置：

```env
WECHAT_PROXY_URL=https://tokyo.example.com
WECHAT_PROXY_API_KEY=和东京服务器 PROXY_API_KEY 一致
WECHAT_PROXY_TIMEOUT=30
```

测试健康检查：

```bash
curl https://tokyo.example.com/healthz
```

测试代理鉴权：

```bash
curl -X POST https://tokyo.example.com/wechat/draft/add \
  -H 'Authorization: Bearer 和东京服务器 PROXY_API_KEY 一致' \
  -H 'Content-Type: application/json' \
  -d '{
    "account":"hao1",
    "article":{
      "title":"代理测试草稿",
      "author":"超级发",
      "digest":"测试摘要",
      "content_html":"<p>这是一篇代理测试草稿。</p>",
      "thumb_media_id":"请替换成真实封面素材media_id",
      "need_open_comment":1,
      "only_fans_can_comment":0
    }
  }'
```

如果成功，会返回：

```json
{"media_id":"..."}
```

然后 NAS 上运行正式命令：

```bash
cd /home/superfa/superfa-ai-agent
python -m app.main generate-daily --date 2026-05-09 --create-draft --wechat-account hao1 --no-fallback
```

---

## 10. 第一阶段必须注意的坑

### 10.1 thumb_media_id

微信创建草稿通常要求封面 `thumb_media_id`。当前 NAS 侧文章里可能没有封面素材 ID。

解决方案二选一：

1. 先在微信公众号后台/接口上传一个默认封面，拿到 `thumb_media_id`，让 NAS 文章携带它。
2. 东京代理服务增加默认封面配置，例如：

```env
DEFAULT_THUMB_MEDIA_ID=xxx
```

然后 `article.thumb_media_id` 为空时自动填默认值。

建议第一阶段采用方案 2，减少 NAS 侧改动。

### 10.2 不要把微信密钥放 NAS

混合架构下：

- NAS 保存 `WECHAT_PROXY_URL` 和 `WECHAT_PROXY_API_KEY`
- 东京服务器保存 `WECHAT_ACCOUNTS`
- 微信后台白名单只填东京服务器 IP

### 10.3 发布接口默认不用

第一阶段只创建草稿。发布接口可以开发好，但不要在 NAS 上设置：

```env
AUTO_PUBLISH=true
```

除非你明确要直接发布。

### 10.4 日志不要打印 appsecret 和 access_token

日志可以打印：

- account 名称
- 微信错误码
- 请求路径

不要打印：

- appsecret
- access_token
- 完整 Authorization header

---

## 11. 建议开发顺序

1. 在东京服务器创建 `/opt/wechat-proxy`。
2. 写 `requirements.txt` 和 `app.py`。
3. 配 `.env`，先只配一个公众号账号。
4. 本地启动 uvicorn，测试 `/healthz`。
5. 配 systemd，让服务常驻。
6. 配 Nginx + HTTPS。
7. 在微信后台添加东京公网 IP 白名单。
8. 用 curl 从 NAS 测试 `/wechat/draft/add`。
9. NAS 上配置 `WECHAT_PROXY_URL`，跑 `generate-daily --create-draft`。
10. 确认微信公众号后台草稿箱出现文章。

---

## 12. NAS 和东京服务器的最终配置对照

### NAS `.env`

```env
WECHAT_PROXY_URL=https://tokyo.example.com
WECHAT_PROXY_API_KEY=和东京一致的共享密钥
WECHAT_PROXY_TIMEOUT=30
AUTO_PUBLISH=false
STRICT_SOURCE=true
```

### 东京服务器 `.env`

```env
PROXY_API_KEY=和NAS一致的共享密钥
WECHAT_ACCOUNTS=hao1:appid1:secret1,hao2:appid2:secret2
TOKEN_DIR=/opt/wechat-proxy/tokens
# 可选
DEFAULT_THUMB_MEDIA_ID=xxx
```

---

## 13. 验收标准

完成后应满足：

- `curl https://tokyo.example.com/healthz` 返回 `status: ok`
- 无 Authorization 请求 `/wechat/draft/add` 返回 401
- 带正确 Authorization 的 `/wechat/draft/add` 能返回微信 `media_id`
- NAS 运行：

```bash
python -m app.main generate-daily --date YYYY-MM-DD --create-draft --wechat-account hao1 --no-fallback
```

返回：

```json
{
  "status": "success",
  "briefing": {
    "draft_id": "微信真实 media_id"
  },
  "interpretation": {
    "draft_id": "微信真实 media_id"
  }
}
```

- 微信公众号后台草稿箱能看到生成的文章
- NAS 本地仍有 SQLite 记录和 `outputs/articles/*.md/*.html/*.json`
