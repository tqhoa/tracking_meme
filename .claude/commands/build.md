---
name: build
description: Implement tasks incrementally using TDD and vertical slices
---

# /build — Incremental Implementation

> "The simplest thing that could work."

## Purpose

Implement tasks one at a time using Test-Driven Development. Each increment leaves the system in a working, testable state.

## Prerequisites

- Plan exists at `docs/plans/[feature-name].md`
- Task acceptance criteria are understood

## Workflow

### For Each Task

#### Step 1: Load Context

```
1. Read the task's acceptance criteria and layer (Backend / Frontend / Full-stack)
2. Identify relevant existing code and patterns
3. Understand schemas, types, and integration points involved
```

#### Step 2: RED — Write Failing Test

**Python (pytest):**

```python
# tests/unit/services/test_task_service.py
@pytest.mark.asyncio
async def test_create_task_returns_id_and_title(mock_repo):
    mock_repo.create.return_value = TaskModel(id="1", title="Test")
    result = await task_service.create(CreateTaskRequest(title="Test"))
    assert result.id == "1"
    assert result.title == "Test"
```

**JavaScript (Vitest):**

```javascript
// tests/unit/services/task-service.test.js
it("should create task with title and return id", async () => {
  mockRepo.create.mockResolvedValue({ id: "1", title: "Test" });
  const result = await createTask({ title: "Test" });
  expect(result.id).toBe("1");
  expect(result.title).toBe("Test");
});
```

Run test — confirm it **fails**.

#### Step 3: GREEN — Minimal Implementation

**Python (FastAPI service):**

```python
# domain/services/task_service.py
async def create(self, data: CreateTaskRequest) -> TaskResponse:
    task = await self.repo.create(title=data.title)
    return TaskResponse.model_validate(task)
```

**JavaScript:**

```javascript
// src/services/task-service.js
async function createTask({ title }) {
  const task = await db.task.create({ data: { title } });
  return task;
}
```

Run test — confirm it **passes**.

#### Step 4: REFACTOR — Improve Code Quality

```
- Improve naming and clarity
- Extract helpers if logic is duplicated
- Remove dead code
- Add type hints (Python) / strict types (TypeScript)
- Run mypy / tsc --noEmit to catch type errors
```

Run tests — confirm they **still pass**.

#### Step 5: Verify & Commit

```bash
# Backend
pytest --cov=. --cov-fail-under=80
mypy .                          # strict type check
alembic upgrade head            # if migrations were added

# Frontend
npm run test:run
npm run build                   # confirm no build errors
tsc --noEmit                    # type check

# Commit specific files — never git add .
git add domain/services/task_service.py tests/unit/services/test_task_service.py
git commit -m "feat(tasks): add create task service"
```

#### Step 6: Mark Complete

Update `docs/plans/[feature-name].md`:

```markdown
- [x] Task 1.1: Create task service
```

### Rules

| Rule                         | Why                                                     |
| ---------------------------- | ------------------------------------------------------- |
| **~100-line limit**          | Test before writing more than ~100 lines                |
| **Touch only what's needed** | Don't refactor adjacent code                            |
| **Keep it building**         | System must compile and tests pass after each increment |
| **Rollback-friendly**        | Each commit must be independently revertable            |
| **No feature flags**         | Ship complete slices or keep behind server-side config  |

### When Stuck

1. **Stop** — Don't push through broken code
2. **Diagnose** — Use `/debug` to find root cause
3. **Fix** — Address the actual problem, not the symptom
4. **Guard** — Add regression test to prevent recurrence
5. **Resume** — Continue from where you stopped

## Red Flags

Stop and reassess if you find yourself:

- Writing > 100 lines without testing
- Mixing unrelated changes in one commit
- Expanding scope mid-task
- Breaking the build between increments
- Creating abstractions "for later"
- Adding fallbacks or error handling for scenarios that can't happen

## Output

- Working, tested code
- Updated `docs/plans/[feature-name].md` with completed items
- Clean git history with atomic commits

## Next Step

After all tasks complete → run `/test` to verify coverage, then `/review` for final quality check.
