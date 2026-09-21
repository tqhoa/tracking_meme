# Testing Patterns Reference

> Quick reference for test patterns. See `.claude/rules/testing.md` for full rules.

## Test Pyramid

```
         ┌─────────┐
         │   E2E   │  5%   Critical user flows
         ├─────────┤
         │  Integ  │  15%  API + DB interactions
         ├─────────┤
         │  Unit   │  80%  Pure logic, fast
         └─────────┘
```

## Test Structure (AAA)

**JavaScript (Vitest):**

```javascript
it("should return 10% discount when order over $100", () => {
  // Arrange
  const amount = 150;

  // Act
  const result = calculateDiscount(amount);

  // Assert
  expect(result).toBe(15);
});
```

**Python (pytest):**

```python
def test_calculate_discount_returns_10_percent_when_order_over_100():
    # Arrange
    amount = 150

    # Act
    result = calculate_discount(amount)

    # Assert
    assert result == 15
```

## Unit Test Examples

**JavaScript:**

```javascript
describe("calculateDiscount", () => {
  it("should return 10% for orders over $100", () => {
    expect(calculateDiscount(150)).toBe(15);
  });

  it("should return 0 for orders under $100", () => {
    expect(calculateDiscount(50)).toBe(0);
  });

  it("should return 0 at exactly $100", () => {
    expect(calculateDiscount(100)).toBe(0);
  });
});
```

**Python:**

```python
def test_calculate_discount_returns_15_for_150():
    assert calculate_discount(150) == 15

def test_calculate_discount_returns_0_for_50():
    assert calculate_discount(50) == 0

def test_calculate_discount_returns_0_at_boundary_100():
    assert calculate_discount(100) == 0
```

## Integration Test Examples

**JavaScript (supertest):**

```javascript
describe("POST /api/v1/users", () => {
  it("should create user and return 201", async () => {
    const response = await request(app)
      .post("/api/v1/users")
      .send({ email: "test@example.com", name: "Test" })
      .set("Authorization", `Bearer ${token}`);

    expect(response.status).toBe(201);
    expect(response.body.data.email).toBe("test@example.com");
  });
});
```

**Python (pytest + httpx):**

```python
@pytest.mark.asyncio
async def test_create_user_returns_201(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "name": "Test"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["data"]["email"] == "test@example.com"
```

## E2E Test Example (Playwright)

```javascript
test("user can complete checkout flow", async ({ page }) => {
  await page.goto("/login");
  await page.fill('[name="email"]', "user@example.com");
  await page.fill('[name="password"]', "password");
  await page.click('button[type="submit"]');

  await page.goto("/products/1");
  await page.click('button:has-text("Add to Cart")');

  await page.goto("/checkout");
  await page.click('button:has-text("Pay")');

  await expect(page.locator(".success-message")).toBeVisible();
});
```

## Vue Component Test

```typescript
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

## Test Doubles

```javascript
// 1. Real (preferred)
const db = createTestDatabase();

// 2. Fake (in-memory)
const fakeUserRepo = {
  users: [],
  create(user) {
    this.users.push(user);
    return user;
  },
  findById(id) {
    return this.users.find((u) => u.id === id);
  },
};

// 3. Stub (canned response)
const stubbedApi = {
  getUser: () => Promise.resolve({ id: "1", name: "Test" }),
};

// 4. Mock (verify interactions — use sparingly)
const mockLogger = vi.fn();
```

```python
# Python test doubles
from unittest.mock import AsyncMock

# Stub
mock_repo = AsyncMock()
mock_repo.find_by_id.return_value = {"id": "1", "name": "Test"}

# Verify call
mock_repo.find_by_id.assert_awaited_once_with("1")
```

## Naming Convention

**JavaScript:** `should [expected] when [condition]`
**Python:** `test_[behavior]_when_[condition]`

```
✅ should return null when user not found
✅ test_find_by_id_returns_none_when_user_not_found

❌ works
❌ test user
❌ error handling
```

## Anti-Patterns

| Pattern           | Problem                 | Fix                                       |
| ----------------- | ----------------------- | ----------------------------------------- |
| Testing internals | Breaks on refactor      | Test behavior                             |
| Shared state      | Tests affect each other | Reset in `beforeEach` / `autouse` fixture |
| Flaky tests       | Random failures         | Deterministic data                        |
| Over-mocking      | False confidence        | Real implementations                      |
| No assertions     | Test always passes      | Assert outcomes                           |
| Magic numbers     | Hard to understand      | Named constants                           |

## Coverage Configuration

**JavaScript (vitest.config.ts):**

```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      thresholds: {
        lines: 80,
        branches: 80,
        functions: 80,
        statements: 80,
      },
    },
  },
});
```

**Python (pyproject.toml):**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["."]
omit = ["tests/*", "alembic/*"]

[tool.coverage.report]
fail_under = 80
```

## Commands

```bash
# JavaScript (Vitest)
npm run test:run          # Run once (CI)
npm test                  # Watch mode
npm run test:coverage     # Coverage report
npm run test:e2e          # Playwright E2E

# Python (pytest)
pytest                              # Run all
pytest tests/unit/                  # Unit only
pytest tests/integration/           # Integration only
pytest --cov=. --cov-fail-under=80  # With coverage
pytest -x                           # Stop on first failure
pytest -k "test_user"               # Filter by name
```
