#!/usr/bin/env python3
"""Project check for the Claude Code handoff Workers site."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "pack"
DIST = ROOT / "dist"
WRANGLER = ROOT / "wrangler.jsonc"

ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def load_wrangler() -> dict:
    raw = WRANGLER.read_text(encoding="utf-8")
    # Strip // comments for naive JSONC parse
    raw = re.sub(r"//.*?$", "", raw, flags=re.M)
    return json.loads(raw)


def check_pack_present() -> None:
    required = [
        "README.md",
        "CLAUDE.md",
        "AGENTS.md",
        "COPY-TO-DESKTOP.md",
        "docs/HANDOFF.md",
        "docs/SKILLS-AND-PLUGINS.md",
        "docs/INVENTORY.json",
        ".mcp.json",
        ".claude/skills/working-agreements/SKILL.md",
        "scripts/setup-claude-code.sh",
    ]
    for rel in required:
        if not (PACK / rel).is_file():
            err(f"Missing pack file: pack/{rel}")


def check_mcp_inventory() -> None:
    inv_path = PACK / "docs" / "INVENTORY.json"
    mcp_path = PACK / ".mcp.json"
    if not inv_path.is_file() or not mcp_path.is_file():
        return
    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
    servers = mcp.get("mcpServers") or {}
    inv_by_id = {s["id"]: s for s in inventory.get("mcp_servers", [])}

    for sid, meta in servers.items():
        if sid not in inv_by_id:
            err(f".mcp.json server {sid!r} missing from INVENTORY.json")
            continue
        url = meta.get("url")
        inv_url = inv_by_id[sid].get("url")
        if url != inv_url:
            err(f"URL mismatch for {sid!r}: .mcp.json={url!r} inventory={inv_url!r}")

    for sid in inv_by_id:
        if sid not in servers:
            err(f"INVENTORY.json server {sid!r} missing from .mcp.json")


def check_gitignore() -> None:
    gi = ROOT / ".gitignore"
    if not gi.is_file():
        err("Missing .gitignore")
        return
    text = gi.read_text(encoding="utf-8")
    if ".wrangler/" not in text and ".wrangler" not in text:
        err(".gitignore must include .wrangler/")
    if "__pycache__" not in text and "*.pyc" not in text:
        err(".gitignore must ignore Python bytecode (__pycache__/ or *.pyc)")


def check_wrangler() -> None:
    if not WRANGLER.is_file():
        err("Missing wrangler.jsonc")
        return
    cfg = load_wrangler()
    if cfg.get("name") != "claude-code-handoff":
        err(f"Worker name must be claude-code-handoff, got {cfg.get('name')!r}")
    assets = cfg.get("assets") or {}
    if assets.get("directory") not in ("./dist", "dist", "./dist/"):
        err(f"assets.directory should be ./dist, got {assets.get('directory')!r}")
    html_handling = assets.get("html_handling")
    if html_handling == "none":
        err("assets.html_handling must not be 'none' (homepage / must serve HTML)")
    if assets.get("not_found_handling") != "404-page":
        err("assets.not_found_handling must be '404-page'")


def check_dist() -> None:
    if not DIST.is_dir():
        err("dist/ missing — run python3 scripts/build.py")
        return
    for rel in [
        "index.html",
        "404.html",
        "styles.css",
        "README.html",
        "CLAUDE.html",
        "AGENTS.html",
        "COPY-TO-DESKTOP.html",
        "docs/HANDOFF.html",
        "docs/SKILLS-AND-PLUGINS.html",
        "docs/INVENTORY.json",
        "Claude-Code-Handoff.zip",
    ]:
        if not (DIST / rel).is_file():
            err(f"Missing dist artifact: {rel}")

    # Site links should point at HTML pages, not raw .md that 404
    html_files = list(DIST.rglob("*.html"))
    md_href = re.compile(r'href=["\']([^"\']+\.md)["\']', re.I)
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        for m in md_href.finditer(text):
            href = m.group(1)
            if href.startswith(("http://", "https://")):
                continue
            err(f"{path.relative_to(DIST)} links to markdown {href!r} (should be HTML)")

    zip_path = DIST / "Claude-Code-Handoff.zip"
    if zip_path.is_file():
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
            expected = [
                "Claude-Code-Handoff/README.md",
                "Claude-Code-Handoff/CLAUDE.md",
                "Claude-Code-Handoff/AGENTS.md",
                "Claude-Code-Handoff/COPY-TO-DESKTOP.md",
                "Claude-Code-Handoff/docs/HANDOFF.md",
                "Claude-Code-Handoff/docs/SKILLS-AND-PLUGINS.md",
                "Claude-Code-Handoff/docs/INVENTORY.json",
                "Claude-Code-Handoff/.mcp.json",
                "Claude-Code-Handoff/.claude/skills/working-agreements/SKILL.md",
                "Claude-Code-Handoff/scripts/setup-claude-code.sh",
            ]
            for name in expected:
                if name not in names:
                    err(f"Zip missing {name}")


def main() -> int:
    # Always rebuild so zip/HTML stay in sync with pack
    sys.path.insert(0, str(ROOT / "scripts"))
    from build import build  # type: ignore

    build()

    check_pack_present()
    check_mcp_inventory()
    check_gitignore()
    check_wrangler()
    check_dist()

    if ERRORS:
        print("verify FAILED:")
        for e in ERRORS:
            print(f"  - {e}")
        return 1
    print("verify OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
