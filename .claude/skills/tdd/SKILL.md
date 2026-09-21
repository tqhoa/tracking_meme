---
name: Test-Driven Development
description: Write tests before code using RED-GREEN-REFACTOR cycle
---

# Test-Driven Development Skill

## Overview

TDD transforms testing from an afterthought into the foundation of development. Tests are proof that code works correctly.

## When to Invoke

- Writing new features
- Fixing bugs (Prove-It pattern)
- When asked to write tests
- Before any implementation work

---

## Core Cycle: RED-GREEN-REFACTOR

### RED Phase

Write a test that describes expected behavior. **It must fail.**

**JavaScript (Vitest):**

```javascript
describe("calculateDiscount", () => {
  it("should apply 10% discount for orders over $100", () => {
    const result = calculateDiscount(150);
    expect(result).toBe(15);
  });
});
```

Run: `npm run test:run` → Should **FAIL**

**Python (pytest):**

```python
def test_calculate_discount_applies_10_percent_for_orders_over_100():
    result = calculate_discount(150)
    assert result == 15
```

Run: `pytest -k "test_calculate_discount"` → Should **FAIL**

---

### GREEN Phase

Write **minimal** code to pass the test. No extras.

**JavaScript:**

```javascript
function calculateDiscount(amount) {
  if (amount > 100) return amount * 0.1;
  return 0;
}
```

Run: `npm run test:run` → Should **PASS**

**Python:**

```python
def calculate_discount(amount: float) -> float:
    if amount > 100:
        return amount * 0.1
    return 0
```

Run: `pytest -k "test_calculate_discount"` → Should **PASS**

---

### REFACTOR Phase

Improve code while keeping tests green.

**JavaScript:**

```javascript
const DISCOUNT_THRESHOLD = 100;
const DISCOUNT_RATE = 0.1;

function calculateDiscount(amount) {
  if (amount <= DISCOUNT_THRESHOLD) return 0;
  return amount * DISCOUNT_RATE;
}
```

**Python:**

```python
DISCOUNT_THRESHOLD = 100
DISCOUNT_RATE = 0.1

def calculate_discount(amount: float) -> float:
    if amount <= DISCOUNT_THRESHOLD:
        return 0
    return amount * DISCOUNT_RATE
```

Run full suite → Should still **PASS**

---

## Prove-It Pattern (Bug Fixes)

### Step 1: Write Failing Test

**JavaScript:**

```javascript
it("should handle empty cart without error (bug #456)", () => {
  const cart = new Cart([]);
  expect(() => cart.getTotal()).not.toThrow();
  expect(cart.getTotal()).toBe(0);
});
```

**Python:**

```python
def test_get_total_returns_zero_for_empty_cart():
    # Regression: bug #456 — empty cart raised ZeroDivisionError
    cart = Cart(items=[])
    assert cart.get_total() == 0
```

### Step 2: Verify Failure

Run test → Confirms bug exists.

### Step 3: Fix Bug

### Step 4: Verify Pass

Run test → Confirms fix works.

### Step 5: Run Full Suite

```bash
# Backend
pytest --cov=. --cov-fail-under=80

# Frontend
npm run test:run
```

---

## Test Pyramid

```
         ┌─────────┐
         │   E2E   │  5%  — Critical user flows
         │  Tests  │       Full system, minutes
         ├─────────┤
         │ Integr. │  15% — API + DB interactions
         │  Tests  │       Seconds
         ├─────────┤
         │  Unit   │  80% — Pure logic
         │  Tests  │       Milliseconds
         └─────────┘
```

---

## Test Structure: AAA Pattern

**JavaScript:**

```javascript
it("should calculate tax for California", () => {
  // Arrange
  const order = createOrder({ state: "CA", subtotal: 100 });

  // Act
  const tax = calculateTax(order);

  // Assert
  expect(tax).toBe(7.25);
});
```

**Python:**

```python
def test_calculate_tax_for_california():
    # Arrange
    order = create_order(state="CA", subtotal=100)

    # Act
    tax = calculate_tax(order)

    # Assert
    assert tax == 7.25
```

---

## DAMP > DRY in Tests

Tests should be **Descriptive And Meaningful Phrases**.

```javascript
// ✅ DAMP — Self-contained and clear
it("should reject password without uppercase letter", () => {
  const result = validatePassword("lowercase123!");
  expect(result.valid).toBe(false);
  expect(result.errors).toContain("Must contain uppercase letter");
});

// ❌ Too DRY — Requires reading shared context
it("should reject invalid password", () => {
  expect(validate(INVALID_PASSWORD_NO_UPPER)).toBe(false);
});
```

---

## Test Doubles (Preference Order)

1. **Real implementations** — Best, but may be slow
2. **Fakes** — In-memory DB, simplified implementations
3. **Stubs** — Return canned responses
4. **Mocks** — Verify interactions (use sparingly)

---

## Naming Conventions

**JavaScript:** `should [expected behavior] when [condition]`
**Python:** `test_[behavior]_when_[condition]`

```
✅ should return empty array when no users exist
✅ test_find_by_id_raises_when_user_not_found

❌ works correctly
❌ test_user_creation
❌ handles error
```

---

## Anti-Patterns

| Pattern              | Problem                 | Solution                                  |
| -------------------- | ----------------------- | ----------------------------------------- |
| Testing internals    | Breaks on refactor      | Test behavior, not implementation         |
| Flaky tests          | Erodes trust            | Use deterministic data                    |
| Over-mocking         | False confidence        | Prefer real implementations               |
| Snapshot abuse       | Large diffs ignored     | Use sparingly                             |
| Shared mutable state | Tests affect each other | Reset in `beforeEach` / `autouse` fixture |
| Testing frameworks   | Wasted effort           | Only test your code                       |

---

## Verification Checklist

- [ ] All new code has tests
- [ ] Bug fixes have reproduction tests
- [ ] Tests describe behavior (readable names)
- [ ] No skipped tests
- [ ] Coverage ≥ 80%
- [ ] Full suite passes
