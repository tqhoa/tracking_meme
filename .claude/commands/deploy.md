---
name: deploy
description: Build, test, migrate, and deploy — staged rollout with verification
---

# /deploy — Deployment Pipeline

> "Ship reliably. Verify before and after."

## Purpose

Deploy the application to a target environment with pre-deploy checks, migration, deployment, and post-deploy verification. Never skip steps.

## Environments

| Environment | Backend                        | Frontend          |
| ----------- | ------------------------------ | ----------------- |
| Local       | `uvicorn main:app --reload`    | `npm run dev`     |
| Staging     | Railway / Fly.io (staging app) | Vercel preview    |
| Production  | Railway / Fly.io (production)  | Vercel production |

---

## Pre-Deploy Checklist

Run before deploying to **any** environment:

```bash
# Backend — all tests pass
pytest --cov=. --cov-fail-under=80

# Frontend — all tests pass
npm run test:run

# Backend — no linting errors
ruff check . && mypy .

# Frontend — no type errors
tsc --noEmit

# Check for secrets that shouldn't be committed
git diff --staged | grep -iE "(password|secret|token|api_key)" || echo "clean"
```

- [ ] All tests passing (≥ 80% coverage)
- [ ] No linting or type errors
- [ ] `.env` files not committed
- [ ] Migrations ready (`alembic upgrade head` tested locally)
- [ ] `CHANGELOG` or PR description updated

---

## Deployment Steps

### 1. Run Migrations First

**Always migrate before deploying new code.**

```bash
# Staging
alembic upgrade head

# Production (via CI or manually)
alembic upgrade head

# Verify applied
alembic current
```

### 2. Deploy Backend

```bash
# Railway
railway up --environment staging
railway up --environment production

# Fly.io
fly deploy --app myapp-staging
fly deploy --app myapp-production

# Docker (manual)
docker build -t myapp:$(git rev-parse --short HEAD) .
docker push registry/myapp:$(git rev-parse --short HEAD)
```

### 3. Deploy Frontend

```bash
# Vercel (auto-deploys from git push)
git push origin master

# Manual Vercel deploy
vercel --prod

# Build locally to verify before push
npm run build
```

---

## Post-Deploy Verification

Run after every deployment:

```bash
# Health check
curl https://api.myapp.com/health

# Verify API is responding
curl -H "Authorization: Bearer $TEST_TOKEN" https://api.myapp.com/api/v1/users/me
```

- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] No error spikes in logs (check Grafana / Railway logs)
- [ ] Smoke test critical paths: auth, core feature, payment (if applicable)
- [ ] Database connections healthy (check pool metrics)

---

## Rollback

If deployment fails or post-deploy verification shows errors:

### Backend Rollback

```bash
# Railway — redeploy previous deployment from dashboard
# or via CLI:
railway rollback

# Fly.io
fly releases list --app myapp-production
fly deploy --image registry/myapp:<previous-sha>

# Database rollback (only if migration is reversible)
alembic downgrade -1
```

### Frontend Rollback

```bash
# Vercel — instant rollback from dashboard or:
vercel rollback
```

---

## Staged Rollout Rules

| Change Type     | Deploy To            | Verify          | Then         |
| --------------- | -------------------- | --------------- | ------------ |
| Bug fix         | Staging → Production | Health + smoke  | Same day     |
| New feature     | Staging (24h soak)   | Full test suite | Next day     |
| DB migration    | Staging first        | Verify data     | Then prod    |
| Breaking change | Staging → 10% prod   | Monitor errors  | Full rollout |

---

## Red Flags — Stop Deployment

- Tests failing → fix before deploying, no exceptions
- Migration not tested on staging → test first
- Deploying during peak hours → schedule off-peak
- No rollback plan for breaking DB migration → write one first

---

## Next Step

After successful deployment, tag the release:

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```
