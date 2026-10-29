# Ray's Customized Agent

Ray's personal agent setup: LibreChat (company Anthropic key), Claude Code (Mac + Linux host) and claude.ai (personal Pro), all sharing one memory, one set of rules and one set of skills.

```
agents/AGENT.md     shared rules (memory) → Claude Code CLAUDE.md, every LibreChat agent, claude.ai profile
agents/<name>/      LibreChat agents (currently: ai-kun)
skills/<name>/      shared skills (guided-tutoring, karpathy-guidelines)
bin/sync.py         pushes agents + skills into LibreChat
bin/pack-claude-ai.py  builds the claude.ai download page (per-skill zips + agent .md files)
LibreChat/          upstream LibreChat + our docker-compose.override.yml, librechat.yaml, .env
```

| Where | Memory | Rules | Skills |
|---|---|---|---|
| Claude Code | `claude mcp add` → `127.0.0.1:2068` | `~/.claude-personal/CLAUDE.md` → symlink to `agents/AGENT.md` | symlinks in `~/.claude-personal/skills/` |
| LibreChat | added to every agent by `sync.py` | prepended to every agent by `sync.py` | attached to every agent by `sync.py` |
| claude.ai | custom connector `https://memory.galaxynetwork.dev/mcp` | pasted into profile preferences | uploaded zips |

**claude.ai bundle:** bookmark `http://localhost:2067/claude-ai/index.html` (from the Mac via the SSH tunnel; served by LibreChat, no login): one zip per skill in claude.ai's upload format (a single top-level `<skill>/` folder with `SKILL.md`; claude.ai takes one skill per zip), plus `agents.zip` and one link per agent `.md` (`AGENT.md` = shared rules, `ai-kun.md`, …) for pasting. The syncer rebuilds it on every run (`docker compose up syncer`); locally `bin/pack-claude-ai.py` writes `dist/claude-ai/`.

## Set up a machine (Claude Code)

```sh
make     # same folder Claude Code uses: $CLAUDE_CONFIG_DIR if set (host: ~/.claude-personal), else ~/.claude (Mac)
```

Links `CLAUDE.md` → `agents/AGENT.md` and every skill (so `git pull` updates them), turns off built-in auto-memory, and registers the shared memory server. It needs the **memory API key** (`MCP_MEMORY_API_KEY`, not a Cloudflare key): read from `LibreChat/.env` on the host, asked for elsewhere. The host uses `127.0.0.1:2068`; other machines (e.g. the Mac on the company API key) use `https://memory.galaxynetwork.dev/mcp`, so the host must be up. `make check` tests the key; `make rules|skills|memory` run one step.

## Daily use

```sh
cd LibreChat
docker compose up -d             # everything: LibreChat, memory server, tunnel, syncer
docker compose up syncer         # after editing agents/ or skills/
docker compose logs -f <service> # api, mcp-memory, cloudflared, syncer
```

- After editing `agents/AGENT.md` or a skill, also re-paste / re-upload it in claude.ai from the bundle (it keeps its own copy)
- Never `docker compose down -v` — it deletes the local memory DB and LibreChat data
- After a memory-server upgrade, give it a minute before `127.0.0.1:2068` answers

## LibreChat

