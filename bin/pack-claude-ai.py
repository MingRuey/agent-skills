#!/usr/bin/env python3
"""Build the claude.ai download page.

  skills/<skill>.zip         one per skill, in the format claude.ai's skill upload requires:
                             a single top-level folder <skill>/ with SKILL.md inside
  agents.zip                 flat: AGENT.md (shared rules) + <agent>.md for every agent
  agents/AGENT.md, agents/<agent>.md   one link per agent file (for pasting)
  index.html                 the page (served by LibreChat at /claude-ai/index.html)

Usage: pack-claude-ai.py [OUT_DIR]   (default: dist/claude-ai)
Run by the syncer container after every sync; SKILLS_DIR / AGENTS_DIR override the
repo paths like in sync.py.
"""
import html
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = Path(os.environ.get("SKILLS_DIR", REPO / "skills"))
AGENTS_DIR = Path(os.environ.get("AGENTS_DIR", REPO / "agents"))
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "dist" / "claude-ai"


def collect():
    """(kind, path-in-bundle, source file) for every skill and agent markdown file."""
    files = [
        ("skills", f"{d.name}.zip", d)
        for d in sorted(SKILLS_DIR.iterdir())
        if (d / "SKILL.md").is_file()
    ]
    if (AGENTS_DIR / "AGENT.md").is_file():
        files.append(("agents", "AGENT.md", AGENTS_DIR / "AGENT.md"))
    files += [
        ("agents", f"{d.name}.md", d / "AGENT.md")
        for d in sorted(AGENTS_DIR.iterdir())
        if d.is_dir() and (d / "AGENT.md").is_file()
    ]
    return files


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.iterdir():  # clear contents, not the dir (it may be a mount point)
        shutil.rmtree(old) if old.is_dir() else old.unlink()

    files = collect()
    for kind in ("skills", "agents"):
        (OUT / kind).mkdir()
    with zipfile.ZipFile(OUT / "agents.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for k, rel, src in files:
            if k == "skills":
                with zipfile.ZipFile(OUT / "skills" / rel, "w", zipfile.ZIP_DEFLATED) as sz:
                    sz.writestr(f"{src.name}/", "")  # explicit top-level folder entry
                    for f in sorted(src.rglob("*")):
                        if f.is_file() and f.name != ".DS_Store":
                            sz.write(f, f.relative_to(src.parent))
            else:
                z.write(src, rel)
                shutil.copyfile(src, OUT / "agents" / rel)

    def section(kind, title):
        items = "\n".join(
            f'<li><a href="{html.escape(kind)}/{html.escape(rel)}" download>{html.escape(rel)}</a></li>'
            for k, rel, _ in files
            if k == kind
        )
        whole = (
            '<p>claude.ai &rarr; Settings &rarr; Capabilities &rarr; Skills: upload one zip per skill.</p>\n'
            if kind == "skills"
            else f'<p><a href="{kind}.zip" download><b>{kind}.zip</b></a> (all of them)</p>\n'
        )
        return f"<h2>{title}</h2>\n{whole}<ul>\n{items}\n</ul>"

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (OUT / "index.html").write_text(f"""<!doctype html>
<meta charset="utf-8"><title>claude.ai bundle</title>
<style>body{{font:16px system-ui;max-width:40em;margin:3em auto;padding:0 1em}}</style>
<h1>claude.ai bundle</h1>
<p>Built {stamp}</p>
{section("skills", "Skills")}
{section("agents", "Agents")}
""")
    n = sum(1 for k, *_ in files if k == "skills")
    print(f"[pack] {n} skills, {len(files) - n} agent files -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
