# 超级发AI情报公众号更新 Agent

基于 PRD `/home/superfa/.hermes/superfa_ai_agent_prd.md` 实现的 Python MVP。

## 能力

- 调用 AIHot Skill 获取 AI 新闻（失败时 MVP 使用本地 fallback，方便端到端验收）
- 新闻标准化、去重；「AI简报」默认按信号源原始顺序展示 10 条，少加工、不做过度解读
- 生成「AI简报」和「AI解读」Markdown：简报负责信息列表，解读负责单条深度拆解
- 转换为微信公众号友好的 inline-style HTML
- 保存 SQLite：`articles`、`sources`、`settings`
- 创建微信公众号草稿：有 `WECHAT_PROXY_URL` 时通过固定 IP 代理调用接口；否则有微信凭据时本机调用接口；无凭据时返回 `local_draft_*` 便于本地验收
- 可选显式发布/群发：必须同时设置 `AUTO_PUBLISH=true` 并传 `--publish-confirm`
- 默认不自动发布

## Web 化规划

当前项目已经具备内容生产引擎能力，适合进一步封装成 Web 管理后台。建议先采用 **FastAPI + Jinja2/HTMX** 做内部后台，再视需要升级到 FastAPI + Next.js。

详见：[`docs/web-roadmap.md`](docs/web-roadmap.md)。

## 快速开始

```bash
cd /home/superfa/superfa-ai-agent
cp .env.example .env
python -m app.main generate-daily --date 2026-05-09 --create-draft
```

## 常用命令

```bash
python -m app.main generate-briefing --date 2026-05-09 --items 10
python -m app.main generate-briefing --date 2026-05-09 --items 0  # 展示本次获取到的全部条目
python -m app.main generate-briefing --date 2026-05-09 --create-draft
python -m app.main generate-briefing --date 2026-05-09 --create-draft --wechat-account hao1
python -m app.main generate-interpretation --date 2026-05-09 --create-draft --wechat-account hao2
python -m app.main generate-daily --date 2026-05-09 --create-draft --items 10 --wechat-account hao1
AUTO_PUBLISH=true python -m app.main generate-briefing --date 2026-05-09 --wechat-account hao1 --publish-confirm
python -m app.main preview --article-id 1 --format markdown
python -m app.main preview --article-id 1 --format html
python -m app.main preview --article-id 1 --format metadata
```

## 数据来源和严格模式

默认模式下，系统会先请求 AIHot 匿名公开 REST API：`AIHOT_SKILL_URL` 默认为 `https://aihot.virxact.com`，实际读取 `/api/public/items`，默认拿精选条目，并按 OpenAPI 3.1 返回字段解析。AIHot API 必须带浏览器 `User-Agent`，项目已内置默认 UA，也可通过 `AIHOT_USER_AGENT` 覆盖。

简报默认展示 10 条原始信号源，尽量保留标题、来源、时间、分类、标签、摘要和原文链接，不再替你改写成“发生了什么/为什么值得看”。如果想展示本次获取到的全部条目，用 `--items 0`；如果想调整采集上限，用 `AIHOT_SKILL_MAX_ITEMS`。

如果请求失败或返回空结果，MVP 会回退到本地 fallback 示例数据，保证端到端验收可运行。

生成结果会在文章对象和 `outputs/articles/*.json` metadata 里写入：

- `source_mode`: `aihot_skill` 或 `fallback`
- `source_error`: 数据源失败原因；真实 AIHot 成功时为空
- `news_items` / `source_news` 内的每条新闻也会带来源字段

生产或正式审核时建议开启严格模式，避免误用 fallback 示例数据：

```bash
python -m app.main generate-daily --date 2026-05-09 --create-draft --no-fallback
```

也可以通过环境变量启用：

```env
STRICT_SOURCE=true
```

严格模式下，如果 AIHot 获取失败，命令会返回 `status: failed` 并以非 0 退出，不会生成文章或草稿。

## 微信固定 IP 代理模式

如果 NAS 出口 IP 不固定，但微信公众号后台要求配置 IP 白名单，推荐使用混合架构：NAS 本地采集、生成、保存 SQLite、写 `outputs/articles/*`，东京固定 IP 服务器只做微信 API 出口代理。

NAS 侧 `.env` 只需要配置代理地址和共享密钥，不需要把微信 `appsecret` 放在 NAS 上：

```env
WECHAT_PROXY_URL=https://tokyo.example.com
WECHAT_PROXY_API_KEY=replace-with-long-random-token
WECHAT_PROXY_TIMEOUT=30
```

启用 `WECHAT_PROXY_URL` 后，`--create-draft` 会向代理发送：

```text
POST /wechat/draft/add
Authorization: Bearer <WECHAT_PROXY_API_KEY>
{"account":"hao1","article":{...}}
```

如果显式开启发布，仍然必须同时满足 `AUTO_PUBLISH=true` 和 `--publish-confirm`，然后代理调用：

```text
POST /wechat/freepublish/submit
Authorization: Bearer <WECHAT_PROXY_API_KEY>
{"account":"hao1","media_id":"<draft_media_id>","draft_id":"<draft_media_id>"}
```

代理返回需包含 `media_id`/`draft_id` 或 `publish_id`。东京服务器保存真实公众号凭据，并在微信后台白名单中登记东京服务器公网 IP。

## 多公众号草稿与发布

默认仍兼容单公众号配置：`WECHAT_APPID` + `WECHAT_APPSECRET`。如果要控制多个公众号，用 `WECHAT_ACCOUNTS` 配账号别名，再在生成命令里用 `--wechat-account` 指定：

```env
# 不要提交真实值
WECHAT_ACCOUNTS=hao1:appid1:secret1,hao2:appid2:secret2
```

```bash
# 简报发到号1草稿箱
python -m app.main generate-briefing --date 2026-05-09 --create-draft --wechat-account hao1

# 解读发到号2草稿箱
python -m app.main generate-interpretation --date 2026-05-09 --create-draft --wechat-account hao2
```

当前默认集成的是微信公众号「创建草稿」能力，不会自动群发/发布。没有配置真实凭据时仍返回 `local_draft_*`，用于本地端到端验收。配置多账号后，每个账号会使用独立 token cache，例如 `data/token_store_hao1.json`。

如果确实要直接发布/群发，必须同时满足两个条件：

1. 环境变量 `AUTO_PUBLISH=true`
2. 命令显式传入 `--publish-confirm`

示例：

```bash
AUTO_PUBLISH=true python -m app.main generate-briefing --date 2026-05-09 --wechat-account hao1 --publish-confirm
```

`--publish-confirm` 会自动先创建草稿，再调用微信公众号 `freepublish/submit`。请只在确认内容无误、公众号凭据指向正确账号时使用。

## 环境变量

见 `.env.example`。真实密钥只放 `.env` 或 shell 环境变量，不要提交。

## 测试

```bash
pytest tests/ -q
```

## 注意

MVP 为了能在没有微信公众号凭据时完成验收，会生成本地草稿 ID：`local_draft_*`。配置 `WECHAT_APPID` 和 `WECHAT_APPSECRET` 后，会获取真实 access_token 并尝试创建微信公众号草稿。
