# Testing Standards

## Testing Pyramid

```
         [E2E Tests]         ← Few, slow, catch integration issues
       [Integration Tests]   ← Some, test component interaction
     [Unit Tests]            ← Many, fast, test isolated logic
```

## Requirements

- Unit test coverage: **minimum 80%**
- All new features must have tests
- All bug fixes must have a regression test
- Tests run in CI before any merge

---

## JavaScript / Jest

### Test File Organization

```
tests/
├── unit/
│   ├── services/user-service.test.js
│   └── utils/format.test.js
├── integration/
│   ├── routes/users.test.js
│   └── database/user-repo.test.js
└── e2e/
    └── auth-flow.test.js
```

### Unit Test Example

```js
// tests/unit/services/user-service.test.js
import { UserService } from "../../../src/services/user-service.js";
import { mockUserRepository } from "../../mocks/user-repository.mock.js";

describe("UserService", () => {
  let userService;
  let mockRepo;

  beforeEach(() => {
    mockRepo = mockUserRepository();
    userService = new UserService(mockRepo);
  });

  describe("findById", () => {
    it("should return user when found", async () => {
      const mockUser = { id: "1", email: "test@test.com" };
      mockRepo.findById.mockResolvedValue(mockUser);

      const result = await userService.findById("1");

      expect(result).toEqual(mockUser);
      expect(mockRepo.findById).toHaveBeenCalledWith("1");
    });

    it("should throw AppError when user not found", async () => {
      mockRepo.findById.mockResolvedValue(null);
      await expect(userService.findById("999")).rejects.toThrow(
        "User not found",
      );
    });
  });
});
```

### Integration Test Example

```js
// tests/integration/routes/users.test.js
import request from "supertest";
import app from "../../../src/index.js";

describe("GET /api/users/:id", () => {
  it("should return 200 with user data", async () => {
    const res = await request(app)
      .get("/api/users/1")
      .set("Authorization", `Bearer ${testToken}`);
    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
  });

  it("should return 404 for unknown user", async () => {
    const res = await request(app)
      .get("/api/users/99999")
      .set("Authorization", `Bearer ${testToken}`);
    expect(res.status).toBe(404);
  });
});
```

### Test Commands (JS)

```bash
npm test                    # Run all tests
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:coverage       # Generate coverage report
npm run test:watch          # Watch mode
```

### Naming Conventions (JS)

- Test files: `[filename].test.js`
- `describe` blocks: match the module/function being tested
- `it` blocks: `should [expected behavior] when [condition]`

---

## Python / pytest + httpx

### Test File Organization

```
tests/
├── unit/
│   └── services/
│       ├── test_user_service.py
│       └── test_order_service.py
├── integration/
│   └── routes/
│       ├── test_users.py
│       └── test_orders.py
└── conftest.py
```

### conftest.py (fixtures)

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app
from infrastructure.database.session import get_db
from infrastructure.database.models.user import Base

TEST_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/test_db"


# pyproject.toml must include: [tool.pytest.ini_options] asyncio_mode = "auto"
# Required for session-scoped async fixtures (pytest-asyncio >= 0.21)
@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    AsyncSession_ = async_sessionmaker(db_engine, expire_on_commit=False)
    async with AsyncSession_() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    # Override must be an async generator to match get_db's signature
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

### Unit Test Example

```python
# tests/unit/services/test_user_service.py
import pytest
from unittest.mock import AsyncMock
from domain.services.user_service import UserService
from shared.exceptions import AppError


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def user_service(mock_repo):
    # Use normal constructor, then override repo — avoids bypassing __init__
    service = UserService(db=AsyncMock())
    service.repo = mock_repo
    return service


@pytest.mark.asyncio
async def test_find_by_id_returns_user(user_service, mock_repo):
    mock_user = {"id": "1", "email": "test@test.com"}
    mock_repo.find_by_id.return_value = mock_user

    result = await user_service.find_by_id("1")

    assert result == mock_user
    mock_repo.find_by_id.assert_awaited_once_with("1")


@pytest.mark.asyncio
async def test_find_by_id_raises_when_not_found(user_service, mock_repo):
    mock_repo.find_by_id.return_value = None

    with pytest.raises(AppError) as exc_info:
        await user_service.find_by_id("999")

    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "USER_NOT_FOUND"
```

