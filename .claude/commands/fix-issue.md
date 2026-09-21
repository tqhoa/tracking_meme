---
name: fix-issue
description: Analyze and fix a reported bug or issue — root cause first, symptom never
---

# /fix-issue — Bug Fix Process

> "Fix root causes, not symptoms."

## Purpose

Systematically analyze and fix a reported bug. Every fix must be verified with a test that would have caught it.

## Prerequisites

- Bug description, error message, or issue number
- Ability to reproduce the bug (or logs showing it occurred)

## Process

### Step 1: Understand the Issue

Gather all context before touching code:

```bash
# Check recent changes that could be related
git log --oneline -20

# Find all references to the failing component
grep -r "ComponentName\|function_name" src/ --include="*.py" --include="*.ts"
```

- What is the exact error message? (quote it verbatim)
- Which layer fails: frontend, backend API, database, external service?
- Is it reproducible consistently or intermittently?
- When did it start? (`git bisect` if unclear)

### Step 2: Reproduce Locally

**Do not fix what you cannot reproduce.**

```bash
# Backend — run failing test
pytest -k "test_name" -v

# Frontend — run failing test
npx vitest run --reporter=verbose tests/path/to/test.ts

# Manual reproduction — curl the failing endpoint
curl -X POST http://localhost:8000/api/v1/path \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```

If not reproducible:

- Check for timing/race conditions
- Check environment differences (env vars, DB state)
- Check test isolation (shared mutable state)

### Step 3: Write a Failing Test (Prove-It)

Write a test that reproduces the bug **before** fixing it:

```bash
# Verify test FAILS first — proves the bug exists
pytest -k "test_regression_issue_123" -v
# → FAILED (expected)
```

If you can't write a test, document why. Then fix.

### Step 4: Identify Root Cause

| Symptom                       | Likely Root Cause                               |
| ----------------------------- | ----------------------------------------------- |
| Duplicate results             | N+1 or missing `DISTINCT` in query              |
| `MissingGreenlet` error       | `expire_on_commit=True` on async SA session     |
| 401 on valid token            | JWT expiry too short or clock skew              |
| `NoneType` access             | Missing null check, data not loaded             |
| Stale data after mutation     | Missing `invalidateQueries`                     |
| Test passes locally, fails CI | Async ordering, missing `asyncio_mode = "auto"` |
| `v-html` XSS                  | Unsanitized user content rendered directly      |

**Fix the root cause. Never patch symptoms:**

| Symptom              | Bad Fix             | Good Fix                         |
| -------------------- | ------------------- | -------------------------------- |
| Duplicate list items | Dedupe in UI        | Fix query                        |
| Null reference error | Add `?.` everywhere | Ensure data loaded before access |
| Slow response        | Increase timeout    | Optimize query + add index       |
| Flaky test           | Add retry           | Fix race condition               |

### Step 5: Implement Minimal Fix

```bash
# Make the targeted fix — no scope creep
# Touch only the files directly related to the bug

# Backend
ruff check . && mypy .   # verify no new errors

# Frontend
tsc --noEmit              # verify no new type errors
```

Follow:

- `rules/error-handling.md` — error handling patterns
- `rules/code-style.md` — formatting (Black/Ruff for Python, ESLint for TS)
- `rules/security.md` — if the bug has security implications

### Step 6: Verify Fix

```bash
# Run the regression test — must PASS now
pytest -k "test_regression_issue_123" -v
# → PASSED

# Run full test suite — no regressions introduced
pytest --cov=. --cov-fail-under=80
mypy .
alembic upgrade head   # only if fix involved a migration

# Frontend
npm run test:run
tsc --noEmit
```

### Step 7: Commit

Follow `rules/git-workflow.md`:

```bash
git add <specific-files-only>
git commit -m "fix(scope): description of what was wrong and what fixed it

Closes #123"
```

---

## Red Flags — Stop and Reassess

- Cannot reproduce the bug → investigate environment/state first
- Fix requires touching > 3 unrelated files → probably treating a symptom
- No test written → how do you know it's fixed?
- Fix disables a safety check to make error go away → wrong direction

---

## Next Step

After fix is committed, run `/review` to verify code quality before merge.
