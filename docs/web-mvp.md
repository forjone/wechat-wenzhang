# Web MVP 工作台

这个模块是独立新增的内部 Web 工作台，入口在 `app/web`，不替换、不重构原有 CLI 流程。

## 能力范围

第一版 MVP 提供：

- `/`：Dashboard，查看新闻源、文章、草稿数量和最近记录。
- `/news`：查看已采集新闻源，也可以按日期触发一次采集。
- `/news/{source_id}/generate`：选择单条新闻，选择内容类型、排版主题、公众号账号，生成文章；勾选后可创建公众号草稿。
- `/articles`：查看已生成文章列表。
- `/articles/{article_id}`：查看文章 Markdown 和微信 HTML 预览。

## 不影响旧流程的设计

- Web 代码全部放在 `app/web/`。
- 原命令行入口仍是 `python3 -m app.main ...`。
- 数据库仍复用现有 `data/superfa.db`、`articles`、`sources`、`settings` 表。
- Web 启动时只调用现有 `init_db()` 做兼容初始化，不会删除或重建数据。
- 默认不会自动发布/群发；只有表单勾选“创建公众号草稿”时才调用已有草稿创建逻辑。
- 页面只展示公众号账号别名，不展示 `appid`、`appsecret`、proxy key、token 等密钥。

## 依赖

Web MVP 使用：

- `fastapi`
- `uvicorn`
- `jinja2`
- `python-multipart`

当前运行环境已具备测试所需的 FastAPI/Jinja2 相关包。若新环境缺少依赖，可以在项目虚拟环境里安装：

```bash
python3 -m pip install fastapi 'uvicorn[standard]' jinja2 python-multipart
```

## 启动

```bash
cd /home/superfa/superfa-ai-agent
python3 -m uvicorn app.web.main:app --host 0.0.0.0 --port 8000
```

然后访问：

```text
http://<服务器IP>:8000/
```

如果只想本机访问：

```bash
python3 -m uvicorn app.web.main:app --host 127.0.0.1 --port 8000
```

## 典型使用流程

1. 打开 `/news`。
2. 选择日期并点击“采集这天新闻”，或查看已有新闻源。
3. 点击某条新闻的“生成文章”。
4. 选择：
   - 内容类型：`AI解读` 或 `AI简报`
   - 排版主题：`fresh-card` 或 `bytedance-green`
   - 公众号账号：例如 `cjfai`
   - 是否创建公众号草稿
5. 提交后跳转到文章详情页。
6. 在 `/articles` 查看历史文章。

## 测试

```bash
pytest tests/test_web_mvp.py -q
pytest tests/ -q
```

## 后续增强建议

- 增加登录/访问控制，避免内部后台公网裸露。
- 从 `WECHAT_ACCOUNTS` 自动解析账号别名，下拉选择账号。
- 增加任务日志和错误页。
- 支持更多主题和“只生成不入草稿 / 重新入草稿”。
- 增加文章编辑页。 
