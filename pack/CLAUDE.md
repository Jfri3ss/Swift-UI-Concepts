# Project instructions for Claude Code

You are working in a repository that uses the Claude Code Handoff Pack.

## Always do

1. Read `docs/HANDOFF.md` before making large changes.
2. Prefer small, reviewable diffs over broad rewrites.
3. Keep secrets out of the repo; use environment variables and secret stores.
4. After meaningful progress, update the **Current state** and **Next actions** sections in `docs/HANDOFF.md`.
5. Run the project's verify command before claiming done (`python3 scripts/verify.py` for this pack's site).

## Never do

- Commit `.env`, API tokens, or private keys.
- Invent MCP server URLs — only use entries listed in `docs/INVENTORY.json`.
- Skip handoff notes when stopping mid-task.

## Working style

- Ask clarifying questions only when blocked; otherwise proceed with the safest assumption and document it in the handoff.
- Match existing code style and file layout.
- Prefer editing existing files over creating new ones.

## Skills

Load `.claude/skills/working-agreements/SKILL.md` when coordinating multi-agent or multi-session work.
