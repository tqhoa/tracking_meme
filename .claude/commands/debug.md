---
name: debug
description: Systematic debugging and error recovery — find root cause, not symptoms
---

# /debug — Debugging & Error Recovery

> "Fix root causes, not symptoms."

## Purpose

Systematically diagnose and fix errors. Stop feature work, preserve evidence, find root cause, add guards, then resume.

## The Stop-the-Line Rule

When unexpected failures occur:

1. **STOP** — Halt feature work immediately
2. **PRESERVE** — Save error messages, logs, stack traces
3. **DIAGNOSE** — Follow the 6-step triage process
4. **FIX** — Address root cause, not symptoms
5. **GUARD** — Add regression test
6. **RESUME** — Only continue after verification

---

## 6-Step Triage Process

### Step 1: Reproduce

Make the failure happen reliably.

```bash
# Python
pytest -k "failing_test_name" -v -s

# JavaScript
npx vitest run --reporter=verbose -t "failing test name"

# API — reproduce with curl
curl -X POST http://localhost:8000/api/v1/resource \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```

**If not reproducible**, investigate:

- Timing/race conditions
- Environment differences (dev vs CI)
- State leakage between tests
- `asyncio` event loop not reset between tests (Python)

### Step 2: Localize

Identify which layer fails:

| Layer                     | Symptoms                                                    |
| ------------------------- | ----------------------------------------------------------- |
| **Frontend (Vue)**        | Render errors, missing elements, wrong display              |
| **API (FastAPI)**         | 4xx/5xx responses, 422 validation errors, 500 unhandled     |
| **Service layer**         | Wrong business logic output, missing domain event           |
| **Database (SQLAlchemy)** | `MissingGreenlet`, N+1, constraint violation, stale session |
| **Migration (Alembic)**   | `relation does not exist`, column mismatch                  |
| **Build**                 | `mypy` errors, `tsc` errors, missing deps                   |
| **External**              | Third-party API failures, network issues                    |
| **Test itself**           | Flaky assertion, wrong expectations, shared state           |

**Use `git bisect` for regressions:**

```bash
git bisect start
git bisect bad HEAD
git bisect good <last-known-good-commit>
git bisect reset   # when done
```

### Step 3: Reduce

Strip away unrelated elements — isolate the failing unit:

**Python:**

```python
# Original complex failing code
result = await order_service.create(user_id, cart_id, payment_data)

# Reduce step by step
user = await user_repo.find_by_id(user_id)
print("user:", user)                    # check each step

cart = await cart_repo.find_by_id(cart_id)
print("cart:", cart)

result = await order_service.create(user, cart, payment_data)
```

**JavaScript:**

```javascript
// Reduce to find which call fails
const config = await getConfig();
console.log("[DEBUG] config:", config);

const data = await fetchData();
console.log("[DEBUG] data:", data);

const result = await processOrder(config, data);
```

### Step 4: Fix Root Cause

**Fix the actual problem, not the symptom:**

| Symptom                  | Bad Fix                 | Good Fix                                        |
| ------------------------ | ----------------------- | ----------------------------------------------- |
| Duplicate list items     | Dedupe in UI            | Fix query returning duplicates                  |
| `MissingGreenlet` error  | Wrap in `asyncio.run()` | Use `expire_on_commit=False` in session factory |
| 422 Unprocessable Entity | Catch and ignore        | Fix Pydantic schema to match request shape      |
| N+1 queries              | Cache result in loop    | Add `selectinload()` to the base query          |
| Null reference           | Add `?.` everywhere     | Ensure data loaded before access                |
| Slow API response        | Increase timeout        | Optimize the query or add index                 |
| Flaky test               | Add retry logic         | Fix the race condition or shared state          |

### Step 5: Guard Against Recurrence

Write a regression test before fixing:

**Python:**

```python
@pytest.mark.asyncio
async def test_get_order_items_returns_no_duplicates(client, auth_headers, seed_order):
    response = await client.get(f"/api/v1/orders/{seed_order.id}/items", headers=auth_headers)
    ids = [item["id"] for item in response.json()["data"]]
    assert len(ids) == len(set(ids))
```

**JavaScript:**

```javascript
it("should not return duplicate items (regression)", async () => {
  await createOrder({ items: [item, item] });
  const result = await getOrderItems();
  const ids = result.map((r) => r.id);
  expect(ids).toEqual([...new Set(ids)]);
});
```

