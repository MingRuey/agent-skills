#!/usr/bin/env bash
# Point a Claude Code install at this repo: shared rules, shared skills, shared memory.
# Usage: bin/setup-claude.sh [rules|skills|memory|check|all]   (normally via `make`)
#
#   CLAUDE_CONFIG_DIR  Claude Code config folder; same rule as Claude Code itself: this variable
#                      if set (host: ~/.claude-personal), else ~/.claude (Mac)
#   MEMORY_URL         memory MCP endpoint; default: this host's server if LibreChat/.env
#                      is here, else the public https://memory.galaxynetwork.dev/mcp
#   MEMORY_API_KEY     memory server key (not a Cloudflare key); read from LibreChat/.env
#                      if present, otherwise asked for (input hidden)
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
DIR=${CLAUDE_CONFIG_DIR:-$HOME/.claude}
ENV_FILE=$REPO/LibreChat/.env
PUBLIC_URL=https://memory.galaxynetwork.dev/mcp

say() { printf '\033[1m[setup]\033[0m %s\n' "$*"; }
env_value() { [ -f "$ENV_FILE" ] && grep -m1 "^$1=" "$ENV_FILE" | cut -d= -f2- || true; }

rules() {
  mkdir -p "$DIR"
  local target=$REPO/agents/AGENT.md link=$DIR/CLAUDE.md
  if [ -e "$link" ] && [ ! -L "$link" ]; then
    mv "$link" "$link.bak.$(date +%Y%m%d%H%M%S)"
    say "backed up existing $link"
  fi
  ln -sfn "$target" "$link"
  say "rules: $link -> agents/AGENT.md"

  # Memory lives only in the memory server, so turn off Claude Code's file-based auto-memory
  python3 - "$DIR/settings.json" <<'EOF'
import json, os, sys
p = sys.argv[1]
s = json.load(open(p)) if os.path.exists(p) else {}
if s.get("autoMemoryEnabled") is not False:
    s["autoMemoryEnabled"] = False
    json.dump(s, open(p, "w"), indent=2)
    print("[setup] settings: autoMemoryEnabled = false")
EOF
}

skills() {
  mkdir -p "$DIR/skills"
  for d in "$REPO"/skills/*/; do
    [ -f "$d/SKILL.md" ] || continue
    ln -sfn "${d%/}" "$DIR/skills/$(basename "$d")"
    say "skill: $(basename "$d")"
  done
  # Drop links to skills that no longer exist in the repo
  for l in "$DIR"/skills/*; do
    [ -L "$l" ] && [[ $(readlink "$l") == "$REPO"/skills/* ]] && [ ! -e "$l" ] && rm "$l" && say "removed stale skill link $(basename "$l")"
  done
  return 0
}

resolve_memory() {
  local port
  port=$(env_value MCP_MEMORY_PORT)
  URL=${MEMORY_URL:-$([ -n "$port" ] && echo "http://127.0.0.1:$port/mcp" || echo "$PUBLIC_URL")}
  KEY=${MEMORY_API_KEY:-$(env_value MCP_MEMORY_API_KEY)}
  if [ -z "$KEY" ]; then
    read -rsp "Memory API key (MCP_MEMORY_API_KEY on the host; not a Cloudflare key): " KEY
    echo
  fi
  [ -n "$KEY" ] || { say "no memory key given"; exit 1; }
}

check() {
  resolve_memory
  local code
  code=$(curl -s -m 15 -o /dev/null -w '%{http_code}' -X POST "$URL" \
    -H "X-API-Key: $KEY" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"setup","version":"0"}}}' || true)
  case $code in
    200) say "memory: $URL answers with this key" ;;
    401|403) say "memory: $URL rejected the key ($code)"; exit 1 ;;
    *) say "memory: $URL unreachable (HTTP ${code:-none}) -- is the host and its LibreChat stack up?"; exit 1 ;;
  esac
}

memory() {
  command -v claude >/dev/null || { say "claude CLI not found in PATH"; exit 1; }
  check
  CLAUDE_CONFIG_DIR=$DIR claude mcp remove memory --scope user >/dev/null 2>&1 || true
  CLAUDE_CONFIG_DIR=$DIR claude mcp add --scope user --transport http memory "$URL" \
    --header "X-API-Key: $KEY" >/dev/null
  say "memory: registered $URL in $DIR (scope: user)"
}

say "Claude Code config folder: $DIR"
case ${1:-all} in
  rules) rules ;;
  skills) skills ;;
  memory) memory ;;
  check) check ;;
  all) rules; skills; memory; say "done -- start a new Claude Code session (or Zed thread) to pick it up" ;;
  *) echo "usage: $0 [rules|skills|memory|check|all]"; exit 2 ;;
esac
