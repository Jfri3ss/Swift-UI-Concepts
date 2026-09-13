# Claude Code Handoff (Workers site)

Static Cloudflare Worker that publishes the Claude Code handoff pack as HTML pages plus a downloadable zip.

## Develop

```bash
npm install
python3 scripts/verify.py
npm run deploy
```

Worker name: `claude-code-handoff`

## Layout

- `pack/` — source handoff files (also zipped into `Claude-Code-Handoff.zip`)
- `scripts/build.py` — Markdown → HTML, regenerate zip into `dist/`
- `scripts/verify.py` — canonical project check
- `wrangler.jsonc` — assets Worker (`html_handling` not `none`, custom `404-page`)

## Pack contents

README.md, CLAUDE.md, AGENTS.md, COPY-TO-DESKTOP.md, docs/*, .mcp.json, .claude/skills/working-agreements/SKILL.md, scripts/setup-claude-code.sh
