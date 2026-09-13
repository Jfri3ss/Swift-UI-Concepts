---
name: working-agreements
description: Shared working agreements for multi-session and multi-agent handoffs.
---

# Working agreements

## Definition of done

A task is done only when:

1. Code or docs for the request are in place
2. The project's verify/test command passes
3. `docs/HANDOFF.md` reflects the new current state (or notes the task is complete)

## Communication

- Prefer durable notes in `docs/HANDOFF.md` over chat-only context.
- Record risky assumptions explicitly.
- Link exact file paths, not vague area names.

## Conflict resolution

If two agents disagree:

1. Stop overlapping edits on the same files
2. Write both options in the handoff
3. Pick the smaller, reversible change unless the user specified otherwise
