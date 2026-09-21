# Clean Code — JavaScript Rules

> Source: [clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) by Ryan McDermott

## 📦 Variables

### ✅ Use meaningful, pronounceable names

```js
// ❌ Bad
const yyyymmdstr = moment().format("YYYY/MM/DD");

// ✅ Good
const currentDate = moment().format("YYYY/MM/DD");
```

### ✅ Same vocabulary for same type

```js
// ❌ getUserInfo(), getClientData(), getCustomerRecord()
// ✅ getUser()
```

### ✅ Use searchable names (no magic numbers)

```js
// ❌ setTimeout(blastOff, 86400000);
const MILLISECONDS_PER_DAY = 60 * 60 * 24 * 1000;
setTimeout(blastOff, MILLISECONDS_PER_DAY); // ✅
```

### ✅ Use explanatory variables

```js
// ❌ Bad
saveCityZipCode(address.match(regex)[1], address.match(regex)[2]);

// ✅ Good
const [_, city, zipCode] = address.match(cityZipCodeRegex) || [];
saveCityZipCode(city, zipCode);
```

### ✅ Avoid mental mapping — be explicit

```js
// ❌ locations.forEach(l => { dispatch(l); });
// ✅ locations.forEach(location => { dispatch(location); });
```

### ✅ Don't add redundant context

```js
// ❌ const Car = { carMake, carModel, carColor }
// ✅ const Car = { make, model, color }
```

### ✅ Use default parameters

```js
// ❌ const name = name || 'Default';
// ✅ function create(name = 'Default') {}
```

---

## 🔧 Functions

### ✅ 2 arguments or fewer — use object destructuring for more

```js
// ❌ function createMenu(title, body, buttonText, cancellable) {}
// ✅ function createMenu({ title, body, buttonText, cancellable }) {}
```

### ✅ Functions should do ONE thing

```js
// ❌ emailClients() — fetches DB + checks active + sends email
// ✅ emailActiveClients() calls isActiveClient() separately
```

### ✅ Function names should say what they do

```js
// ❌ addToDate(date, 1)     → unclear what is added
// ✅ addMonthToDate(1, date) → crystal clear
```

### ✅ One level of abstraction per function

```js
// ❌ parseBetterJSAlternative() — tokenizes + parses + AST walks in one function
// ✅ parseBetterJSAlternative() → calls tokenize() → calls parse()
```

### ✅ Remove duplicate code — extract shared logic

### ✅ No flag parameters — split into separate functions

```js
// ❌ function createFile(name, isTemp) { if (isTemp) ... }
// ✅ function createFile(name) {}
//    function createTempFile(name) {}
```

### ✅ Avoid Side Effects

- Don't mutate global state
- Don't mutate function arguments (use copies)

```js
// ✅ Return new array instead of mutating
function addItemToCart(cart, item) {
  return [...cart, { item, date: Date.now() }];
}
```

### ✅ Favor functional programming

```js
// ❌ for loop with mutations
// ✅ filter(), map(), reduce()
const totalOutput = programmerOutput
  .filter((p) => p.linesOfCode > 0)
  .reduce((acc, p) => acc + p.linesOfCode, 0);
```

### ✅ Encapsulate conditionals

```js
// ❌ if (fsm.state === 'fetching' && isEmpty(listNode)) {}
// ✅ if (shouldShowSpinner(fsmInstance, listNodeInstance)) {}
```

### ✅ Avoid negative conditionals

```js
// ❌ if (!isNotDOMNodePresent(node)) {}
// ✅ if (isDOMNodePresent(node)) {}
```

### ✅ Remove dead code immediately

---

## 🏛️ Classes

### ✅ Prefer ES6 classes

### ✅ Use method chaining (builder pattern)

```js
class QueryBuilder {
  select(fields) {
    this.fields = fields;
    return this;
  }
  from(table) {
    this.table = table;
    return this;
  }
  build() {
    return `SELECT ${this.fields} FROM ${this.table}`;
  }
}
new QueryBuilder().select("*").from("users").build();
```

### ✅ Prefer composition over inheritance

> "Favor has-a over is-a"

---

## 🧱 SOLID Principles

| Principle                     | Rule                                                  |
| ----------------------------- | ----------------------------------------------------- |
| **S** — Single Responsibility | One class = one job. Never combine unrelated concerns |
| **O** — Open/Closed           | Open for extension, closed for modification           |
| **L** — Liskov Substitution   | Subclasses must be substitutable for their base class |
| **I** — Interface Segregation | Clients shouldn't depend on interfaces they don't use |
| **D** — Dependency Inversion  | Depend on abstractions, not concretions               |

```js
// ✅ D — Dependency Inversion
class InventoryService {
  constructor(inventoryRequester) {
    // inject the dependency
    this.inventoryRequester = inventoryRequester;
  }
  requestItems(customer) {
    return this.inventoryRequester.requestItem(customer.purchaseHistory);
  }
}
```

