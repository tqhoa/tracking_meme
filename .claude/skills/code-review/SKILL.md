---
name: Code Review & Quality
description: Five-axis code review for comprehensive quality assessment
---

# Code Review & Quality Skill

## Philosophy

> "Approve a change when it definitely improves overall code health, even if it isn't perfect."

Progress over perfection. Continuous incremental improvement.

---

## Five-Axis Review Framework

### Axis 1: Correctness

**Questions to ask:**

- Does the implementation match the specification?
- Are edge cases handled?
- Are error paths covered?
- Are there potential runtime issues?
  - Off-by-one errors
  - Race conditions
  - Null/undefined access
  - Resource leaks

**Test adequacy:**

- Do tests verify the claimed behavior?
- Are negative cases tested?
- Would a bug slip through?

---

### Axis 2: Readability & Simplicity

**Questions to ask:**

- Can another engineer understand this without explanation?
- Are names clear and descriptive?
- Is control flow straightforward?
- Is the code organized logically?

**Complexity checks:**

- Deep nesting (> 3 levels)?
- Long functions (> 30 lines)?
- Clever tricks that obscure intent?
- Unnecessary abstractions?

---

### Axis 3: Architecture

**Questions to ask:**

- Does this follow existing patterns in the codebase?
- Are module boundaries respected?
- Is there code duplication that should be extracted?
- Is the abstraction level appropriate?
- Do dependencies flow in the right direction?

**Over-engineering checks:**

- Is this simpler than it needs to be?
- Are there abstractions "for future use"?
- Would a simpler approach work?

---

### Axis 4: Security

**Input validation:**

- Is user input validated with Pydantic / Zod schemas?
- Are ORM queries used (no raw SQL string concatenation)?
- Is `v-html` avoided or sanitized?
- Is output properly encoded?

**Authentication & Authorization:**

- Are auth checks in place on every protected route?
- Is resource ownership verified?
- Are permissions enforced?

**Secrets management:**

- No hardcoded secrets?
- Sensitive data excluded from logs?
- External data treated as untrusted?

---

### Axis 5: Performance

**Common issues:**

- N+1 query patterns? (use `selectinload` / Prisma `include`)
- Unbounded operations (loops, queries without pagination)?
- Missing indexes for frequently queried columns?
- Unnecessary watchers or computed re-runs (Vue)?
- Objects created in hot paths?

**Async handling:**

- Are async operations properly awaited?
- Could independent operations be parallelized with `asyncio.gather` / `Promise.all`?

---

## Change Sizing Guidelines

| Size           | Lines | Guidance                  |
| -------------- | ----- | ------------------------- |
| **Ideal**      | ~100  | Easy to review thoroughly |
| **Acceptable** | ~300  | Requires focused review   |
| **Too Large**  | 1000+ | Split into smaller PRs    |

Each PR should be **one logical change**, not an entire feature.

---

## Severity Labels

| Severity   | Meaning                                         | Action                |
| ---------- | ----------------------------------------------- | --------------------- |
| `CRITICAL` | Security flaw, data loss, broken auth           | Must fix before merge |
| `HIGH`     | Bug, incorrect behavior, missing error handling | Must fix before merge |
| `MEDIUM`   | Readability, architecture, test coverage        | Should fix            |
| `LOW`      | Style, naming, minor improvement                | Author's choice       |

**Output format:**

```
path/to/file.py:42: CRITICAL: SQL injection via string concatenation. Use ORM parameterized queries.
api/v1/users.py:88: HIGH: Missing authorization check — any authenticated user can delete any resource.
domain/services/order_service.py:31: MEDIUM: Function exceeds 30 lines. Extract validation into `_validate_order`.
schemas/user.py:14: LOW: Rename `d` to `data` for clarity.
```

---

## Review Process

### Step 1: Understand Context

- What is this PR trying to achieve?
- Is there a linked issue or spec?
- What's the scope of changes?

### Step 2: Review Tests First

Tests reveal:

- What behavior is expected
- What edge cases are considered
- Whether coverage is adequate

### Step 3: Examine Implementation

Walk through changes with the 5 axes in mind.

### Step 4: Provide Actionable Feedback

```
❌ "This is confusing"

✅ "This nested conditional is hard to follow. Extract the inner logic
    to a named function like `is_eligible_for_discount()`."
```

---

## Review Output Format

```markdown
## Review: [PR Title]

### Summary

[1-2 sentences on overall assessment]

### Findings

path/to/file:line: CRITICAL: [issue]. [fix].
path/to/file:line: HIGH: [issue]. [fix].
path/to/file:line: MEDIUM: [issue]. [fix].
path/to/file:line: LOW: [suggestion].

### Verdict

**REQUEST CHANGES** — [N critical/high issues must be resolved]
```

If no CRITICAL or HIGH issues:

```markdown
### Verdict

**APPROVE** — [Optional: one sentence on what to watch]
```

---

## Rules

- **Don't accept "I'll clean it up later"** — It won't happen
- **Remove dead code** — Don't comment it out
- **Be kind, not nice** — Honest feedback helps everyone
- **One approval minimum** — Before any merge
