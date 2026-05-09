# CLAUDE.md

## Project Overview

Henry Hu's Blog — a personal blog system with AI-powered writing assistance and video embedding.

## Tech Stack

- **Backend**: Python 3 / FastAPI / SQLite / JWT auth
- **Frontend**: Vue 3 / Vite / Axios
- **AI**: Multi-provider support (OpenAI, Anthropic, DashScope, MiniMax)

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