Set up per the [official Docker guide](https://www.librechat.ai/docs/local/docker), plus our `docker-compose.override.yml` and `librechat.yaml`.

- Host ports, localhost only: LibreChat `2067` (`PORT`), memory `2068` (`MCP_MEMORY_PORT`). Everything else stays inside Docker. Reach the UI from the Mac over an SSH tunnel
- Web search: Tavily (`webSearch` in `librechat.yaml`) for the agent's `web_search` tool; Brave is also wired as an MCP server
- Admin panel is off (`profiles: ["admin"]`); not needed, users and config come from this repo

<details><summary>Setup notes</summary>

- `.env`: Anthropic key; replace the example secrets before first start (`openssl rand -hex 32` for `JWT_SECRET`, `JWT_REFRESH_SECRET`, `CREDS_KEY`; `-hex 16` for `CREDS_IV`). Changing `CREDS_*` later invalidates keys entered in the UI
- Ports are rebound with `ports: !override` — without `!override` Compose appends and the bind clashes
- Full reset: `docker compose down`, `sudo rm -rf ./data-node ./meili_data_v* ./logs ./uploads ./images`, then `docker volume rm` only the LibreChat volumes (`librechat-data`, `pgdata2`)
- Brave: `BRAVE_API_KEY` from `api-dashboard.search.brave.com` (free 2000 req/month)

</details>

## Agents and skills

- **Agent** = a different API key / model / toolset. One today: **Ai-kun** (`agents/ai-kun`: company key, Opus, web search). A personal one would need a personal Anthropic API key
- **Skill** = a procedure loaded when relevant: `guided-tutoring`, `karpathy-guidelines` (verbatim from multica-ai/andrej-karpathy-skills, MIT)
- **Memory** = facts and preferences about Ray, never files

`sync.py` (run by the `syncer` container) gives every agent: `agents/AGENT.md` + its own prompt, the 5 core memory tools, and every skill in `skills/`. Opt out per agent with `shared: false`.

<details><summary>Sync details</summary>

- `bootstrap-user` inserts the LibreChat account `syncer` logs in with (`LIBRECHAT_EMAIL` / `LIBRECHAT_PASSWORD` in `.env`); registration is closed otherwise
- Agents and skills are matched by name: created or updated, never duplicated. `id:` in an agent's frontmatter pins it to an existing agent instead, so it can be renamed; `avatar:` uploads that image file from the agent folder
- Removing one from the repo doesn't delete it in LibreChat; to delete everything the repo doesn't define: `docker compose run --rm -e SYNC_PRUNE=1 syncer`
- LibreChat silently drops MCP tools it can't verify; `sync.py` exits non-zero if an agent lost its memory tools — rerun once the memory server is up
- Default chat = `ai-kun` model spec in `librechat.yaml`, pointing at the same agent ID as `id:` in `agents/ai-kun/AGENT.md`
- Claude Code skills: `for d in ~/code/agent-skills/skills/*/; do ln -sfn "$d" ~/.claude-personal/skills/; done`

</details>

## Shared memory

[mcp-memory-service](https://github.com/doobidoo/mcp-memory-service), one per machine (Docker `mcp-memory` on the host, `uv` on the Mac), synced through Cloudflare (D1 + Vectorize + Workers AI, free tier). Reads are local; new memories reach Cloudflare in ~5 s, other machines pull hourly and on startup.

Tag rules (in `agents/AGENT.md`): one scope tag — project name or `general` — plus `preference` + one work type (`coding`, `science`, `writing`, `language`, `travel`) for preferences that hold across projects. Test after editing the rules: `CLAUDE_CONFIG_DIR=~/.claude-personal bin/test-memory-tags.py --runs 3`.

<details><summary>How it works</summary>

```
 Mac:  Claude Code → mcp-memory (uv) → SQLite ───────────────┐
 Host: LibreChat, Claude Code → mcp-memory (Docker) → SQLite ─┤ push ~5 s / pull hourly
       claude.ai → Cloudflare Tunnel ──┘                      ▼
                          Cloudflare: D1 (text, tags) + Vectorize (vectors)
```

- Search is local: keyword (FTS5 trigram, works for Japanese) + vectors from `paraphrase-multilingual-MiniLM-L12-v2` (384-dim). Keep this local model identical on every machine
- Cloudflare re-embeds with `@cf/baai/bge-m3` (1024-dim); the Vectorize index must be 1024-dim. Only text travels between machines
- Free tier caps at ~4.9k memories (Vectorize 5M stored dims); over the limit requests fail, never bill
- D1 keeps tags in `memory_tags` (authoritative); the `memories.tags` column goes stale after `memory_update`
- Image: `docker.io/doobidoo/mcp-memory-service:12.4.0` (pinned; the `ghcr.io` image is abandoned at an old, vulnerable version — never use it, and never expose anything < 11.11.0)

</details>

<details><summary>Setup</summary>

1. Cloudflare API token (Account: Account Settings Read, D1 Edit, Vectorize Edit, Workers AI Read), then create the resources:
   ```sh
   export $(grep -E '^CLOUDFLARE_(API_TOKEN|ACCOUNT_ID)=' .env | xargs)
   B="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID"
   curl -s -X POST "$B/d1/database" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" -d '{"name":"mcp-memory-db"}'
   curl -s -X POST "$B/vectorize/v2/indexes" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" -d '{"name":"mcp-memory-index","config":{"dimensions":1024,"metric":"cosine"}}'
   ```
   (Don't `. ./.env` in a shell — some values glob-expand.)
2. `.env`: `MCP_MEMORY_API_KEY` (`openssl rand -hex 32`), `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_D1_DATABASE_ID`, `CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index`
3. LibreChat connects via `mcpServers.memory` in `librechat.yaml` (`http://mcp-memory:8000/mcp`, needs `mcpSettings.allowedAddresses: ['mcp-memory:8000']`, and `requiresOAuth: false` — otherwise LibreChat sees the server's OAuth support and demands an OAuth login instead of sending the API key)
4. Claude Code on the host:
   ```sh
   claude mcp add --scope user --transport http memory http://127.0.0.1:2068/mcp --header "X-API-Key: <MCP_MEMORY_API_KEY>"
   ```
5. Mac: `uv tool install mcp-memory-service`, same `CLOUDFLARE_*` vars plus `MCP_MEMORY_STORAGE_BACKEND=hybrid`, `MCP_HYBRID_SYNC_OWNER=http`, `MCP_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2`, `CLOUDFLARE_EMBEDDING_MODEL=@cf/baai/bge-m3`; run `memory launch` and add it to Claude Code the same way

</details>

## claude.ai (personal subscription)

claude.ai is the personal second bot: same memory via a custom connector, same skills and rules. A Pro subscription can't power LibreChat or other apps (Anthropic's terms), so this is the supported route.

The memory server is published at `https://memory.galaxynetwork.dev` through a Cloudflare Tunnel (`cloudflared` container, part of the LibreChat stack, outbound only — no open ports). Logins require `MCP_MEMORY_API_KEY`. `docker compose stop cloudflared` takes claude.ai offline alone.

<details><summary>Setup</summary>

1. Cloudflare → Zero Trust → Networks → Tunnels → Create (Cloudflared). Copy only the token after `--token` into `CLOUDFLARE_TUNNEL_TOKEN` (don't run their command)
2. `.env`: `MEMORY_PUBLIC_URL=https://memory.<domain>` (must match the hostname exactly), `COMPOSE_PROFILES=tunnel`; `docker compose up -d`. The wizard's Next unlocks once the connector shows Connected
3. Tunnel → Published application routes → `memory` · `<domain>` · URL `http://mcp-memory:8000`
4. Check: `curl https://memory.<domain>/.well-known/oauth-authorization-server` shows that issuer; `curl -i https://memory.<domain>/api/memories` → 401
5. claude.ai → Settings → Connectors → Add custom connector → `https://memory.<domain>/mcp`, log in with `MCP_MEMORY_API_KEY`
6. From the bundle page (`http://localhost:2067/claude-ai/index.html`): Settings → Capabilities → Skills → upload the skills; Settings → Profile → paste `agents/AGENT.md`
7. Test: "What do you know about my computer setup?"

OAuth signing keys live in `LibreChat/secrets/mcp-memory-oauth/` (gitignored); without them claude.ai is logged out on every restart.

</details>