---

## ⚡ Concurrency

### ✅ Use Promises over callbacks

### ✅ Use async/await over Promises

```js
// ✅ Clearest form
async function getCleanCodeArticle() {
  try {
    const response = await request.get(cleanCodeUrl);
    await fs.writeFile("article.html", response);
  } catch (err) {
    console.error(err);
  }
}
```

---

## 🗒️ Comments

### ✅ Only comment business logic complexity

### ❌ Never leave commented-out code

### ❌ No journal comments (use git log instead)

### ❌ No positional markers (`/////`)

```js
// ✅ Good comment — explains WHY
// We retry 3x because OAuth2 tokens can have clock skew
const MAX_RETRIES = 3;
```

---

## 📐 Formatting

- Use consistent capitalization (camelCase for vars/fns, PascalCase for classes, UPPER_SNAKE for constants)
- Keep callers and callees close in the file
- Related code should appear together

---

---

# Clean Code — Python Rules

> Adapted from clean-code principles for idiomatic Python (PEP 8, PEP 20, Pythonic style)
> Source: [clean-code-python](https://github.com/zedr/clean-code-python) by Rigel Di Scala

## 📦 Variables

### ✅ Use meaningful, pronounceable names

```python
# ❌ Bad
yyyymmdstr = datetime.now().strftime('%Y/%m/%d')
d = 86400

# ✅ Good
current_date = datetime.now().strftime('%Y/%m/%d')
SECONDS_PER_DAY = 60 * 60 * 24
```

### ✅ Same vocabulary for the same concept

```python
# ❌ get_user_info(), fetch_client_data(), retrieve_customer_record()
# ✅ get_user()
```

### ✅ Use searchable names — no magic numbers

```python
# ❌
time.sleep(86400)

# ✅
SECONDS_PER_DAY = 86400
time.sleep(SECONDS_PER_DAY)
```

### ✅ Use explanatory variables

```python
# ❌ Bad
save_city_zip(address_match[1], address_match[2])

# ✅ Good
city, zip_code = address_match.group(1), address_match.group(2)
save_city_zip(city, zip_code)
```

### ✅ Avoid mental mapping — be explicit

```python
# ❌
for l in locations:
    dispatch(l)

# ✅
for location in locations:
    dispatch(location)
```

### ✅ Don't add redundant context

```python
# ❌
car = {'car_make': 'Toyota', 'car_model': 'Camry', 'car_color': 'Blue'}

# ✅
car = {'make': 'Toyota', 'model': 'Camry', 'color': 'Blue'}
```

### ✅ Use default parameter values

```python
# ❌
def create_user(name):
    name = name or 'Anonymous'

# ✅
def create_user(name: str = 'Anonymous') -> User:
    ...
```

---

## 🔧 Functions

### ✅ 2 arguments or fewer — use dataclasses/TypedDict for more

```python
# ❌
def create_menu(title, body, button_text, cancellable):
    ...

# ✅
@dataclass
class MenuConfig:
    title: str
    body: str
    button_text: str
    cancellable: bool = True

def create_menu(config: MenuConfig) -> None:
    ...
```

### ✅ Functions should do ONE thing

```python
# ❌ email_clients() — queries DB + checks active + sends email in one function

# ✅ Split responsibilities
def email_active_clients(clients: list[Client]) -> None:
    active = [c for c in clients if is_active_client(c)]
    for client in active:
        send_email(client)

def is_active_client(client: Client) -> bool:
    return client.last_active >= date.today() - timedelta(days=30)
```

### ✅ Function names should say what they do

```python
# ❌
def add_to_date(date, months):
    ...

# ✅
def add_months_to_date(months: int, date: date) -> date:
    ...
```

### ✅ One level of abstraction per function

```python
# ❌ parse_code() — tokenizes + parses + walks AST all in one block

# ✅
def parse_code(source: str) -> AST:
    tokens = tokenize(source)
    return parse_tokens(tokens)
```

### ✅ No flag parameters — split into separate functions

```python
# ❌
def create_file(name: str, is_temp: bool) -> None:
    if is_temp:
        tmp_dir / name
    else:
        ...

# ✅
def create_file(name: str) -> Path: ...
def create_temp_file(name: str) -> Path: ...
```

### ✅ Avoid Side Effects — return new values, don't mutate arguments

```python
# ❌ Mutates the list in place
def add_item_to_cart(cart: list, item: dict) -> None:
    cart.append(item)

# ✅ Returns a new list
def add_item_to_cart(cart: list[dict], item: dict) -> list[dict]:
    return [*cart, item]
```

### ✅ Favor comprehensions and built-ins over manual loops

```python
# ❌
total = 0
for p in programmer_output:
    if p['lines_of_code'] > 0:
        total += p['lines_of_code']

# ✅
total = sum(p['lines_of_code'] for p in programmer_output if p['lines_of_code'] > 0)
```

### ✅ Encapsulate conditionals

```python
# ❌
if fsm.state == 'fetching' and not list_node:
    show_spinner()

# ✅
def should_show_spinner(fsm: FSM, list_node: Node) -> bool:
    return fsm.state == 'fetching' and not list_node

if should_show_spinner(fsm, list_node):
    show_spinner()
```

### ✅ Avoid negative conditionals

```python
# ❌
if not is_not_dom_node_present(node):
    ...

# ✅
if is_dom_node_present(node):
    ...
```

### ✅ Remove dead code immediately

---

## 🏛️ Classes

### ✅ Use dataclasses for plain data containers

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
```

### ✅ Use method chaining (builder pattern) where it improves readability

```python
class QueryBuilder:
    def select(self, fields: str) -> 'QueryBuilder':
        self._fields = fields
        return self

    def from_table(self, table: str) -> 'QueryBuilder':
        self._table = table
        return self

    def build(self) -> str:
        return f'SELECT {self._fields} FROM {self._table}'

query = QueryBuilder().select('*').from_table('users').build()
```

### ✅ Prefer composition over inheritance

```python
# ❌ Deep inheritance chains
class Animal: ...
class Dog(Animal): ...
class GuideDog(Dog): ...

# ✅ Compose behaviors
@dataclass
class Dog:
    name: str
    trainer: Trainer   # has-a, not is-a
```

---

## 🧱 SOLID Principles (Python)

| Principle                     | Rule                                                 |
| ----------------------------- | ---------------------------------------------------- |
| **S** — Single Responsibility | One class = one job                                  |
| **O** — Open/Closed           | Extend via new classes, don't modify existing        |
| **L** — Liskov Substitution   | Subclasses must be substitutable for their base      |
| **I** — Interface Segregation | Use `Protocol` to define narrow contracts            |
| **D** — Dependency Inversion  | Depend on abstractions (`Protocol`), not concretions |

```python
# ✅ D — Dependency Inversion with Protocol
from typing import Protocol

class InventoryRequester(Protocol):
    def request_item(self, item: str) -> bool: ...

class InventoryService:
    def __init__(self, requester: InventoryRequester) -> None:
        self._requester = requester

    def request_items(self, items: list[str]) -> list[bool]:
        return [self._requester.request_item(item) for item in items]
```

---

## 🔑 Type Hints

### ✅ Always annotate function signatures

```python
# ❌
def get_user(user_id):
    ...

# ✅
def get_user(user_id: str) -> User | None:
    ...
```

### ✅ Use `|` union syntax (Python 3.10+) over `Optional`

```python
# ❌
from typing import Optional
def find(id: str) -> Optional[User]: ...

# ✅
def find(id: str) -> User | None: ...
```

### ✅ Use `TypeAlias` and `TypeVar` for complex types

```python
from typing import TypeAlias, TypeVar

UserId: TypeAlias = str
T = TypeVar('T')

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

---

## ⚡ Async / Concurrency

### ✅ Use async/await for I/O-bound work

```python
# ✅ Clearest form
async def fetch_user_article(user_id: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'/users/{user_id}/article')
        response.raise_for_status()
        return response.text
```

### ✅ Run independent async tasks concurrently

```python
# ❌ Sequential — slow
user = await get_user(user_id)
orders = await get_orders(user_id)

# ✅ Concurrent
user, orders = await asyncio.gather(get_user(user_id), get_orders(user_id))
```

### ✅ Use context managers for resource cleanup

```python
# ✅
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User))
```

---

## 🗒️ Comments

### ✅ Only comment business logic complexity — explain WHY, not WHAT

### ❌ Never leave commented-out code

### ❌ No changelog/journal comments (use git log)

```python
# ✅ Good — explains WHY
# Retry 3x: the payment gateway returns transient 503s during peak hours
MAX_RETRIES = 3

# ❌ Bad — states the obvious
# Increment counter by 1
counter += 1
```

### ✅ Docstrings only for public APIs

```python
def send_invoice(order_id: str, recipient: str) -> bool:
    """Send a PDF invoice email for the given order.

    Returns True if the email was queued successfully.
    Raises AppError if the order is not found.
    """
```

---

## 📐 Formatting (PEP 8)

- **Indentation**: 4 spaces (no tabs)
- **Max line length**: 88 characters (Black default)
- **Naming**:
  - `snake_case` — variables, functions, modules
  - `PascalCase` — classes
  - `UPPER_SNAKE_CASE` — constants
  - `_private` — internal use (single underscore prefix)
- **Blank lines**: 2 between top-level definitions, 1 between methods
- **Imports order**: stdlib → third-party → local (use `isort`)
- **Formatter**: Black (non-negotiable)
- **Linter**: Ruff (replaces flake8 + isort)

```python
# ✅ Import order
import asyncio
from datetime import datetime

import httpx
from fastapi import FastAPI

from shared.config import settings
from domain.services import user_service
```
