---
name: spec
description: Spec before code — structured PRD creation for new features
---

# /spec — Specification-Driven Development

> "Plan the work, then work the plan."

## Purpose

Create a specification document **before** writing any code. Ensures alignment on requirements, constraints, and acceptance criteria.

## Workflow

### Phase 1: Discovery (Ask Questions)

Gather requirements before generating the spec:

**Scope**

- What is the objective? What problem does this solve?
- Who are the target users?
- Which layer does this touch? Backend (FastAPI) / Frontend (Vue 3) / Both?

**Features**

- What are the core features (MVP)?
- What is the acceptance criteria for each?
- What is explicitly out of scope?

**Technical**

- Integration points with existing systems?
- New DB tables / columns needed?
- New API endpoints needed?
- Performance or security constraints?

### Phase 2: Generate Specification

After discovery, produce the spec with this template:

```markdown
# Feature: [Name]

## Objective

[1-2 sentences describing the goal]

## Target Users

[Who will use this and why]

## Layer

- [ ] Backend only (FastAPI)
- [ ] Frontend only (Vue 3)
- [ ] Full-stack (FastAPI + Vue 3)

## Core Features

| #   | Feature     | Acceptance Criteria      |
| --- | ----------- | ------------------------ |
| 1   | [Feature A] | [What "done" looks like] |
| 2   | [Feature B] | [What "done" looks like] |

## Out of Scope

- [What we're NOT building in this iteration]

## Technical Approach

### Backend (FastAPI)

- New endpoints: `POST /api/v1/...`, `GET /api/v1/...`
- Pydantic schemas: `[RequestSchema]`, `[ResponseSchema]`
- New DB models / Alembic migration needed? Yes / No
- Services/repositories affected: `domain/services/...`

### Frontend (Vue 3)

- New pages/components: `views/...`, `features/.../components/...`
- State: Pinia store / TanStack Query / local ref
- API calls: via `apiClient` → which endpoint

### API Contract
```

POST /api/v1/[resource]
Authorization: Bearer <token>

Request:
{
"field": "value"
}

Response 201:
{
"success": true,
"data": { "id": "...", ... }
}

Errors: 400, 401, 422

```

## Mandatory Standards
- Rules: `.claude/rules/` — all mandatory
- API format: `api-conventions.md` (camelCase fields, success envelope)
- DB patterns: `database.md` (SQLAlchemy async, transactions)
- Security: `security.md` — **CRITICAL**

## Testing Strategy
- Unit: `domain/services/` logic
- Integration: API endpoints via `pytest + httpx`
- Component: Vue components via `Vitest + Vue Testing Library`
- E2E: critical user flows via Playwright
- Coverage target: ≥ 80%

## Boundaries

### Always Do
- [Non-negotiables]

### Ask First
- [Decisions requiring approval before implementation]

### Never Do
- [Hard constraints]
```

### Phase 3: Review & Confirm

- Present spec to user
- Confirm all sections before proceeding to `/plan`
- Save as `docs/specs/[feature-name].md`

## Output

- `docs/specs/[feature-name].md` — approved specification
- Clear alignment on what to build, which layer, API contracts

## Next Step

After spec approved → run `/plan` to decompose into tasks.
