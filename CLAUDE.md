# CLAUDE.md

## Project

`tg-task-tracker` — a monorepo with a Python backend and a React frontend.

```
backend/    Python 3.14, Telethon, Starlette, aiosqlite (uv workspace member)
frontend/   React + Vite + TypeScript
docs/rules/ project rules
docs/api/   API contract
docs/handoff/ cross-session notes
```

Backend and frontend are worked on in separate sessions. A session reads only
the rules of its own side.

## Rules

@docs/rules/general.md
@docs/rules/claude-md.md
@docs/rules/handoff.md

Before touching `backend/`, read `backend/CLAUDE.md`.
Before touching `frontend/`, read `frontend/CLAUDE.md`.
Read them before writing any code, not after.

## Reporting

Keep answers short. State what was done, nothing more. No summaries of the
obvious, no restating the code, no next-step essays. Tokens are a cost.
