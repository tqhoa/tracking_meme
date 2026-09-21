---
name: deploy
description: Skill to automate the full deployment process including build, test, and release steps
---

# Deploy Skill

## Purpose

Automate the deployment pipeline: test → migrate → deploy → verify.

## Prerequisites

- All tests passing locally
- Environment variables configured on target
- Access to deployment target (Railway/Fly.io for backend, Vercel for frontend)

---

## Steps

### 1. Verify Clean State

```bash
git status
git pull origin main
```

### 2. Run Tests

**Backend (FastAPI / Python):**

```bash
pytest --cov=. --cov-fail-under=80
```

**Frontend (Vue / Vitest):**

```bash
npm run test:run && npm run build
```

If tests fail → **STOP**. Fix failures before proceeding.

### 3. Run Database Migrations

```bash
alembic upgrade head
```

Verify migration applied:

```bash
alembic current
```

### 4. Deploy

**Backend (Railway):**

```bash
railway up
```

**Backend (Fly.io):**

```bash
fly deploy
```

**Frontend (Vercel):**

```bash
vercel --prod
```

**Docker Compose (self-hosted VPS):**

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --remove-orphans
docker image prune -f
```

### 5. Health Check

```bash
curl -f https://api.example.com/health || echo "Health check failed"
```

Expected response:

```json
{
  "status": "healthy",
  "version": "v1.2.0",
  "checks": { "database": "ok", "redis": "ok" }
}
```

### 6. Tail Logs (first 30 seconds)

```bash
# Railway
railway logs

# Fly.io
fly logs

# Docker
docker compose logs --tail=50 -f backend
```

---

## Rollback

**Railway:**

```bash
railway rollback
```

**Fly.io:**

```bash
fly deploy --image registry.fly.io/app-name:<previous-version>
```

**Vercel:**

```bash
vercel rollback
```

**Docker Compose (VPS):**

```bash
export TAG=v1.1.9
docker compose up -d
```

**Database migration rollback:**

```bash
alembic downgrade -1
```

---

## Success Criteria

- Health endpoint returns 200
- No error logs in initial 30 seconds
- All smoke tests pass
- Alembic shows correct current revision

---

## Red Flags — Stop and Investigate

- Health check returns non-200 after deploy
- Error rate spikes in first 5 minutes
- Migration failed or rolled back
- Memory/CPU usage above normal baseline
