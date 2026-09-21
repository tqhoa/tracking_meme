---
name: simplify
description: Reduce complexity without changing behavior — code simplification
---

# /simplify — Code Simplification

> "Complexity is the enemy of execution."

## Purpose

Simplify code for clarity and maintainability. Reduce complexity **without changing behavior**.

## When to Use

- After `/review` identifies complexity issues
- When code is hard to understand
- Before adding new features to tangled code
- During tech debt cleanup sprints

## Principles

### Chesterton's Fence

> Before removing something, understand why it exists.

Don't delete code just because it looks unnecessary. Investigate:

- Git history: `git log -p -- path/to/file`
- Related tests
- Comments or documentation

### Rule of 500

If a function, file, or class exceeds ~500 lines, it likely needs splitting.

---

## Workflow

### Step 1: Identify Target

```bash
# Recently modified complex code
git diff --stat HEAD~10

# Or specify scope: "Simplify the OrderService class"
```

### Step 2: Understand Before Changing

1. **Read the code** — What does it do?
2. **Check tests** — What behaviors are verified?
3. **Trace callers** — Who uses this code?
4. **Note edge cases** — Any special handling?

### Step 3: Identify Opportunities

| Pattern                     | Simplification                       |
| --------------------------- | ------------------------------------ |
| Deep nesting (> 3 levels)   | Guard clauses, extract helpers       |
| Long functions (> 30 lines) | Split by responsibility              |
| Nested ternaries            | `if/else` or `match` (Python 3.10+)  |
| Unclear names               | Rename for clarity                   |
| Duplicated code             | Extract shared function              |
| Dead code                   | Remove entirely                      |
| Complex conditionals        | Extract to named function            |
| Magic numbers/strings       | Named constants                      |
| `for` loop with `append`    | List/dict/set comprehension (Python) |
| Manual `any`/`all` loop     | Built-in `any()` / `all()` (Python)  |

### Step 4: Apply Incrementally

**One change at a time. Run tests after each change.**

### Step 5: Validate

```bash
# Backend
pytest --cov=. --cov-fail-under=80
mypy .

# Frontend
npm run test:run && npm run build
tsc --noEmit

# Behavior unchanged — verify manually if needed
```

### Step 6: If Tests Fail

**Revert immediately.** Don't debug while mid-simplification.

```bash
git restore .   # discard all unstaged changes
```

Then:

1. Reassess the change
2. Make a smaller change
3. Or add missing tests first

---

## Common Simplifications

### Guard Clauses (Early Return)

**Python:**

```python
# Before — deep nesting
def process_order(order):
    if order:
        if order.items:
            if order.status == "pending":
                # actual logic buried here
                pass

# After — guard clauses
def process_order(order: Order | None) -> None:
    if not order:
        return
    if not order.items:
        return
    if order.status != "pending":
        return

    # actual logic at top level
```

**JavaScript:**

```javascript
// Before
function processOrder(order) {
  if (order) {
    if (order.items.length > 0) {
      if (order.status === "pending") {
        // actual logic buried here
      }
    }
  }
}

// After
function processOrder(order) {
  if (!order) return;
  if (order.items.length === 0) return;
  if (order.status !== "pending") return;

  // actual logic at top level
}
```

### Extract Named Functions

**Python:**

```python
# Before — opaque filter condition
eligible = [u for u in users
            if u.age >= 18 and u.verified and not u.banned and u.plan != "free"]

# After — named predicate
def is_eligible(user: User) -> bool:
    return u.age >= 18 and u.verified and not u.banned and u.plan != "free"

eligible = [u for u in users if is_eligible(u)]
```

**JavaScript:**

```javascript
// Before
const eligible = users.filter(
  (u) => u.age >= 18 && u.verified && !u.banned && u.subscription !== "free",
);

// After
const isEligible = (user) =>
  user.age >= 18 &&
  user.verified &&
  !user.banned &&
  user.subscription !== "free";

const eligible = users.filter(isEligible);
```

### Replace Nested Ternary / if-elif Chain

**Python:**

```python
# Before — elif chain
def get_discount(user: User) -> float:
    if user.tier == "gold":
        return 0.3
    elif user.tier == "silver":
        return 0.2
    elif user.tier == "bronze":
        return 0.1
    else:
        return 0.0

# After — dict lookup (simple mapping)
TIER_DISCOUNTS = {"gold": 0.3, "silver": 0.2, "bronze": 0.1}

def get_discount(user: User) -> float:
    return TIER_DISCOUNTS.get(user.tier, 0.0)
```

**JavaScript:**

```javascript
// Before — nested ternary
const status = isPaid ? (isShipped ? "complete" : "processing") : "pending";

// After — early returns
function getOrderStatus(isPaid, isShipped) {
  if (!isPaid) return "pending";
  if (!isShipped) return "processing";
  return "complete";
}
```

### Replace Loop with Comprehension (Python)

```python
# Before — for loop with append
active_ids = []
for user in users:
    if user.is_active:
        active_ids.append(user.id)

# After — list comprehension
active_ids = [user.id for user in users if user.is_active]

# Before — manual any/all check
has_admin = False
for user in users:
    if user.role == "admin":
        has_admin = True
        break

# After — built-in
has_admin = any(u.role == "admin" for u in users)
```

### Remove Dead Code

**Python:**

```python
# Before
async def get_user(user_id: str) -> UserResponse:
    # old_result = legacy_get_user(user_id)  # old path
    user = await self.repo.find_by_id(user_id)
    # print("debug:", user)
    return UserResponse.model_validate(user)

# After
async def get_user(user_id: str) -> UserResponse:
    user = await self.repo.find_by_id(user_id)
    return UserResponse.model_validate(user)
```

**JavaScript:**

```javascript
// Before
function calculate(a, b) {
  // const old = legacyCalc(a, b);
  const result = a + b;
  // console.log('Debug:', result);
  return result;
}

// After
function calculate(a, b) {
  return a + b;
}
```

---

## Red Flags

Stop if you find yourself:

- Changing behavior while "simplifying"
- Unable to explain why code exists
- Simplifying without tests
- Making changes across unrelated files
- Creating new abstractions "for future use"

---

## Output

- Simpler, clearer code
- All tests still passing (`pytest --cov-fail-under=80`, `mypy`, `tsc --noEmit`)
- Atomic commits per simplification with clear messages

## Next Step

Run `/review` to verify improvements.
