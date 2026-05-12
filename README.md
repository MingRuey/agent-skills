# Ray's Customized Agent

This repo contains Ray's setting with a customized agent service with Anthorpoic API + LibreChat, which includes:
- the setup for LibreChat agent service
- skills/subagent Ray frequently used

## LibreChat Service Setup

Following the official guide of [docker setup](https://www.librechat.ai/docs/local/docker)
- Remember to add proper Anthropic API key in the `.env` file
- After the setup, you can run the service with `docker compose up -d` and it will be available at designated port
- To bind the port to localhost only (Docker otherwise publishes on `0.0.0.0` and bypasses UFW), `docker-compose.override.yml` replaces `api.ports` with `"127.0.0.1:${PORT}:${PORT}"` using the `!override` tag (without it, Compose appends to the base list and the duplicate bind causes "address already in use")

- `docker compose down -v` && `sudo rm -rf ./data-node ./meili_data_v1.12 ./logs ./uploads ./images` will stop the service and remove the data volume, which is useful for resetting the service completely
- otherwise `docker compose up -d --force-recreate` might be enough for refreshing the service with updated .env file, for example.

## Web Search MCP via Brave Search API 

Brave Search wired in via MCP:
- `librechat.yaml` (copied from `librechat.example.yaml`) bind-mounted into the API container via `docker-compose.override.yml` — also the file-native source-of-truth for future MCP servers and `modelSpecs`
- `mcpServers.brave-search` in `librechat.yaml` launches `@brave/brave-search-mcp-server` via `npx`; reads `BRAVE_API_KEY` from `.env`
- 6 tools registered on load: `brave_web_search`, `brave_local_search`, `brave_video_search`, `brave_image_search`, `brave_news_search`, `brave_summarizer` — selectable per-agent in Agent Builder under Tools
- Verify load: `docker compose logs api | grep -iE "mcp|brave"` should report `Initialized with 1 configured server and 6 tools`
- API key: free tier at `api-dashboard.search.brave.com` (2000 req/month, 1 req/sec)

## Subagents/Skills

Agents and skills are defined as markdown-with-frontmatter files under `agents/<name>/` and synced into LibreChat's MongoDB by two one-shot containers in `docker-compose.override.yml`. The repo is the source of truth; the DB is derived state. `agents/translator-tutor/` is the live example — one agent with three attached skills.

### Layout

```
agents/
  <agent-name>/
    AGENT.md                    # frontmatter (name, provider, model, skills, ...) + system prompt body
    skills/
      <skill-name>/
        SKILL.md                # frontmatter (name, description, ...) + skill body
bin/
  bootstrap-user.py             # seeds the syncer's LibreChat account
  sync.py                       # upserts skills, then the agent, via the REST API
```

### Why two containers

LibreChat's `/api/skills` and `/api/agents` endpoints require JWT auth, and `ALLOW_REGISTRATION=false` blocks self-registration. So we need a real LibreChat account before the syncer can log in.

- **`bootstrap-user`** (`python:3.12-slim`, ~50 MB) — uses `bcrypt` + `pymongo` to insert a `users` document directly into MongoDB, matching `AuthService.registerUser` (bcrypt rounds=10, `provider='local'`, `role='USER'`, `emailVerified=true`). Idempotent — skips if the email/username already exists. We bypass `npm run create-user` to avoid pulling the ~1 GB LibreChat image just to run one script.

- **`syncer`** (same image) — depends on `bootstrap-user` completing and `api` started. Logs in via `/api/auth/login` with `LIBRECHAT_EMAIL`+`LIBRECHAT_PASSWORD` to fetch a fresh JWT (so token expiry is irrelevant), lists existing records, then POSTs new skills/agents or PATCHes existing ones by name. Skill ObjectIds returned at creation are resolved into the agent's `skills:` list before the agent upsert. Re-running is safe and idempotent.

### Required `.env` entries

```
LIBRECHAT_EMAIL=<your-email>
LIBRECHAT_PASSWORD=<your-password>     # 8+ chars, also seeds bootstrap-user
```

### Usage

First bring-up:
```
cd LibreChat
docker compose up -d
```
Bootstrap inserts the user, syncer creates skills and agent, both exit. The agent is then selectable in the UI (`@<agent-name>` in the chat input).

Iteration after editing any `AGENT.md` or `SKILL.md`:
```
docker compose up syncer
```
Bootstrap is a no-op; syncer PATCHes the changed records in place. No restart of `api` or `mongodb` needed.
