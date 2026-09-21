# Deployment Workflow

> Quy trình CI/CD hoàn chỉnh từ development đến production.

---

## Architecture Overview

```
┌─────────────┐     push      ┌──────────────────────────────────────────────────────────┐
│   LOCAL     │ ────────────► │                      GITHUB                              │
│             │               │                                                          │
│ Dev         │               │  dev branch                                              │
│ Claude Code │               │      │                                                   │
│ + IDE       │               │      ▼ PR (dev → main)                                   │
│             │               │  ┌─────────────────┐                                     │
└─────────────┘               │  │ ci.yml — PR gate│                                     │
                              │  │ ✅ Test Backend  │                                     │
                              │  │ ✅ Test Frontend │                                     │
                              │  └────────┬────────┘                                     │
                              │           │ must pass                                    │
                              │           ▼                                              │
                              │  ┌─────────────────────┐                                 │
                              │  │ Branch Protection   │                                 │
                              │  │ ✅ Require PR        │                                 │
                              │  │ ✅ CI must pass      │                                 │
                              │  │ ✅ No force push     │                                 │
                              │  │ ✅ Enforce admins    │                                 │
                              │  └────────┬────────────┘                                 │
                              │           │ merge                                        │
                              │           ▼                                              │
                              │      main branch ──────────────────────────────────────► │
                              └──────────────────────────────────────────────────────────┘
                                                                      │
                              ┌───────────────────────────────────────┘
                              ▼
                    ┌─────────────────────────────────┐
                    │  deploy.yml — triggers on main  │
                    │                                 │
                    │  ① Version: v1.2.0 (auto)       │  ✅
                    │  ② Test Backend (pytest)        │  ✅
                    │  ③ Test Frontend (vitest)       │  ✅
                    │  ④ Build Backend → GHCR         │  ✅
                    │  ⑤ Build Frontend → GHCR        │  ✅
                    │  ⑥ Git Tag v1.2.0               │  ✅
                    │  ⑦ Deploy VPS (pull + up)       │  ✅
                    │  ⑧ Notify                       │  ✅
                    └─────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼ push images     │                 ▼ git tag
┌───────────────────────────────────────────────────────────────────────────────┐
│                            GHCR REGISTRY                                      │
│                                                                               │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │ myapp-backend                       │  │ myapp-frontend                  │ │
│  │ v1.2.0 ✅   v1.1.9   v1.1.8  latest │  │ v1.2.0 ✅   v1.1.9   v1.1.8    │ │
│  └─────────────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                               │
│  Rollback (30s): TAG=v1.1.9 docker compose up -d                              │
└───────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ docker pull v1.2.0
┌───────────────────────────────────────────────────────────────────────────────┐
│                                 VPS                                           │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ Nginx (SSL)                                                             │  │
│  │ api.example.com → :8000    app.example.com → :3000                      │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ Docker Containers                                                       │  │
│  │ myapp-backend:v1.2.0 ✅   myapp-worker:v1.2.0 ✅                         │  │
│  │ myapp-frontend:v1.2.0 ✅  postgres:15 ✅   redis:7 ✅                     │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Local Development

### Setup

```bash
# Clone repository
git clone git@github.com:org/project.git
cd project

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload

# Frontend setup
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Development Flow

1. Checkout từ `main` hoặc `dev` branch
2. Tạo feature branch: `feature/add-user-auth`
3. Code + test locally
4. Push lên GitHub

```bash
git checkout -b feature/add-user-auth
# ... coding ...
git add backend/api/v1/auth.py backend/tests/integration/routes/test_auth.py
git commit -m "feat(auth): add JWT authentication"
git push origin feature/add-user-auth
```

---

## 2. GitHub CI/CD

### 2.1 Branch Strategy

| Branch      | Purpose            | Protection            |
| ----------- | ------------------ | --------------------- |
| `main`      | Production code    | Full protection       |
| `dev`       | Integration branch | PR required           |
| `feature/*` | New features       | None                  |
| `fix/*`     | Bug fixes          | None                  |
| `hotfix/*`  | Urgent fixes       | Direct to main via PR |