### Step 6: Verify End-to-End

```bash
# Backend
pytest -k "regression" -v
pytest --cov=. --cov-fail-under=80
mypy .

# Frontend
npx vitest run --reporter=verbose
npm run build
tsc --noEmit
```

---

## Error-Specific Triage Trees

### Python / FastAPI

```
FastAPI error
├── 422 Unprocessable Entity
│   ├── Request body field name mismatch → check Pydantic schema field names
│   ├── Wrong field type → check type annotations
│   └── Missing required field → add field or make Optional
├── 500 Internal Server Error
│   ├── Check structlog output for exception traceback
│   ├── AppError not raised → bare Exception leaked through
│   └── DB error → see SQLAlchemy section below
├── 401 Unauthorized
│   └── Auth dependency missing or token expired
└── 403 Forbidden
    └── Role/ownership check failed — check authorization logic

SQLAlchemy error
├── MissingGreenlet
│   └── session expired after commit → set expire_on_commit=False
├── DetachedInstanceError
│   └── accessing relation outside session → use selectinload eagerly
├── IntegrityError
│   ├── Unique constraint → duplicate insert
│   └── ForeignKey violation → parent record missing
└── OperationalError
    ├── Connection pool exhausted → reduce pool_size or fix connection leak
    └── "relation does not exist" → missing alembic migration (run: alembic upgrade head)

pytest error
├── AssertionError → check actual vs expected values with -s flag
├── RuntimeError: event loop closed → missing asyncio_mode = "auto" in pyproject.toml
├── greenlet_spawn error → sync code called inside async context
└── Fixture not found → check conftest.py scope and import
```

### TypeScript / Vue

```
Build / Type error
├── mypy error → fix type annotation or add cast with comment
├── tsc error → fix type or use unknown + type guard
└── Vite build error → check import paths, missing deps (npm install)

Test failure (Vitest)
├── Assertion error → check actual value with console.log
├── TypeError → check null/undefined — add optional chaining
└── Timeout → async not awaited, or test setup hanging

Vue runtime error
├── [Vue warn] Missing required prop → add prop or default
├── [Vue warn] Extraneous non-props attributes → use $attrs or inheritAttrs: false
└── Pinia error: "No active Pinia" → call setActivePinia(createPinia()) in test setup
```

### Common to Both

```
Network / API
├── CORS error → check CORSMiddleware allowed_origins on FastAPI
├── 504 Gateway Timeout → query too slow, check for missing index or N+1
└── Connection refused → service not running, check port

Flaky test
├── Shared mutable state → reset in beforeEach / autouse fixture
├── Time-dependent → freeze time (freezegun / vi.useFakeTimers)
└── DB state leakage → rollback in fixture teardown
```

---

## Debugging Tools

### Python / FastAPI

```bash
# Verbose test output with print statements
pytest -k "test_name" -v -s

# Drop into debugger on failure
pytest --pdb

# Inline breakpoint
breakpoint()   # equivalent to import pdb; pdb.set_trace()

# Check Alembic migration state
alembic current
alembic history --verbose

# Check structlog output (pretty print in dev)
LOG_LEVEL=debug uvicorn main:app --reload
```

### JavaScript / Vue

```bash
# Debug Vitest tests
node --inspect-brk node_modules/.bin/vitest

# Verbose build output
npx vite build --debug

# Remove all debug logs before commit
git diff | grep "console.log"
```

### Git Bisect

```bash
git bisect start
git bisect bad                   # current commit is broken
git bisect good <commit-sha>     # this commit was working
# test each commit git suggests, then:
git bisect good   # or   git bisect bad
git bisect reset  # done
```

---

## Common Rationalizations (Avoid)

| Excuse                | Reality                          |
| --------------------- | -------------------------------- |
| "Works on my machine" | Environment differences are bugs |
| "It's just flaky"     | Flaky tests have root causes     |
| "Let's just retry"    | Retries hide real problems       |
| "Third-party issue"   | Still need to handle gracefully  |
| "Fix it later"        | Tech debt compounds              |

---

## Output

- Root cause identified and fixed (not symptom-patched)
- Regression test added and passing
- All tests passing (`pytest --cov-fail-under=80`, `mypy`, `tsc --noEmit`)
- Commit message explains the root cause

## Next Step

After fixing → continue with `/build` or run `/review` for verification.
