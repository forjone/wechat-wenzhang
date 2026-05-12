# 超级发AI情报 Web 化梳理

当前项目已经具备“内容生产引擎”的核心能力，适合在此基础上封装成一个 Web 网站/后台。更准确地说：现在是 Python CLI + SQLite + 微信草稿自动化；下一步可以做成“AI 情报内容中台”。

## 1. 现有能力盘点

### 已实现

- AI 新闻采集：通过 AIHot 公共接口获取 AI 新闻，支持严格模式与 fallback。
- 内容生成：生成 AI 简报、AI 解读两类文章。
- 内容编排：简报偏新闻列表，解读偏普通人视角、机会拆解。
- HTML 渲染：将 Markdown 转成公众号 inline-style HTML。
- 图片元数据：生成封面/内嵌图占位资源与 prompt。
- 数据持久化：SQLite 保存 articles、sources、settings。
- 输出归档：每次生成会保存 Markdown、HTML、JSON metadata。
- 微信草稿：支持本机微信 API 或东京固定 IP proxy 创建公众号草稿。
- 多公众号：支持账号别名，例如 cjfai、mflai。
- 发布保护：默认只创建草稿，直接发布必须 `AUTO_PUBLISH=true` + `--publish-confirm` 双重确认。
- 自动任务：已有脚本化 daily 运行基础。
- 测试：已有内容管线、微信代理、预览、严格模式等测试。

## 2. 是否能形成 Web 网站？

结论：可以，而且比较顺。

原因是当前业务逻辑已经集中在 `app/main.py` 与各模块函数里，CLI 只是入口。Web 层可以复用这些函数，而不是重写内容生产逻辑。

推荐形态不是一开始做公开门户，而是先做一个内部管理后台：

```text
Web 管理后台
├── 今日 AI 信号源
├── 一键生成 AI 简报
├── 一键生成 AI 解读
├── 文章列表 / 搜索 / 预览
├── Markdown / HTML 预览
├── 创建公众号草稿
├── 草稿状态 / issue 编号
├── 配置页：AIHot、公众号账号、严格模式、主题
└── 日志页：每日任务运行结果
```

## 3. 推荐 Web 架构

### 方案 A：FastAPI + Jinja/HTMX（推荐 MVP）

适合快速上线内部后台，依赖少、部署简单。

```text
现有 app/ 业务模块
        ↑
FastAPI service 层
        ↑
Jinja2 + HTMX 页面
```

优点：

- 与当前 Python 项目最贴合。
- 不需要单独维护前端工程。
- 很快能做出可用后台。
- 适合 NAS / VPS 部署。

### 方案 B：FastAPI + Next.js

适合后续做更完整的 SaaS/内容平台。

优点：

- UI 体验更好。
- 前后端分离，适合多人协作。
- 后续可以做用户系统、多账号、多工作区。

缺点：

- 初期复杂度明显更高。
- 需要 Node.js、构建、部署链路。

### 我的建议

第一版用 **FastAPI + Jinja2/HTMX**，先把核心后台跑起来；等流程稳定后再考虑 Next.js。

## 4. Web 版页面规划

### P0：最小可用后台

1. 首页 Dashboard
   - 今日是否已生成
   - 最新简报、最新解读
   - 最近草稿状态
   - 数据源状态

2. 新闻源页面 `/sources`
   - 查看指定日期 AIHot 新闻
   - 展示标题、来源、摘要、分数、原文链接
   - 手动选择要进入简报/解读的条目

3. 生成页面 `/generate`
   - 选择日期
   - 选择栏目：简报 / 解读 / 每日组合
   - 选择公众号账号
   - 是否创建草稿
   - 是否严格模式
   - 生成结果 JSON/摘要展示

4. 文章列表 `/articles`
   - 按类型、日期、状态筛选
   - 查看 issue_no、标题、状态、草稿是否存在

5. 文章详情 `/articles/{id}`
   - Markdown 预览
   - HTML 预览
   - metadata 查看
   - 创建/重试公众号草稿

### P1：好用增强

- 编辑 Markdown 后重新渲染 HTML。
- 多主题排版预览。
- 重新发送草稿，不重复生成内容。
- 日志查看。
- 定时任务配置。
- “今日工作流”一键跑完。

### P2：平台化

- 登录权限。
- 多品牌/多公众号 workspace。
- 内容日历。
- 数据源配置管理。
- 图像生成服务接入。
- 发布后数据回收与复盘。

## 5. 需要补的工程能力

当前如果要变 Web，需要补：

1. Web server 入口
   - `app/web/main.py`
   - FastAPI app
   - 路由与模板

2. Service 层
   - 把 CLI command 函数进一步拆成可被 Web 安全调用的 service。
   - 避免 Web 请求长时间阻塞，生成任务最好后台执行。

3. 任务状态
   - 简单版：同步执行，页面显示结果。
   - 稳定版：SQLite 增加 `jobs` 表，记录 running/success/failed。

4. 安全
   - 内部后台至少加 Basic Auth 或反向代理鉴权。
   - 不在页面显示 `WECHAT_PROXY_API_KEY`、appsecret 等敏感值。
   - 发布按钮继续保持双重确认。

5. 数据库迁移
   - 当前 SQLite schema 由 `CREATE TABLE IF NOT EXISTS` 管理。
   - Web 化后建议引入轻量迁移机制，或至少加 schema version。

6. 部署
   - `uvicorn app.web.main:app --host 0.0.0.0 --port 8000`
   - systemd 或 Docker。
   - Nginx 反代 + HTTPS。

## 6. 建议里程碑

### Milestone 1：Web MVP，1-2 天

- FastAPI 后台跑起来。
- Dashboard、文章列表、文章详情。
- 支持从网页触发 `generate-daily`。
- 支持预览 Markdown/HTML。

### Milestone 2：草稿工作台，1-2 天

- 对已有文章创建/重试微信草稿。
- 展示草稿账号与状态。
- 防重复生成 issue_no。
- 加日志页。

### Milestone 3：选题工作台，2-3 天

- 新闻源列表。
- 手动选择简报条目和解读条目。
- 支持重新排序。
- 支持编辑标题/digest 后创建草稿。

### Milestone 4：生产部署，1 天

- 鉴权。
- systemd/Docker。
- 反向代理。
- 定时任务可视化。
- 备份 SQLite 与 outputs。

## 7. 当前仓库发布注意事项

应该提交到 GitHub 的内容：

- `app/`
- `tests/`
- `scripts/`
- `docs/`
- `README.md`
- `.env.example`
- `.gitignore`
- `pytest.ini`

不应该提交：

- `.env`
- `data/*.db`
- `data/token_store*.json`
- `outputs/articles/*`
- `outputs/images/*`
- `outputs/covers/*`
- `logs/*`
- `__pycache__/`
- `.pytest_cache/`

当前 `.gitignore` 已经忽略了大部分，但建议补上 `outputs/images/*` 和 `data/token_store_*.json`。

## 8. 推荐下一步

先把当前 CLI 项目作为稳定的 GitHub v0.1 提交；然后新建一个分支或下一次迭代做 Web MVP。这样可以保证当前已能跑通的公众号自动化能力先被版本化保存。