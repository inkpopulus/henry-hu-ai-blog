# CLAUDE.md

## Project Overview

Henry Hu's Blog — a personal blog system with AI-powered writing assistance and video embedding.

## Tech Stack

- **Backend**: Python 3 / FastAPI / SQLite / JWT auth
- **Frontend**: Vue 3 / Vite / Axios
- **AI**: Multi-provider support (OpenAI, Anthropic, DashScope, MiniMax)

## Workflow Rules

### Multi-Session Collaboration

This project uses a dual-session Claude workflow.

Two independent Claude sessions work together:

### Session A — Planner

Responsibilities:

- architecture design
- task decomposition
- API design
- database structure decisions
- identifying blockers
- maintaining PLAN.md

Rules:

- do not directly write implementation code
- focus on long-term maintainability
- prioritize system stability
- output decisions into PLAN.md

---

### Session B — Executor

Responsibilities:

- code implementation
- debugging
- bug fixing
- feature completion based on PLAN.md

Rules:

- do not redesign architecture without strong reason
- follow PLAN.md strictly
- prefer minimal code changes
- do not modify unrelated modules
- stability first, optimization second

---

### Collaboration Rules

Communication must happen through files, not memory.

Use:

- PLAN.md → current execution plan
- TODO.md → task breakdown (optional)
- REVIEW.md → review notes (optional)
- BUG.md → debugging notes (optional)

PLAN.md is maintained only by Planner. Executor never modifies PLAN.md directly. Executor reports facts. Planner updates decisions.

Never assume another session remembers context.

Always read project files first before making decisions.

---

### Context Management

When context usage exceeds 65%:

/compact

When context becomes unreliable:

/new

Avoid long single-session conversations.

Prefer multiple focused sessions over one overloaded session.

---

### Coding Philosophy

- minimal changes first
- no unnecessary refactor
- do not modify unrelated modules
- explain before modifying
- test after changes
- preserve existing architecture unless necessary
- backend API consistency is priority
- frontend polish comes after stability

### Security Rules

- 不要在源码中硬编码密码、密钥等敏感信息，从环境变量或配置文件读取
- AI provider API 密钥由用户在 `ai_config.json` 中自行配置（已 gitignore）
- 应用凭据（admin 密码、JWT 密钥等）从环境变量读取
- 事故记录：2026-05-10，admin123 和 JWT secret 硬编码在源码中并提交到公开 repo

## Running

```bash
# Backend (port 8000)
cd backend && python3 main.py

# Frontend (port 5173, proxies /api to backend)
cd frontend && npm run dev
```

## Project Structure

```
backend/
  main.py              # FastAPI app, blog CRUD, auth, AI feature endpoints
  database.py          # SQLite layer (posts, users)
  ai_config.json       # AI providers and feature config
  ai_function/         # Skill platform (future extensibility)
    config.py          # Config loader (providers, features, skills)
    providers.py       # AI provider abstractions (OpenAI, Anthropic, DashScope)
    router.py          # Skill endpoints: POST /api/ai/skills/{skill_name}
    skills.py          # Skill definitions (continue_writing, polish, generate_article)

frontend/src/
  api/index.js         # API client (axios + SSE streaming)
  views/
    NewPost.vue        # Editor with toolbar (formatting, images, video, AI)
    PostDetail.vue     # Post viewer with custom Markdown renderer
    Home.vue           # Post listing
    Login.vue          # Login form
  utils/
    videoEmbed.js      # Video platform registry (Bilibili, YouTube)
```

## Key Architecture

### AI Features vs Skills

**Built-in features** (fixed, hardcoded in main.py):
- `/api/ai/continue` — continue writing
- `/api/ai/polish` — polish/rewrite selected text
- `/api/ai/generate` — generate full article
- Configured under `features` in `ai_config.json`

**Skill platform** (extensible, in `ai_function/`):
- `/api/ai/skills/{skill_name}` — pluggable AI skills
- Configured under `skills` in `ai_config.json`
- Reserved for future user-extensible functionality

### Video Embedding

Syntax: `{% platform video_id %}` or paste full URL (auto-detected).

Supported platforms in `frontend/src/utils/videoEmbed.js`:
- Bilibili — `{% bilibili BV1xx411c7mD %}`
- YouTube — `{% youtube dQw4w9WgXcQ %}`

To add a new platform: add entry to `PLATFORMS` object in `videoEmbed.js`.

### Markdown Rendering

Custom renderer in `PostDetail.vue` (not a library). Handles:
- Headings (h1-h4), bold, italic, strikethrough, inline code
- Code blocks, blockquotes, horizontal rules, images, links
- Video embeds via `parseVideoEmbeds()`

### Editor Toolbar

`NewPost.vue` toolbar groups:
1. Text formatting (bold, italic, strikethrough)
2. Headings (H1-H3)
3. Insert (link, code, code block, quote)
4. Media (upload image, network image, video embed)
5. AI (continue, polish, generate, stop)

## Config

`backend/ai_config.json`:
- `providers` — AI provider credentials and defaults
- `features` — built-in AI feature → provider mapping
- `skills` — skill platform → provider mapping
