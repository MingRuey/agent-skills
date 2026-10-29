#!/usr/bin/env python3
"""Sync local agent + skills definitions to a LibreChat instance.

Reads everything under $AGENTS_DIR (default `/agents` inside the container, or
`./agents` for local runs) and $SKILLS_DIR (default `/skills`):

  $AGENTS_DIR/<agent-name>/AGENT.md
  $AGENTS_DIR/<agent-name>/skills/<skill-name>/SKILL.md   (agent-only skills)
  $SKILLS_DIR/<skill-name>/SKILL.md                       (shared skills)

Each markdown file is YAML-frontmatter + body. Body of AGENT.md becomes the
agent's `instructions`; body of SKILL.md becomes the skill's `body`.

Shared layer: the top-level `AGENT.md` (no frontmatter) is prepended to every
agent's instructions, and the core `memory` MCP tools are added to its tools.
Every shared skill under $SKILLS_DIR is attached too. An agent opts out of all
three with `shared: false` in its frontmatter. LibreChat
silently drops MCP tools it can't authorize, so each saved agent is checked and
the run exits non-zero if any shared tool went missing.

SYNC_PRUNE=1 deletes this user's agents and skills that the repo doesn't define
(e.g. ones built by hand in the UI). Off by default because it is destructive.

Auth: POSTs LIBRECHAT_EMAIL + LIBRECHAT_PASSWORD to /api/auth/login each run.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

BASE_URL = os.environ.get(
    "LIBRECHAT_URL",
    f"http://localhost:{os.environ.get('PORT', '3080')}",
).rstrip("/")
EMAIL = os.environ.get("LIBRECHAT_EMAIL")
PASSWORD = os.environ.get("LIBRECHAT_PASSWORD")
AGENTS_DIR = Path(os.environ.get("AGENTS_DIR", "/agents"))
SKILLS_DIR = Path(os.environ.get("SKILLS_DIR", "/skills"))
PRUNE = os.environ.get("SYNC_PRUNE") == "1"

if not EMAIL or not PASSWORD:
    sys.exit("[sync] LIBRECHAT_EMAIL and LIBRECHAT_PASSWORD must be set")

SHARED_MD = AGENTS_DIR / "AGENT.md"
SHARED_TOOLS = [
    f"{tool}_mcp_memory"
    for tool in ("memory_store", "memory_search", "memory_update", "memory_delete", "memory_list")
]

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def _decode(raw):
    """Return parsed JSON if possible, else the raw text (or None on empty)."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.decode(errors="replace")


BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def http(method, path, *, token=None, body=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": BROWSER_UA,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE_URL}{path}", method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, _decode(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, _decode(e.read())


def wait_for_api(retries=90, delay=2):
    """Cold starts (fresh image, MCP init) can take a couple of minutes."""
    print(f"[sync] waiting for {BASE_URL} (up to ~{retries * delay // 60} min) ...", flush=True)
    for _ in range(retries):
        try:
            urllib.request.urlopen(f"{BASE_URL}/", timeout=2)
            return
        except urllib.error.HTTPError:
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(delay)
    sys.exit(f"[sync] API at {BASE_URL} did not become reachable")


def login():
    status, body = http("POST", "/api/auth/login", body={"email": EMAIL, "password": PASSWORD})
    if status != 200 or not isinstance(body, dict) or "token" not in body:
        sys.exit(f"[sync] login failed ({status}): {body}")
    return body["token"]


def parse_md(text):
    m = FRONTMATTER.match(text)
    if not m:
        raise ValueError("missing or malformed YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}, m.group(2).strip()


def list_remote(token, path, items_key_candidates):
    status, body = http("GET", path, token=token)
    if status != 200:
        sys.exit(f"[sync] GET {path} failed ({status}): {body!r}")
    if body is None:
        return []
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in items_key_candidates:
            value = body.get(key)
            if isinstance(value, list):
                return value
        # dict but no recognized key — treat as empty
        return []
    # Non-JSON text response (e.g. HTML) — log a clipped preview and continue
    preview = (body or "")[:300] if isinstance(body, str) else repr(body)[:300]
    print(f"[sync] WARN: GET {path} returned non-JSON body, treating as empty. Preview: {preview!r}", flush=True)
    return []


def upsert_skill(token, skill_dir):
    fm, body = parse_md((skill_dir / "SKILL.md").read_text())
    name = fm.pop("name", None)
    description = fm.pop("description", None)
    if not name or not description:
        sys.exit(f"[sync] {skill_dir}/SKILL.md missing required name/description")

    payload = {
        "name": name,
        "description": description,
        "body": body,
        "frontmatter": fm,
    }

    existing = next((s for s in list_remote(token, "/api/skills", ["skills"]) if s.get("name") == name), None)

    if existing is None:
        status, resp = http("POST", "/api/skills", token=token, body=payload)
        if status not in (200, 201):
            sys.exit(f"[sync] create skill {name} failed ({status}): {resp}")
        print(f"[sync]   + skill {name} ({resp['_id']})", flush=True)
        return resp["_id"]

    skill_id = existing["_id"]
    payload["expectedVersion"] = existing.get("version", 1)
    status, resp = http("PATCH", f"/api/skills/{skill_id}", token=token, body=payload)
    if status not in (200, 201):
        sys.exit(f"[sync] update skill {name} failed ({status}): {resp}")
    print(f"[sync]   ~ skill {name} ({skill_id})", flush=True)
    return skill_id


def upsert_agent(token, agent_dir, skill_ids, shared_text, shared_skill_ids):
    """Returns the shared tools LibreChat dropped from the saved agent (empty if none)."""
    fm, body = parse_md((agent_dir / "AGENT.md").read_text())
    name = fm.get("name")
    if not name:
        sys.exit(f"[sync] {agent_dir}/AGENT.md missing name")

    use_shared = fm.get("shared", True)
    tools = list(fm.get("tools", []) or [])
    if use_shared:
        if shared_text:
            body = f"{shared_text}\n\n{body}"
        tools += [t for t in SHARED_TOOLS if t not in tools]

    payload = {
        "name": name,
        "description": fm.get("description"),
        "instructions": body,
        "provider": fm.get("provider", "anthropic"),
        "model": fm.get("model"),
        "model_parameters": fm.get("model_parameters", {}),
        "tools": tools,
    }

    skill_refs = fm.get("skills", []) or []
    unknown = [s for s in skill_refs if s not in skill_ids]
    if unknown:
        sys.exit(f"[sync] agent {name} references unknown skills: {unknown}")
    attached = [skill_ids[s] for s in skill_refs]
    if use_shared:
        attached += [i for i in shared_skill_ids if i not in attached]
    if attached:
        payload["skills"] = attached
        payload["skills_enabled"] = fm.get("skills_enabled", True)

    items = list_remote(token, "/api/agents", ["data", "agents"])
    existing = next((a for a in items if a.get("name") == name), None)

    def _id_of(obj):
        if isinstance(obj, dict):
            return obj.get("id") or obj.get("_id") or "?"
        return "?"

    if existing is None:
        status, resp = http("POST", "/api/agents", token=token, body=payload)
        if status not in (200, 201):
            sys.exit(f"[sync] create agent {name} failed ({status}): {resp!r}")
        print(f"[sync]   + agent {name} ({_id_of(resp)})", flush=True)
    else:
        agent_id = _id_of(existing)
        status, resp = http("PATCH", f"/api/agents/{agent_id}", token=token, body=payload)
        if status not in (200, 201):
            sys.exit(f"[sync] update agent {name} failed ({status}): {resp!r}")
        print(f"[sync]   ~ agent {name} ({agent_id})", flush=True)

    if not use_shared:
        return name, []
    saved = resp.get("tools") if isinstance(resp, dict) else None
    if saved is None:
        print(f"[sync]   ? agent {name}: response has no tools list, can't verify memory tools", flush=True)
        return name, []
    missing = [t for t in SHARED_TOOLS if t not in saved]
    if missing:
        print(f"[sync]   ! agent {name}: LibreChat dropped {missing} "
              "(is the memory server connected, and may this user use MCP?)", flush=True)
    return name, missing


def prune(token, kind, path, keys, keep, id_keys):
    """Delete remote items of `kind` whose name isn't in `keep`."""
    for item in list_remote(token, path, keys):
        name = item.get("name")
        item_id = next((item[k] for k in id_keys if item.get(k)), None)
        if name in keep or not item_id:
            continue
        status, resp = http("DELETE", f"{path}/{item_id}", token=token)
        if status not in (200, 204):
            sys.exit(f"[sync] delete {kind} {name} failed ({status}): {resp!r}")
        print(f"[sync]   - {kind} {name} ({item_id})", flush=True)


def _skill_names(root):
    """Frontmatter names of every SKILL.md directly under `root`."""
    if not root.is_dir():
        return []
    return [
        parse_md((d / "SKILL.md").read_text())[0].get("name")
        for d in sorted(root.iterdir())
        if (d / "SKILL.md").exists()
    ]


def main():
    wait_for_api()
    token = login()
    print("[sync] authenticated", flush=True)

    if not AGENTS_DIR.is_dir():
        sys.exit(f"[sync] AGENTS_DIR {AGENTS_DIR} does not exist")

    shared_text = SHARED_MD.read_text().strip() if SHARED_MD.is_file() else ""
    print(f"[sync] shared layer: {len(shared_text.split())} words, {len(SHARED_TOOLS)} memory tools", flush=True)
    dropped = {}

    shared_skill_ids = {}
    if SKILLS_DIR.is_dir():
        print("[sync] shared skills", flush=True)
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if (skill_dir / "SKILL.md").exists():
                shared_skill_ids[skill_dir.name] = upsert_skill(token, skill_dir)
    synced_skills = set(_skill_names(SKILLS_DIR))
    synced_agents = set()

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or not (agent_dir / "AGENT.md").exists():
            continue

        print(f"[sync] {agent_dir.name}", flush=True)
        skill_ids = {}
        skills_root = agent_dir / "skills"
        if skills_root.is_dir():
            for skill_dir in sorted(skills_root.iterdir()):
                if (skill_dir / "SKILL.md").exists():
                    skill_ids[skill_dir.name] = upsert_skill(token, skill_dir)
            synced_skills |= set(_skill_names(skills_root))

        name, missing = upsert_agent(
            token, agent_dir, skill_ids, shared_text, list(shared_skill_ids.values())
        )
        synced_agents.add(name)
        if missing:
            dropped[agent_dir.name] = missing

    if PRUNE:
        print("[sync] pruning items not defined in the repo", flush=True)
        prune(token, "agent", "/api/agents", ["data", "agents"], synced_agents, ["id", "_id"])
        prune(token, "skill", "/api/skills", ["skills"], synced_skills, ["_id"])

    if dropped:
        sys.exit(f"[sync] done, but memory tools missing on: {', '.join(dropped)}")
    print("[sync] done", flush=True)


if __name__ == "__main__":
    main()
