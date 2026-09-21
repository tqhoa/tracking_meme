---
name: security-review
description: Skill to perform a thorough security audit of the codebase
---

# Security Review Skill

## Purpose

Systematically scan the codebase for security vulnerabilities and produce a prioritized report.

---

## Checklist

### CRITICAL (Check First)

- [ ] Hardcoded secrets, API keys, passwords in source files
  ```bash
  grep -rn --include="*.py" --include="*.ts" --include="*.js" \
    -E "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}" src/
  ```
- [ ] `.env` files accidentally committed
  ```bash
  git log --all --full-history -- .env
  ```
- [ ] SQL injection via raw string concatenation (not using ORM)
- [ ] `eval()` or `new Function()` with user input (JS)
- [ ] Python `exec()` or `eval()` with user input

---

### HIGH

- [ ] Missing authentication on protected routes
- [ ] Missing authorization — any authenticated user can access any resource
- [ ] Resource ownership not verified (user can modify other users' data)
- [ ] Passwords stored in plain text (must use bcrypt, rounds ≥ 12)
- [ ] JWT secrets too short or exposed in source
- [ ] No rate limiting on auth endpoints
- [ ] Missing input validation (no Pydantic schemas / Zod schemas at boundary)

---

### MEDIUM

- [ ] Missing security headers (`Helmet` not applied / FastAPI middleware missing)
- [ ] CORS configured too broadly (`origins=["*"]` in production)
- [ ] Dependencies with known vulnerabilities

  ```bash
  # JavaScript
  npm audit --audit-level=moderate

  # Python
  pip-audit
  ```

- [ ] Sensitive data in logs (PII, tokens, passwords)
- [ ] Missing HTTPS enforcement

---

### LOW

- [ ] Error messages revealing stack traces to the client
- [ ] Missing CSP headers
- [ ] Cookie security flags missing (`HttpOnly`, `Secure`, `SameSite`)
- [ ] `v-html` used without sanitization (Vue — XSS risk)

---

## Stack-Specific Checks

### FastAPI / Python

- [ ] All request bodies use Pydantic models (not raw `dict`)
- [ ] All DB queries use SQLAlchemy ORM (no `text()` with user input)
- [ ] `@app.exception_handler(Exception)` does not leak internal details
- [ ] Secrets loaded via `pydantic-settings` from env, not hardcoded
- [ ] `python-jose` / `passlib` used correctly for JWT and password hashing

### Vue 3 / TypeScript

- [ ] `v-html` not used, or input is sanitized with `DOMPurify` before binding
- [ ] `localStorage` not used for JWT tokens (prefer `httpOnly` cookies)
- [ ] API calls use the centralized `apiClient` (not raw `fetch`)
- [ ] Auth guard applied to all protected routes in Vue Router

---

## Commands

```bash
# Check for secrets in Python + JS/TS source
grep -rn --include="*.py" --include="*.ts" --include="*.js" \
  -E "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}" src/

# Check .env history
git log --all --full-history -- .env

# Dependency audit — JavaScript
npm audit --audit-level=moderate

# Dependency audit — Python
pip-audit

# Check for v-html usage
grep -rn "v-html" src/

# Check for eval/exec usage
grep -rn "eval\|exec(" src/
```

---

## Output Format

```
path/to/file.py:42: CRITICAL: Hardcoded API key. Move to environment variable.
api/v1/users.py:88: HIGH: Missing authorization — any user can delete any resource. Add ownership check.
main.py:15: MEDIUM: CORS allows all origins in production. Restrict to allowed domains.
frontend/src/views/Post.vue:67: LOW: v-html binds unsanitized user input. Sanitize with DOMPurify.
```

Report structure:

```markdown
# Security Review Report — [Date]

## CRITICAL

[file:line references with description and fix]

## HIGH

[file:line references with description and fix]

## MEDIUM

[file:line references with description and fix]

## LOW

[file:line references with description and fix]

## Recommendations

[Prioritized action items]
```