### 2.2 Branch Protection Rules (main)

```yaml
# Settings → Branches → Branch protection rules

✅ Require a pull request before merging
✅ Require approvals (1+)
✅ Dismiss stale pull request approvals when new commits are pushed

✅ Require status checks to pass before merging
✅ Require branches to be up to date before merging
- test-backend (required)
- test-frontend (required)

✅ Do not allow force pushes

✅ Do not allow deletions

✅ Include administrators
```

### 2.3 CI Workflow (ci.yml)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, dev]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        run: pip install -r requirements.txt
        working-directory: backend

      - name: Run linter
        run: ruff check .
        working-directory: backend

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost/test_db
        run: pytest --cov=. --cov-fail-under=80 --cov-report=xml
        working-directory: backend

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: frontend

      - name: Run linter
        run: npm run lint
        working-directory: frontend

      - name: Run tests
        run: npm run test:run
        working-directory: frontend

      - name: Build check
        run: npm run build
        working-directory: frontend
```

### 2.4 Deploy Workflow (deploy.yml)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: ghcr.io/${{ github.repository }}/myapp-backend
  FRONTEND_IMAGE: ghcr.io/${{ github.repository }}/myapp-frontend

jobs:
  # ① Auto Version
  version:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get next version
        id: version
        run: |
          LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
          VERSION=$(echo $LATEST_TAG | awk -F. '{print $1"."$2"."$3+1}')
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Version: $VERSION"

  # ② Test Backend
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
          cache-dependency-path: backend/requirements.txt
      - run: pip install -r requirements.txt
        working-directory: backend
      - run: pytest --cov=. --cov-fail-under=80
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost/test_db
        working-directory: backend

  # ③ Test Frontend
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
        working-directory: frontend
      - run: npm run test:run && npm run build
        working-directory: frontend

  # ④ Build Backend → GHCR
  build-backend:
    needs: [version, test-backend]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ env.BACKEND_IMAGE }}:${{ needs.version.outputs.version }}
            ${{ env.BACKEND_IMAGE }}:latest
          cache-from: type=registry,ref=${{ env.BACKEND_IMAGE }}:buildcache
          cache-to: type=registry,ref=${{ env.BACKEND_IMAGE }}:buildcache,mode=max

  # ⑤ Build Frontend → GHCR
  build-frontend:
    needs: [version, test-frontend]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ env.FRONTEND_IMAGE }}:${{ needs.version.outputs.version }}
            ${{ env.FRONTEND_IMAGE }}:latest
          build-args: |
            VITE_API_BASE_URL=${{ vars.VITE_API_BASE_URL }}
          cache-from: type=registry,ref=${{ env.FRONTEND_IMAGE }}:buildcache
          cache-to: type=registry,ref=${{ env.FRONTEND_IMAGE }}:buildcache,mode=max

  # ⑥ Git Tag
  tag:
    needs: [version, build-backend, build-frontend]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Create and push tag
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git tag -a ${{ needs.version.outputs.version }} -m "Release ${{ needs.version.outputs.version }}"
          git push origin ${{ needs.version.outputs.version }}

  # ⑦ Deploy VPS
  deploy:
    needs: [version, build-backend, build-frontend, tag]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/app

            # Login to GHCR
            echo ${{ secrets.GHCR_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin

            # Pull new images
            export TAG=${{ needs.version.outputs.version }}
            docker compose pull

            # Run database migrations
            docker compose run --rm backend alembic upgrade head

            # Deploy with zero-downtime
            docker compose up -d --remove-orphans

            # Cleanup old images
            docker image prune -f

            # Health check
            sleep 10
            curl -f http://localhost:8000/health || exit 1

  # ⑧ Notify
  notify:
    needs: [version, deploy]
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Send notification
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          format: markdown
          message: |
            ${{ needs.deploy.result == 'success' && '✅' || '❌' }} *Deploy ${{ needs.version.outputs.version }}*

            Repository: `${{ github.repository }}`
            Branch: `${{ github.ref_name }}`
            Commit: `${{ github.sha }}`

            Status: *${{ needs.deploy.result }}*

            [View Action](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
```

