# Skills and plugins

## Included skill: working-agreements

Path: `.claude/skills/working-agreements/SKILL.md`

Use when:

- Multiple agents share a repo
- You need a crisp handoff between sessions
- You are aligning on definition of done

## Recommended Claude Code plugins

Keep this list short and explicit. Add only plugins you actually use.

| Plugin | Why | Status |
|--------|-----|--------|
| (none bundled) | Pack stays dependency-light | optional |

## MCP servers

Canonical list lives in `docs/INVENTORY.json`. Project stubs live in `.mcp.json`.

When adding a server:

1. Add the entry to `INVENTORY.json` with `id`, `url`, and `purpose`.
2. Mirror the same URL in `.mcp.json`.
3. Re-run `python3 scripts/verify.py` on the docs site repo (or your project's check).
