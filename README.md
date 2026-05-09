# Henry Hu's Blog

一个基于 FastAPI + Vue 3 的个人博客系统。

## 技术栈

- **后端**: Python 3.11+, FastAPI, SQLite, JWT 认证
- **前端**: Vue 3, Vue Router, Vite, Axios

## 功能

- 文章的创建、编辑、删除
- Markdown 编辑器（加粗、斜体、标题、引用、代码块、链接）
- 本地图片上传 + 网络图片插入
- 视频嵌入（Bilibili、YouTube，支持粘贴链接自动识别）
- AI 写作助手（续写、润色、生成文章，流式输出）
- 标签下拉筛选（支持搜索）
- 全文关键词搜索
- JWT 登录认证
- 修改密码
- 数据持久化（SQLite）

## 环境要求

- Python 3.11+
- Node.js 18+
- npm

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd test_vibe_coding
```

### 2. 后端

```bash
cd backend

# 创建虚拟环境（如果还没有）
python3 -m venv ../.venv
source ../.venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

后端运行在 `http://localhost:8000`。

### 3. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`。

### 4. 一键启动（macOS/Linux）

```bash
chmod +x start.sh
./start.sh
```

## 默认账号

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |

首次登录后请立即修改密码（导航栏 → 改密码）。

## 生产构建

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/`，可部署到 Nginx 或其他静态服务器。Nginx 需要将 `/api` 和 `/uploads` 反向代理到后端 8000 端口。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
    }

    location /uploads {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 项目结构

```
├── backend/
│   ├── main.py              # FastAPI 应用入口、博客 CRUD、AI 功能端点
│   ├── database.py          # SQLite 数据库操作
│   ├── requirements.txt     # Python 依赖
│   ├── ai_config.json       # AI 提供商和功能配置（不入库，含 API Key）
│   ├── ai_function/         # AI Skill 平台（可扩展）
│   │   ├── config.py        # 配置加载器
│   │   ├── providers.py     # AI 提供商抽象（OpenAI、Anthropic、DashScope）
│   │   ├── router.py        # Skill 端点
│   │   └── skills.py        # Skill 定义
│   ├── uploads/             # 上传的图片
│   └── blog.db              # SQLite 数据库文件（自动生成）
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── api/index.js          # API 请求封装 + AI 流式调用
│       ├── router/index.js       # 路由配置
│       ├── stores/auth.js        # 认证状态管理
│       ├── utils/
│       │   └── videoEmbed.js     # 视频嵌入平台注册表
│       └── views/
│           ├── Home.vue          # 首页
│           ├── PostDetail.vue    # 文章详情 + Markdown 渲染
│           ├── NewPost.vue       # 新建/编辑文章 + AI 编辑器
│           ├── Login.vue         # 登录
│           └── ChangePassword.vue # 修改密码
└── start.sh                 # 一键启动脚本
```

## AI 配置

编辑 `backend/ai_config.json` 配置 AI 提供商和功能：

```json
{
  "providers": {
    "my_provider": {
      "name": "openai",
      "api_key": "sk-your-key",
      "base_url": "https://api.example.com/v1",
      "default_model": "model-name"
    }
  },
  "features": {
    "continue": { "provider": "my_provider", "temperature": 0.8 },
    "polish": { "provider": "my_provider", "temperature": 0.3 },
    "generate": { "provider": "my_provider", "temperature": 0.7 }
  }
}
```

支持的提供商类型：`openai`、`anthropic`、`dashscope`。

## 视频嵌入

在文章中使用以下语法嵌入视频：

```markdown
{% bilibili BV1xx411c7mD %}
{% youtube dQw4w9WgXcQ %}
```

也支持粘贴完整链接自动提取视频 ID。

## API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/login` | 登录获取 token | 否 |
| GET | `/api/me` | 获取当前用户状态 | 可选 |
| PUT | `/api/password` | 修改密码 | 是 |
| GET | `/api/posts` | 文章列表（支持 `?tag=` `?q=`） | 否 |
| GET | `/api/posts/:id` | 文章详情 | 否 |
| POST | `/api/posts` | 创建文章 | 是 |
| PUT | `/api/posts/:id` | 更新文章 | 是 |
| DELETE | `/api/posts/:id` | 删除文章 | 是 |
| GET | `/api/tags` | 所有标签 | 否 |
| POST | `/api/upload` | 上传图片 | 是 |
| POST | `/api/ai/continue` | AI 续写（SSE 流式） | 是 |
| POST | `/api/ai/polish` | AI 润色（SSE 流式） | 是 |
| POST | `/api/ai/generate` | AI 生成文章（SSE 流式） | 是 |
| GET | `/api/ai/skills` | 列出可用 AI Skills | 否 |
| POST | `/api/ai/skills/:name` | 执行 AI Skill（SSE 流式） | 是 |
