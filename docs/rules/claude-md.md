# CLAUDE.md Rules

Every package gets its own `CLAUDE.md`, in `backend/` and `frontend/` alike.

## Purpose

A reader must understand what the package is and what it does without opening
its code.

## Placement

- One `CLAUDE.md` per package directory.
- A nested package gets its own; it does not inherit the parent's file.
- Test directories follow the same rule.

## Content

Short and exact. Nothing that repeats the code.

1. One-line statement of what the package is responsible for.
2. What each module in it does — one line per file.
3. Notes a reader cannot infer: invariants, ordering, side effects, gotchas.

## Constraints

- No code snippets, no signatures, no copied logic.
- No history, no rationale essays, no future plans.
- Update it in the same change that alters the package. A stale `CLAUDE.md` is
  a bug.