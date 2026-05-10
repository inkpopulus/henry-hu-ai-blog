# Plan — 项目全景审查

## 已完成

### 核心功能（全部可运行）
- **博客 CRUD** — 创建、读取、编辑、删除文章，完整可用
- **认证系统** — JWT 登录、修改密码、可选/强制鉴权两层机制
- **标签与搜索** — 文章按标签过滤、关键词搜索
- **图片上传** — UUID 重命名、扩展名白名单校验
- **编辑器工具栏** — 粗体/斜体/删除线/H1-H3/链接/代码/引用/图片上传/网络图片/视频嵌入，全部已实现
- **AI 三件套** — 续写、润色、生成文章，SSE 流式响应，按钮式交互
- **视频嵌入** — `{% bilibili/youtube %}` 语法，自动从 URL 提取 ID，iframe 渲染
- **Markdown 渲染** — 使用 markdown-it，支持标题/粗体/斜体/删除线/行内代码/代码块/引用/分割线/图片/链接/视频嵌入/列表/表格/任务列表
- **AI 技能平台** — `ai_function/` 目录下完整的 Provider 抽象（OpenAI/Anthropic/DashScope）、Skill 注册机制、流式路由

### 基础设施
- FastAPI + Vue 3 + Vite 全栈搭建完成
- Vite 代理配置正确（/api、/uploads → :8000）
- SQLite 数据库自动初始化 + 种子数据
- start.sh 一键启动脚本

### 2026-05-10 完成
- **P0-1 最小测试/验证清单** — 登录、文章 CRUD、AI 三件套、Markdown 渲染（代码块/图片/视频）全部验证通过，基线已确认
- **P0-2 消除硬编码凭据** — admin 密码和 JWT 密钥改为环境变量读取，源码中不再有真实凭据
- **P0-3 替换 Markdown 渲染器** — 引入 markdown-it，替换手写解析器，支持列表/表格/任务列表等完整语法
- **P0-4 统一 AI 架构** — 清理死代码，统一鉴权逻辑，ChangePassword 走 API 模块
- **P0-5 修复弹窗 bug** — 四个弹窗 @click.self 改 @mousedown.self，解决选文本自动关闭

### 2026-05-11 完成
- **P1-1 路由守卫 + 404** — 未登录用户自动跳转登录页，不存在的路径显示 404
- **P1-2 AI 对话助手** — `/api/ai/chat` 端点 + Lab A/B/C 三个原型已完成
- **P2-1 密码哈希升级** — 从 SHA-256 升级到 bcrypt
- **P2-2 依赖版本锁定** — requirements.txt 精确版本 + package-lock.json
- **P2-3 Git 清理** — .DS_Store 从 git 移除，.claude/ 加入 gitignore

---

## 稳定可用的功能

- 文章的增删改查 + 标签 + 搜索
- 登录 / 鉴权 / 修改密码
- 图片上传
- 编辑器全部工具栏按钮
- AI 续写 / 润色 / 生成（架构已统一）
- AI 对话助手（/api/ai/chat，三个原型已完成）
- 路由守卫 + 404
- 视频嵌入（Bilibili、YouTube）
- Markdown 渲染（markdown-it，完整语法）

---

## 半成品 / 有问题的部分

### 后端
| 问题 | 位置 | 说明 |
|------|------|------|
| DashScope 声明但未使用 | `ai_config.json` + `providers.py` | 定义了 provider 但没有任何 feature 引用它 |
| 无注册端点 | — | 只有种子 admin 用户，无法通过 API 创建新用户 |

### 前端
| 问题 | 位置 | 说明 |
|------|------|------|
| `.login-error` 样式不一致 | `Login.vue:92` vs `style.css:425` | scoped 版 `margin-bottom: 99px` vs 全局版 `16px` |

### 配置 / 工程
| 问题 | 位置 | 说明 |
|------|------|------|
| 无自动化测试 | 整个项目 | P0-1 已手动验证基线，但无测试框架和自动化测试 |
| start.sh 每次重装依赖 | `start.sh` | 每次运行都 `pip install` + `npm install`，慢且不必要 |

---

## 真正的 Blockers

（无）

---

## 不紧急但应记录的历史设计问题

- 无用户注册机制（单 admin 博客可能有意为之，但限制了扩展）

---

## 下一阶段优先级

### ~~P0-1 — 最小测试/验证清单~~ ✅ 已完成

- [x] 登录、文章 CRUD、AI continue/polish/generate、Markdown 代码块/图片/视频 — 全部验证通过

### ~~P0-2 — 消除硬编码凭据~~ ✅ 已完成

- [x] admin 密码和 JWT 密钥改为环境变量读取

### ~~P0-3 — 替换 Markdown 渲染器~~ ✅ 已完成

引入 markdown-it，替换手写解析器，支持列表/表格/任务列表等完整语法。

### ~~P0-4 — 统一 AI 架构~~ ✅ 已完成

清理死代码，统一鉴权逻辑，ChangePassword 走 API 模块。

### ~~P0-5 — 修复弹窗选文本自动关闭 bug~~ ✅ 已完成

四个弹窗 @click.self 改 @mousedown.self。

### ~~P1 — 补工程短板 + 新功能~~ ✅ 已完成

- [x] 路由守卫 + 404
- [x] AI 对话助手 — `/api/ai/chat` 端点 + 三个原型（Lab A/B/C）

### ~~P2 — 加固~~ ✅ 已完成

- [x] 密码哈希升级（bcrypt）
- [x] 依赖版本锁定
- [x] `.DS_Store` 从 git 移除、`.claude/` 加入 gitignore
