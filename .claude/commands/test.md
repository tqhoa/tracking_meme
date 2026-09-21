---
name: test
description: Write tests using TDD patterns — tests are proof of correctness
---

# /test — Test-Driven Development

> "Tests are proof, not afterthought."

## Purpose

Write tests that prove code works correctly. Use the RED-GREEN-REFACTOR cycle for new features and the Prove-It pattern for bug fixes.

## For New Features: RED-GREEN-REFACTOR

### RED: Write Failing Test First

**Python (pytest):**

```python
# tests/unit/services/test_user_service.py
@pytest.mark.asyncio
async def test_find_by_id_returns_user_when_found(user_service, mock_repo):
    mock_repo.find_by_id.return_value = UserModel(id="user-123", email="a@b.com")

    result = await user_service.find_by_id("user-123")

    assert result.id == "user-123"
    mock_repo.find_by_id.assert_awaited_once_with("user-123")

@pytest.mark.asyncio
async def test_find_by_id_raises_app_error_when_not_found(user_service, mock_repo):
    mock_repo.find_by_id.return_value = None

    with pytest.raises(AppError) as exc:
        await user_service.find_by_id("nonexistent")

    assert exc.value.status_code == 404
    assert exc.value.code == "USER_NOT_FOUND"
```

**JavaScript (Vitest):**

```javascript
// tests/unit/services/user-service.test.js
describe("UserService.findById", () => {
  it("should return user when found", async () => {
    mockRepo.findById.mockResolvedValue({ id: "user-123", email: "a@b.com" });

    const result = await userService.findById("user-123");

    expect(result.id).toBe("user-123");
  });

  it("should throw AppError when user does not exist", async () => {
    mockRepo.findById.mockResolvedValue(null);

    await expect(userService.findById("nonexistent")).rejects.toThrow(AppError);
  });
});
```

Run tests — **they should fail** (proves nothing is implemented yet).

### GREEN: Write Minimal Code to Pass

**Python:**

```python
async def find_by_id(self, user_id: str) -> UserResponse:
    user = await self.repo.find_by_id(user_id)
    if not user:
        raise AppError("User not found", 404, "USER_NOT_FOUND")
    return UserResponse.model_validate(user)
```

**JavaScript:**

```javascript
async findById(id) {
  const user = await this.repo.findById(id);
  if (!user) throw new AppError('User not found', 404, 'USER_NOT_FOUND');
  return user;
}
```

Run tests — **they should pass**.

### REFACTOR: Improve While Green

- Better naming, extract helpers, remove duplication
- Add type hints (Python) / strict types (TS)
- Run `mypy .` / `tsc --noEmit` — zero errors required

Run full suite — confirm tests **still pass**.

---

## For Bug Fixes: Prove-It Pattern

### Step 1: Write Test That Reproduces the Bug

**Python:**

```python
@pytest.mark.asyncio
async def test_add_item_increments_quantity_when_product_already_in_cart(cart_service):
    await cart_service.add_item("product-1", quantity=1)
    await cart_service.add_item("product-1", quantity=1)

    assert len(cart_service.items) == 1
    assert cart_service.items[0].quantity == 2
```

**JavaScript:**

```javascript
it("should not duplicate items when adding same product twice", async () => {
  await cart.addItem("product-1", 1);
  await cart.addItem("product-1", 1);

  expect(cart.items).toHaveLength(1);
  expect(cart.items[0].quantity).toBe(2);
});
```

### Step 2: Verify Test Fails

Run the test — confirm it **fails** (proving the bug exists).

### Step 3: Fix the Bug

Fix the actual root cause — not a workaround.

### Step 4: Verify Test Passes

Run the test — confirm it **passes** (proving the fix works).

### Step 5: Run Full Suite

```bash
# Backend
pytest --cov=. --cov-fail-under=80
mypy .

# Frontend
npm run test:run
tsc --noEmit
```

---

## Test Pyramid

