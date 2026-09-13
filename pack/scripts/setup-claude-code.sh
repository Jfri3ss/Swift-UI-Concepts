#!/usr/bin/env bash
# Bootstrap helper for the Claude Code Handoff Pack.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "Claude Code Handoff Pack — setup"
echo "Root: $ROOT"

missing=0
for path in \
  CLAUDE.md \
  AGENTS.md \
  docs/HANDOFF.md \
  docs/INVENTORY.json \
  .mcp.json \
  .claude/skills/working-agreements/SKILL.md
do
  if [[ ! -e "$path" ]]; then
    echo "Missing: $path" >&2
    missing=1
  else
    echo "OK: $path"
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Setup incomplete — restore missing pack files." >&2
  exit 1
fi

chmod +x "$ROOT/scripts/setup-claude-code.sh" 2>/dev/null || true
echo
echo "Next: edit docs/HANDOFF.md, then start Claude Code in this directory."
