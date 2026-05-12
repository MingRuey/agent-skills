#!/usr/bin/env python3
"""Sync local agent + skills definitions to a LibreChat instance.

Reads everything under $AGENTS_DIR (default `/agents` inside the container, or
`./agents` for local runs):

  <agent-name>/AGENT.md
  <agent-name>/skills/<skill-name>/SKILL.md

Each markdown file is YAML-frontmatter + body. Body of AGENT.md becomes the
agent's `instructions`; body of SKILL.md becomes the skill's `body`.

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

if not EMAIL or not PASSWORD:
    sys.exit("[sync] LIBRECHAT_EMAIL and LIBRECHAT_PASSWORD must be set")

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


def wait_for_api(retries=30, delay=2):
    print(f"[sync] waiting for {BASE_URL} ...", flush=True)
    for _ in range(retries):
        try:
            urllib.request.urlopen(f"{BASE_URL}/", timeout=2)
            return
        except urllib.error.HTTPError:
            return
        except urllib.error.URLError:
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


def upsert_agent(token, agent_dir, skill_ids):
    fm, body = parse_md((agent_dir / "AGENT.md").read_text())
    name = fm.get("name")
    if not name:
        sys.exit(f"[sync] {agent_dir}/AGENT.md missing name")

    payload = {
        "name": name,
        "description": fm.get("description"),
        "instructions": body,
        "provider": fm.get("provider", "anthropic"),
        "model": fm.get("model"),
        "model_parameters": fm.get("model_parameters", {}),
        "tools": fm.get("tools", []),
    }

    skill_refs = fm.get("skills", []) or []
    if skill_refs:
        unknown = [s for s in skill_refs if s not in skill_ids]
        if unknown:
            sys.exit(f"[sync] agent {name} references unknown skills: {unknown}")
        payload["skills"] = [skill_ids[s] for s in skill_refs]
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
        return

    agent_id = _id_of(existing)
    status, resp = http("PATCH", f"/api/agents/{agent_id}", token=token, body=payload)
    if status not in (200, 201):
        sys.exit(f"[sync] update agent {name} failed ({status}): {resp!r}")
    print(f"[sync]   ~ agent {name} ({agent_id})", flush=True)


def main():
    wait_for_api()
    token = login()
    print("[sync] authenticated", flush=True)

    if not AGENTS_DIR.is_dir():
        sys.exit(f"[sync] AGENTS_DIR {AGENTS_DIR} does not exist")

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

        upsert_agent(token, agent_dir, skill_ids)

    print("[sync] done", flush=True)


if __name__ == "__main__":
    main()
