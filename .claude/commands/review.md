---
name: review
description: Five-axis code review before merge — correctness, readability, architecture, security, performance
---

# /review — Code Review

> "Approve when a change definitely improves code health, even if imperfect."

## Purpose

Conduct a five-axis code review of specified files, a PR diff, or recent changes. Catch bugs, security issues, and design problems before merge.

## Prerequisites

- Code to review: file path, PR number, or `git diff` output
- Understanding of what the change is trying to accomplish

## Workflow

### Step 1: Understand the Change

```bash
# Review what changed
git diff master...HEAD
git log --oneline master...HEAD
```

- What is this change trying to do?
- Is there a linked spec or issue?

### Step 2: Review Tests First

Tests reveal intent, expected behavior, and coverage gaps. Start here before reading implementation.

### Step 3: Walk the Five Axes

Full checklist: `.claude/agents/code-reviewer.md` and `.claude/skills/code-review/SKILL.md`

| Axis             | Key Questions                                                                |
| ---------------- | ---------------------------------------------------------------------------- |
| **Correctness**  | Does it do what it claims? Edge cases handled? Error paths covered?          |
| **Readability**  | Can another engineer understand this without help? Names clear?              |
| **Architecture** | Follows project patterns? Import direction correct? Abstraction appropriate? |
| **Security**     | Inputs validated? Auth enforced? No secrets? See `rules/security.md`         |
| **Performance**  | N+1 queries? Unbounded operations? Missing indexes?                          |

### Step 4: Check Project-Specific Rules

**Backend (Python / FastAPI):**

- [ ] `rules/error-handling.md` — AppError, no bare `except`, `details` key for validation errors
- [ ] `rules/database.md` — SQLAlchemy ORM only, `expire_on_commit=False`, `session.begin()`
- [ ] `rules/security.md` — Pydantic on all inputs, auth dependency on protected routes
- [ ] `rules/testing.md` — async generator DI override, normal constructor in fixtures

**Frontend (Vue 3 / TypeScript):**

- [ ] `rules/vue-patterns.md` — `<script setup>`, store at top of setup, `onUnmounted` cleanup
- [ ] `rules/security.md` — no raw `v-html`, no secrets committed
- [ ] `rules/testing.md` — `emitted()` for events, `setActivePinia` in store tests

### Step 5: Run Verification Commands

```bash
# Backend
pytest --cov=. --cov-fail-under=80    # coverage gate
mypy .                                 # type errors

# Frontend
tsc --noEmit                           # type errors
npm run test:run                       # full suite
```

Fail on any command = REQUEST CHANGES before reviewing further.

### Step 6: Produce Output

---

## Output Format

```
## Review Summary

**Overall**: APPROVE | REQUEST CHANGES | NEEDS DISCUSSION

### Critical (merge blocker)
path:line: CRITICAL: <problem>. <fix>.

### High (should fix before merge)
path:line: HIGH: <problem>. <fix>.

### Medium (consider fixing)
path:line: MEDIUM: <problem>. <fix>.

### Low (minor / optional)
path:line: LOW: <problem>. <fix>.
```

One finding per line. File path + line on every finding. Fix suggestion on every finding. No praise.

---

## Automatic REQUEST CHANGES

Any of these = block merge immediately:

- Raw SQL string concatenation with user input (use ORM or parameterized `text()`)
- Hardcoded secret, token, or password in source code
- Missing auth dependency on a protected FastAPI route
- Bare `except:` or `except Exception: pass` silencing errors
- `v-html` with unsanitized user-controlled content
- Test that contains no assertions
- `any` / `Any` type used without an explanatory comment
- N+1 query in a loop without `selectinload` / Prisma `include`
- DB schema change with no Alembic migration file
- Coverage drops below 80% (`--cov-fail-under=80` gate fails)
- `mypy` / `tsc --noEmit` errors introduced by the change

---

## Next Step

After review passes, run `/deploy` to ship.
