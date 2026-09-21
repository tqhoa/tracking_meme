# Project Structure

## Environment Files (all stacks)

- `.env` — Local development (gitignored)
- `.env.example` — Template committed to git
- `.env.test` — Test environment (gitignored)
- `.env.production` — Set in CI/CD, never committed

---

## JavaScript / Node.js (Express)

### Folder Layout

```
project-root/
├── .claude/                    # AI Agent configuration
│   ├── agents/
│   ├── commands/
│   ├── rules/
│   ├── skills/
│   ├── settings.json
│   └── CLAUDE.md
│
├── src/
│   ├── config/                 # App configuration
│   ├── controllers/            # Route handlers (thin layer)
│   ├── middleware/             # Express middleware
│   ├── models/                 # Database models/schemas
│   ├── repositories/           # Data access layer
│   ├── routes/                 # Route definitions
│   ├── services/               # Business logic layer
│   ├── utils/                  # Utility functions
│   └── index.js                # Entry point
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── api/
│   └── architecture/
│
├── scripts/
├── .env.example
├── package.json
└── README.md
```

### Layered Architecture

```
Request → Routes → Middleware → Controllers → Services → Repositories → Database
```

- **Routes**: URL mapping only, no logic
- **Controllers**: Request/response handling, input validation
- **Services**: Business logic, orchestration
- **Repositories**: Data access, queries
- **Models**: Data schemas and types

### File Naming

- Source files: `kebab-case.js` (`user-service.js`)
- Test files: `[name].test.js` (`user-service.test.js`)
- Config files: `kebab-case.js` or `kebab-case.json`

---

## Python / FastAPI

### Folder Layout

```
project-root/
├── .claude/                    # AI Agent configuration
│
├── api/                        # Presentation layer
│   ├── v1/                     # Versioned routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── orders.py
│   ├── dependencies/           # FastAPI Depends
│   │   ├── auth.py
│   │   └── pagination.py
│   └── middleware/
│       ├── logging.py
│       └── rate_limit.py
│
├── domain/                     # Business logic layer
│   ├── services/
│   │   ├── user_service.py
│   │   └── order_service.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── order_repository.py
│   └── events/
│
├── infrastructure/             # External services
│   ├── database/
│   │   ├── models/             # SQLAlchemy models
│   │   ├── session.py
│   │   └── migrations/         # Alembic versions
│   ├── cache/
│   │   ├── client.py
│   │   └── keys.py
│   ├── queue/
│   │   ├── celery_app.py
│   │   └── tasks/
│   ├── storage/
│   └── email/
│
├── schemas/                    # Pydantic request/response
│   ├── user.py
│   ├── auth.py
│   ├── order.py
│   └── common.py               # ApiResponse, PaginatedResponse
│
├── shared/                     # Cross-cutting concerns
│   ├── config.py               # pydantic-settings
│   ├── exceptions.py           # AppError
│   ├── helpers/
│   │   ├── hash.py
│   │   └── jwt.py
│   └── utils/
│       ├── logger.py
│       └── pagination.py
│
├── jobs/                       # Scheduled jobs (Celery Beat)
├── tests/
│   ├── unit/services/
│   ├── integration/routes/
│   └── conftest.py
│
├── docs/
│   ├── api/
│   └── architecture/
│
├── main.py                     # FastAPI app + lifespan
├── alembic.ini
├── pyproject.toml
├── .env.example
└── README.md
```

### Layered Architecture

```
Request → Router → Dependency → Endpoint → Service → Repository → Database
                       ↓
               (auth, validation, rate-limit)
```

- **api/**: HTTP only — no business logic
- **domain/services/**: Business rules and orchestration
- **domain/repositories/**: Data access — all DB queries here
- **infrastructure/**: External systems (DB session, cache, queue)
- **schemas/**: Pydantic models for request/response
- **shared/**: Config, exceptions, helpers used across layers

### Import Direction (never reverse)

```
api/ → domain/ → infrastructure/
all layers → shared/
```

### File Naming

- Source files: `snake_case.py` (`user_service.py`)
- Test files: `test_[name].py` (`test_user_service.py`)
- Packages: `snake_case/` (no hyphens in folder names)
