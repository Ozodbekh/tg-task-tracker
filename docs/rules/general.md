# General Rules

These rules apply to every part of the project, backend and frontend alike.

## Code quality

- Write clean code. Readability first, no dead code, no leftovers.
- Performance matters. Avoid needless allocations, N+1 queries, and blocking
  calls in async paths. Measure before optimizing, but do not write knowingly
  slow code.

## Design principles

- **OOP / MRO** — use classes where they model the domain. Keep inheritance
  shallow and linear; be explicit about the MRO, prefer composition over deep
  hierarchies, and use `super()` correctly in cooperative chains.
- **SOLID** — single responsibility per class/module; extend rather than modify;
  subclasses must honor the base contract; small focused interfaces; depend on
  abstractions, not concrete implementations.
- **KISS** — the simplest solution that solves the actual problem.
- **YAGNI** — no speculative abstraction, no features that are not asked for.

## Comments

- Do not write comments in code. The code must explain itself through naming
  and structure.

## Language

- All `.md` files are written in English.
- All code, identifiers, logs, and internal strings are in English.
- UI-facing text may use another language — only when explicitly requested.