---

## 3. GHCR Registry

### Image Naming Convention

```
ghcr.io/{owner}/{repo}/{service}:{version}

# Examples
ghcr.io/myorg/myproject/myapp-backend:v1.2.0
ghcr.io/myorg/myproject/myapp-frontend:v1.2.0
ghcr.io/myorg/myproject/myapp-worker:v1.2.0
```

### Image Tags

| Tag      | Description                  |
| -------- | ---------------------------- |
| `v1.2.0` | Specific version (immutable) |
| `latest` | Latest stable release        |

### Manual Rollback (30 seconds)

```bash
# SSH vào VPS
ssh user@vps
cd /opt/app

# Rollback to previous version
export TAG=v1.1.9
docker compose up -d

# Verify rollback
docker ps
curl http://localhost:8000/health
```

---

## 4. VPS Infrastructure

### 4.1 Directory Structure

```
/opt/app/
├── docker-compose.yml
├── .env
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       ├── backend.conf
│       └── frontend.conf
├── data/
│   ├── postgres/
│   └── redis/
└── logs/
```

### 4.2 Docker Compose

```yaml
# docker-compose.yml
services:
  backend:
    image: ghcr.io/myorg/myproject/myapp-backend:${TAG:-latest}
    container_name: myapp-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

  worker:
    image: ghcr.io/myorg/myproject/myapp-backend:${TAG:-latest}
    container_name: myapp-worker
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - backend
      - redis
    command: ["celery", "-A", "jobs.celery_app", "worker", "--loglevel=info"]

  frontend:
    image: ghcr.io/myorg/myproject/myapp-frontend:${TAG:-latest}
    container_name: myapp-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"

  postgres:
    image: postgres:15
    container_name: postgres
    restart: unless-stopped
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    container_name: redis
    restart: unless-stopped
    volumes:
      - ./data/redis:/data
    command: ["redis-server", "--appendonly", "yes"]
```

### 4.3 Nginx Configuration

```nginx
# /etc/nginx/conf.d/backend.conf
upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 4.4 Port Mapping

| Domain          | Internal Port | Service         |
| --------------- | ------------- | --------------- |
| api.example.com | :8000         | FastAPI Backend |
| app.example.com | :3000         | Vue Frontend    |

---

## 5. Monitoring & Health Checks

### Health Endpoint

```bash
curl https://api.example.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "v1.2.0",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

### Docker Health Monitoring

```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check logs
docker logs -f myapp-backend --tail 100

# Resource usage
docker stats
```

### Useful Commands

```bash
# View deployment logs
docker compose logs -f

# Restart specific service
docker compose restart backend

# Scale workers
docker compose up -d --scale worker=3

# Enter container
docker exec -it myapp-backend sh

# Check migration status
docker compose run --rm backend alembic current
```

---

## 6. Troubleshooting

### Deploy Failed

```bash
# 1. Check GitHub Actions logs
# 2. SSH to VPS and check manually
ssh user@vps
cd /opt/app
docker compose logs backend --tail 50

# 3. Manual deploy
docker compose pull
docker compose up -d
```

### Rollback Steps

```bash
# 1. Find previous working version
git tag -l | tail -5

# 2. Deploy previous version
export TAG=v1.1.9
docker compose up -d

# 3. Verify
curl https://api.example.com/health
```

### Database Migration Failed

```bash
# 1. Check migration status
docker compose run --rm backend alembic current

# 2. Check migration history
docker compose run --rm backend alembic history

# 3. Manual rollback one step
docker compose run --rm backend alembic downgrade -1

# 4. Manual deploy with specific revision
docker compose run --rm backend alembic upgrade <revision>
```

---

## 7. Security Checklist

- [ ] SSH key authentication only (no password)
- [ ] Firewall configured (ufw/iptables)
- [ ] SSL certificates auto-renewed (certbot)
- [ ] Docker socket not exposed
- [ ] Environment variables secured (not in image)
- [ ] GHCR token stored in GitHub Secrets
- [ ] Database backups automated
- [ ] Logs rotated and monitored