### Integration Test Example

```python
# tests/integration/routes/test_users.py
import pytest


@pytest.mark.asyncio
async def test_get_user_returns_200(client, test_user, auth_headers):
    response = await client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_user_not_found_returns_404(client, auth_headers):
    response = await client.get("/api/v1/users/nonexistent", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_user_unauthenticated_returns_401(client):
    response = await client.get("/api/v1/users/some-id")
    assert response.status_code == 401
```

### Test Commands (Python)

```bash
pytest                              # Run all tests
pytest tests/unit/                  # Unit tests only
pytest tests/integration/           # Integration tests only
pytest --cov=src --cov-report=html  # Coverage report
pytest -x                           # Stop on first failure
pytest -k "test_user"               # Filter by name
```

### Naming Conventions (Python)

- Test files: `test_[module].py`
- Test functions: `test_[behavior]_when_[condition]`
- Fixtures: descriptive noun (`user_service`, `auth_headers`, `test_user`)

---

## Vue 3 / Vitest + Vue Testing Library

### Test File Organization

```
tests/
├── unit/
│   ├── components/
│   │   └── BaseButton.test.ts
│   └── composables/
│       └── useDebounce.test.ts
├── integration/
│   └── features/
│       └── auth.test.ts
└── e2e/
    └── auth-flow.spec.ts
```

### Component Test Example

```typescript
// tests/unit/components/BaseButton.test.ts
import { describe, it, expect, vi } from "vitest";
import { render, fireEvent } from "@testing-library/vue";
import BaseButton from "@/components/ui/BaseButton.vue";

describe("BaseButton", () => {
  it("renders slot content", () => {
    const { getByText } = render(BaseButton, {
      slots: { default: "Click me" },
    });
    expect(getByText("Click me")).toBeInTheDocument();
  });

  it("emits click event when clicked", async () => {
    const { getByRole, emitted } = render(BaseButton, {
      slots: { default: "Click" },
    });
    await fireEvent.click(getByRole("button"));
    expect(emitted().click).toHaveLength(1);
  });

  it("is disabled when loading prop is true", () => {
    const { getByRole } = render(BaseButton, {
      props: { loading: true },
      slots: { default: "Loading" },
    });
    expect(getByRole("button")).toBeDisabled();
  });
});
```

### Composable Test Example

```typescript
// tests/unit/composables/useDebounce.test.ts
import { describe, it, expect, vi } from "vitest";
import { ref } from "vue";
import { useDebounce } from "@/composables/useDebounce";

describe("useDebounce", () => {
  it("debounces value changes by the specified delay", async () => {
    vi.useFakeTimers();
    const value = ref("initial");
    const debounced = useDebounce(value, 300);

    expect(debounced.value).toBe("initial");

    value.value = "updated";
    expect(debounced.value).toBe("initial"); // not yet

    vi.advanceTimersByTime(300);
    expect(debounced.value).toBe("updated"); // now updated

    vi.useRealTimers();
  });
});
```

### Pinia Store Test

```typescript
// tests/unit/stores/useUserStore.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useUserStore } from "@/stores/useUserStore";

describe("useUserStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("isAuthenticated is false when no token", () => {
    const store = useUserStore();
    expect(store.isAuthenticated).toBe(false);
  });

  it("isAuthenticated is true after setToken", () => {
    const store = useUserStore();
    store.setToken("abc123");
    expect(store.isAuthenticated).toBe(true);
  });

  it("clears state on logout", () => {
    const store = useUserStore();
    store.setToken("abc123");
    store.logout();
    expect(store.token).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });
});
```

### Test Commands (Vue / Vitest)

```bash
npm run test              # Run all tests (watch mode)
npm run test:run          # Run once (CI)
npm run test:coverage     # Coverage report
npm run test:e2e          # Playwright E2E
npx vitest run --reporter=verbose
```

### Naming Conventions (Vue)

- Test files: `[ComponentName].test.ts` or `use[Name].test.ts`
- `describe` blocks: component or composable name
- `it` blocks: `[action/state] when [condition]`
- Prefer `getByRole` / `getByLabelText` over `getByTestId` (tests behavior, not impl)
