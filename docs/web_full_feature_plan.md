# Superfa Web 全功能实现计划

## 目标
把当前 Web MVP 升级为公众号内容生产工作台，覆盖：今日工作台、新闻去重、生成前编辑、草稿面板、补发/重生成、健康检查、多角度、主题预览、封面工作流。

## 落地策略
- 不破坏现有 CLI daily 流程。
- Web 默认继续使用 `data/web/superfa-web.db`，避免误动生产 `data/superfa.db`。
- 涉及真实微信草稿的动作保留显式按钮，默认只预览/保存。
- 不新增重型前端依赖，继续使用 FastAPI + Jinja2 + 原生表单。

## 数据模型
首版尽量复用既有表：
- `sources.selected`：保留选择状态。
- `articles.status`：支持 `generated`、`draft_created`、`published`、`voided`、`needs_review`。
- `articles.source_url/source_title`：用于新闻已用/重复标记。
- `articles.cover_prompt/cover_path/content_html`：用于封面与主题预览。

暂不新增表，降低迁移风险；后续如需要操作审计再加 `article_events`。

## API/UI
- `GET /today`：今日工作台，显示候选新闻、下一个编号、草稿生成表单。
- `POST /today/generate`：根据勾选 source 生成简报/解读/mflai 草稿。
- `GET /news`：增加已用标记、重复提示、用途状态。
- `POST /articles/{id}/edit`：保存标题、摘要、Markdown 并重渲染 HTML。
- `GET /drafts`：草稿状态面板。
- `POST /articles/{id}/status`：标记已发布/作废/待审。
- `POST /articles/{id}/create-draft`：对已有文章补发草稿，不新占编号。
- `GET /health`：服务器时间、北京时间、cron、最近文章、下次编号。
- `GET /articles/{id}`：增加多角度建议、主题预览、封面 prompt 编辑。
- `POST /articles/{id}/cover`：保存封面 prompt。
- `POST /articles/{id}/theme-preview`：按主题重渲染 HTML。

## 验证
- 扩展 `tests/test_web_mvp.py` 覆盖所有核心 Web 路由。
- 定向测试：`python3 -m pytest tests/test_web_mvp.py -q`。
- 全量测试：`python3 -m pytest tests/ -q`。
- 重启 uvicorn 后 HTTP 验证 `/`、`/today`、`/news`、`/articles`、`/drafts`、`/health`。
