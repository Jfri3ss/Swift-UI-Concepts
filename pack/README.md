# Claude Code Handoff Pack

A portable starter kit for handing work between Claude Code sessions, Cursor agents, and teammates.

## What's inside

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Project instructions Claude Code loads automatically |
| `AGENTS.md` | Cross-tool agent conventions (Cursor, Codex, Claude) |
| `COPY-TO-DESKTOP.md` | Quick copy checklist for a fresh machine |
| `docs/HANDOFF.md` | Session handoff template |
| `docs/SKILLS-AND-PLUGINS.md` | Skills and plugins inventory notes |
| `docs/INVENTORY.json` | Machine-readable MCP / tool inventory |
| `.mcp.json` | Project MCP server stubs |
| `.claude/skills/working-agreements/SKILL.md` | Shared working-agreements skill |
| `scripts/setup-claude-code.sh` | Bootstrap helper for Claude Code |

## Quick start

1. Download [Claude-Code-Handoff.zip](./Claude-Code-Handoff.zip).
2. Unzip into your project root (or Desktop staging folder).
3. Run `bash scripts/setup-claude-code.sh`.
4. Open `docs/HANDOFF.md`, fill the current-state section, and start Claude Code.

## Browse on the web

- [CLAUDE.md](./CLAUDE.html)
- [AGENTS.md](./AGENTS.html)
- [Copy to Desktop](./COPY-TO-DESKTOP.html)
- [Handoff guide](./docs/HANDOFF.html)
- [Skills & plugins](./docs/SKILLS-AND-PLUGINS.html)
- [Inventory JSON](./docs/INVENTORY.json)

## Design goals

- **One pack, many tools** — same files work in Claude Code, Cursor, and other agent IDEs.
- **Handoff first** — every session can leave a crisp next-action note.
- **Auditable MCP** — `.mcp.json` URLs must match `docs/INVENTORY.json`.
