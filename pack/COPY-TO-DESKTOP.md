# Copy to Desktop checklist

Use this when staging the pack on a new machine before merging into a project.

## Steps

1. Download `Claude-Code-Handoff.zip` from the docs site.
2. Unzip to `~/Desktop/Claude-Code-Handoff`.
3. Copy these files into the target project root:
   - `CLAUDE.md`
   - `AGENTS.md`
   - `.mcp.json`
   - `.claude/skills/working-agreements/SKILL.md`
   - `docs/HANDOFF.md`
   - `docs/SKILLS-AND-PLUGINS.md`
   - `docs/INVENTORY.json`
   - `scripts/setup-claude-code.sh`
4. From the project root, run:

```bash
bash scripts/setup-claude-code.sh
```

5. Edit `docs/HANDOFF.md` with the current task state.
6. Start Claude Code (or your agent IDE) in that project.

## Notes

- Do not commit Desktop copies; only commit files inside the real project.
- After first sync, keep inventory and `.mcp.json` in lockstep.
