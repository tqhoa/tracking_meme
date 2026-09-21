---
name: plan
description: Decompose specs into small, verifiable tasks with dependency ordering
---

# /plan — Planning & Task Breakdown

> "Vertical slices, not horizontal layers."

## Purpose

Transform a specification into an ordered list of small, verifiable tasks. Each task delivers end-to-end functionality through all required layers.

## Prerequisites

- Approved spec exists at `docs/specs/[feature-name].md`
- Understanding of the codebase structure

## Workflow

### Phase 1: Analysis (Read-Only)

1. **Read the spec** — Understand objectives, layer, and acceptance criteria
2. **Survey the codebase** — Identify relevant files, patterns, integration points
3. **Map dependencies** — Which components depend on which?

> **Do NOT modify code during planning.**

### Phase 2: Vertical Slicing

Break work into **vertical slices** — each slice delivers complete functionality through all required layers:

```
❌ Horizontal (anti-pattern):
   Task 1: Create all DB models
   Task 2: Create all API routes
   Task 3: Create all UI components

✅ Vertical (correct):
   Task 1: User can create a task (DB + API + UI)
   Task 2: User can view task list (DB + API + UI)
   Task 3: User can mark task complete (DB + API + UI)
```

Backend-only features slice by endpoint. Frontend-only features slice by user interaction.

### Phase 3: Task Definition

Each task must include:

```markdown
## Task [N]: [Short description]

**Layer**: Backend (FastAPI) / Frontend (Vue 3) / Full-stack

**Objective**: [What this achieves end-to-end]

**Files to modify**:

- `domain/repositories/task_repository.py`
- `api/v1/tasks.py`
- `features/tasks/components/TaskList.vue`

**Test first** (TDD):

- Write failing test in `tests/unit/` or `tests/integration/`
- Implement until test passes
- Refactor

**Acceptance Criteria**:

- [ ] User can [action]
- [ ] [Validation] is enforced
- [ ] Unit/integration test covers [scenario]
- [ ] Coverage ≥ 80%

**Dependencies**: [Task IDs this depends on, or "none"]
```

### Phase 4: Ordering

Order tasks by:

1. **Foundation first** — DB models/migrations, Pydantic schemas, shared utilities
2. **Risk-first** — Tackle uncertain/complex items early
3. **Dependencies** — Respect the dependency graph
4. **Quick wins** — Early momentum with simpler tasks

### Phase 5: Checkpoints

Insert checkpoints between major phases:

```markdown
---
## Checkpoint: [Phase Name] Complete

**Verify before proceeding**:
- [ ] All acceptance criteria met
- [ ] Test coverage ≥ 80% (`pytest --cov=. --cov-fail-under=80`)
- [ ] `alembic upgrade head` runs cleanly (if migrations added)
- [ ] No type errors (`mypy` / `tsc --noEmit`)
- [ ] API contracts match `api-conventions.md`

---
```

## Output

Save to `docs/plans/[feature-name].md`:

```markdown
# Plan: [Feature Name]

**Spec**: `docs/specs/[feature-name].md`
**Layer**: Backend / Frontend / Full-stack

## Phase 1: Foundation

- [ ] Task 1.1: [Description] — `[files affected]`
- [ ] Task 1.2: [Description] — `[files affected]`

## Checkpoint: Foundation Complete

## Phase 2: Core Features

- [ ] Task 2.1: [Description] — `[files affected]`
- [ ] Task 2.2: [Description] — `[files affected]`

## Checkpoint: Core Complete

## Phase 3: Polish & Tests

- [ ] Task 3.1: [Description]
- [ ] Task 3.2: Coverage audit — ensure ≥ 80%
```

## Next Step

After plan approved → run `/build` to implement tasks incrementally (TDD: RED → GREEN → REFACTOR).
