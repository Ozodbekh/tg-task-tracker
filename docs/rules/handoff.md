# Handoff Rules

Backend and frontend are written in separate sessions. They communicate only
through handoff notes in `docs/handoff/`.

## Direction

- `docs/handoff/backend-to-frontend/` — backend finished something the frontend
  needs to consume, or the API contract changed.
- `docs/handoff/frontend-to-backend/` — frontend needs something from the
  backend: a missing endpoint, a different response shape, a new field.

Write into the folder that matches the direction. Never write into the other
one.

## File name

`YYYY-MM-DD-HHMM.md` in Tashkent time (UTC+5), e.g. `2026-08-13-1914.md`.

Get it with:

```bash
TZ=Asia/Tashkent date +%Y-%m-%d-%H%M
```

One note per handoff. Never edit an old note; write a new one.

## Content

- A title line stating what this note is about.
- What was done, or what is needed — concrete, no vague requests.
- The affected endpoints or resources, with a link to their `docs/api/` file.
- What the other side must change, if anything.
- What is intentionally out of scope.

Keep it short. Contract details belong in `docs/api/`; the note points there
rather than duplicating it.

## Reading

At the start of a session, read the unhandled notes in the folder addressed to
your side. When a note is fully handled, add a `Status: handled` line at the top
of it.