| Level           | %   | Speed   | Scope                            |
| --------------- | --- | ------- | -------------------------------- |
| **Unit**        | 80% | ms      | Single function, no I/O          |
| **Integration** | 15% | seconds | API + DB, component interactions |
| **E2E**         | 5%  | minutes | Full user flows                  |

---

## Writing Good Tests

### Arrange-Act-Assert Pattern

**Python:**

```python
def test_calculate_total_applies_discount():
    # Arrange
    cart = Cart(items=[Item(price=100)])
    cart.apply_discount(10)

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 90
```

**JavaScript:**

```javascript
it("should calculate total with discount", () => {
  // Arrange
  const cart = new Cart([{ price: 100 }]);
  cart.applyDiscount(10);

  // Act
  const total = cart.calculateTotal();

  // Assert
  expect(total).toBe(90);
});
```

### DAMP Over DRY

Tests must read independently — don't hide setup in shared helpers:

```python
# ✅ DAMP — clear and self-contained
def test_validate_password_rejects_short_password():
    result = validate_password("short")
    assert result.valid is False
    assert result.error == "Password must be at least 8 characters"

# ❌ Too DRY — requires reading shared fixtures to understand
def test_rejects_short(v):
    assert not v(short_pass)
```

### Naming Conventions

**Python:** `test_[behavior]_when_[condition]`

```python
test_find_by_id_returns_user_when_found
test_find_by_id_raises_app_error_when_not_found
test_create_order_raises_when_stock_insufficient
```

**JavaScript:** `should [expected behavior] when [condition]`

```javascript
"should return user when found";
"should throw AppError when user not found";
"should increment quantity when adding existing product";
```

### One Behavior Per Test

```python
# ✅ Good — focused
def test_validate_email_rejects_missing_at_symbol(): ...
def test_validate_email_rejects_empty_string(): ...

# ❌ Bad — multiple behaviors in one test
def test_validate_email():
    assert not validate("")        # required
    assert not validate("bad")     # format
    assert validate("a@b.com")    # valid
```

---

## Test Doubles

Prefer in order:

```
1. Real implementations (best — hit actual DB in integration tests)
2. In-memory fakes (test DB, fake filesystem)
3. Stubs (canned responses)
4. Mocks (verify interactions — use sparingly)
```

**Python (AsyncMock):**

```python
@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.find_by_id.return_value = UserModel(id="1", email="a@b.com")
    return repo

# Verify call
mock_repo.find_by_id.assert_awaited_once_with("1")
```

**JavaScript (vi.fn):**

```javascript
const mockRepo = { findById: vi.fn().mockResolvedValue({ id: "1" }) };
expect(mockRepo.findById).toHaveBeenCalledWith("1");
```

---

## Anti-Patterns

| Anti-Pattern         | Problem                 | Fix                                     |
| -------------------- | ----------------------- | --------------------------------------- |
| Testing internals    | Breaks on refactor      | Test inputs/outputs only                |
| Flaky tests          | Erodes trust            | Deterministic data, isolate state       |
| Over-mocking         | False confidence        | Prefer real implementations             |
| Shared mutable state | Tests affect each other | Reset in `beforeEach` / autouse fixture |
| No assertions        | Test always passes      | Assert concrete outcomes                |

---

## Verification Checklist

```bash
# Coverage gate
pytest --cov=. --cov-fail-under=80    # Python
npm run test:coverage                  # JS (threshold in vitest.config.ts)

# Type safety
mypy .                                 # Python
tsc --noEmit                           # TypeScript

# E2E (critical paths)
npm run test:e2e                       # Playwright
```

- [ ] All new behaviors have tests
- [ ] Bug fixes have reproduction tests before the fix
- [ ] Test names describe behavior, not implementation
- [ ] No skipped or disabled tests (`pytest.mark.skip`, `it.skip`)
- [ ] Coverage ≥ 80% — gate enforced
- [ ] `mypy` / `tsc --noEmit` passes
- [ ] Full test suite green
