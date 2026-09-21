# Code Style Guide

## General Principles

- **Clarity over cleverness** — Write code that is easy to read and understand
- **Consistency** — Follow existing patterns in the codebase
- **DRY** — Don't Repeat Yourself, but don't over-abstract

## JavaScript / TypeScript

### Formatting

- Indentation: **2 spaces** (no tabs)
- Max line length: **100 characters**
- Use **single quotes** for strings
- Always use **semicolons**
- Trailing commas in multi-line structures

### Naming

```js
// Variables and functions: camelCase
const userProfile = {};
function getUserById(id) {}

// Classes and interfaces: PascalCase
class UserService {}
interface UserRepository {}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';

// Files: kebab-case
// user-service.js, auth-middleware.js
```

### Functions

```js
// ✅ Good — Arrow functions for simple operations
const double = (x) => x * 2;

// ✅ Good — Named functions for complex logic
function processUserData(user) {
  // ...
}

// ❌ Avoid — Functions longer than 30 lines (extract helpers)
```

### Async/Await

```js
// ✅ Always use async/await over raw promises
async function fetchUser(id) {
  try {
    const user = await userRepository.findById(id);
    return user;
  } catch (error) {
    throw new AppError('User not found', 404);
  }
}

// ❌ Avoid promise chains
fetchUser(id).then(...).catch(...);
```

### Imports

```js
// Order: 1. Node built-ins, 2. External deps, 3. Internal modules
import path from "path";
import express from "express";
import { UserService } from "./user-service.js";
```

## Comments

```js
// ✅ Explain WHY, not WHAT
// We retry 3 times because the external API has transient failures
const MAX_RETRIES = 3;

// ❌ Avoid obvious comments
// Set x to 5
const x = 5;
```

## File Organization

- One class/service per file
- Group related files in feature folders
- Index files for clean imports

---

## Python

### Toolchain (non-negotiable)

| Tool       | Purpose             | Config           |
| ---------- | ------------------- | ---------------- |
| **Black**  | Auto-formatter      | `pyproject.toml` |
| **Ruff**   | Linter + isort      | `pyproject.toml` |
| **mypy**   | Static type checker | `pyproject.toml` |
| **pytest** | Test runner         | `pyproject.toml` |

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ["py312"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
```

### Formatting

- Indentation: **4 spaces** (no tabs)
- Max line length: **88 characters** (Black default)
- Strings: **double quotes** (Black enforces this)
- Trailing commas in multi-line structures (Black adds automatically)
- No semicolons — one statement per line

### Naming Conventions

```python
# Variables and functions: snake_case
user_profile = {}
def get_user_by_id(user_id: str) -> User: ...

# Classes: PascalCase
class UserService: ...
class OrderRepository: ...

# Constants: UPPER_SNAKE_CASE (module-level)
MAX_RETRY_COUNT = 3
API_BASE_URL = "https://api.example.com"

# Private (internal use): single leading underscore
_cache: dict = {}
def _hash_password(plain: str) -> str: ...

# Type aliases: PascalCase
UserId = str
OrderList = list[Order]

# Files and modules: snake_case
# user_service.py, auth_middleware.py, order_repository.py

# Packages/folders: snake_case (no hyphens)
# domain/services/, infrastructure/cache/
```

### Type Hints

```python
# ✅ Always annotate public function signatures
def create_user(email: str, name: str, role: str = "user") -> User:
    ...

# ✅ Use X | None (Python 3.10+) over Optional[X]
def find_user(user_id: str) -> User | None:
    ...

# ✅ Use built-in generics (Python 3.9+) — no need to import from typing
def get_users(ids: list[str]) -> dict[str, User]:
    ...

# ✅ Use TypeAlias for complex repeated types
from typing import TypeAlias
JsonDict: TypeAlias = dict[str, object]

# ❌ Never use Any without a comment explaining why
from typing import Any
result: Any  # ❌

# ✅ Narrow with cast or assert when truly needed
from typing import cast
user = cast(User, raw_data)
```

### Functions

```python
# ✅ Short, single-purpose — max ~30 lines
async def get_user(user_id: str, db: AsyncSession) -> User:
    user = await user_repo.find_by_id(db, user_id)
    if not user:
        raise AppError("User not found", 404, "USER_NOT_FOUND")
    return user

# ✅ Use * to force keyword-only arguments when order is ambiguous
def create_order(*, user_id: str, product_id: str, quantity: int = 1) -> Order:
    ...

# ✅ Use / to mark positional-only arguments (stdlib pattern)
def distance(x: float, y: float, /) -> float:
    return (x**2 + y**2) ** 0.5

# ❌ Avoid mutable default arguments
def append_item(item: str, items: list[str] = []) -> list[str]:  # ❌ bug-prone
    ...

# ✅ Use None sentinel instead
def append_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    return [*items, item]
```

### Classes

```python
# ✅ Use @dataclass for plain data containers
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UserCreateRequest:
    email: str
    name: str
    role: str = "user"
    tags: list[str] = field(default_factory=list)

# ✅ Use __slots__ on hot-path dataclasses to reduce memory
@dataclass(slots=True)
class Point:
    x: float
    y: float

# ✅ Use @classmethod for named constructors
class User:
    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "User":
        return cls(id=str(data["id"]), email=str(data["email"]))

# ✅ Use __repr__ (auto-generated by @dataclass) for debugging
# ✅ Implement __eq__ only when semantic equality differs from identity
```

### Async / Await

```python
# ✅ Use async/await for all I/O — never block the event loop
async def fetch_user(user_id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        response.raise_for_status()
        return User(**response.json())

# ✅ Run independent coroutines concurrently with asyncio.gather
user, orders = await asyncio.gather(
    get_user(user_id),
    get_orders(user_id),
)

# ❌ Never call sync-blocking code inside async functions
async def bad() -> None:
    time.sleep(1)        # ❌ blocks the event loop
    requests.get(url)    # ❌ use httpx.AsyncClient instead

# ✅ Offload CPU-bound work to a thread/process pool
import asyncio
result = await asyncio.to_thread(heavy_cpu_task, data)
```

### Imports

```python
# Order enforced by Ruff/isort:
# 1. Standard library
# 2. Third-party
# 3. Local / internal

import asyncio
import uuid
from datetime import datetime, timedelta

import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.user_service import UserService
from shared.config import settings
from shared.exceptions import AppError
```

### Error Handling

```python
# ✅ Catch specific exceptions — never bare except
try:
    user = await user_repo.find_by_id(user_id)
except sqlalchemy.exc.OperationalError as exc:
    raise AppError("Database unavailable", 503) from exc

# ✅ Use 'from exc' to preserve the original traceback
raise AppError("Not found", 404) from original_exception

# ❌ Never silence exceptions
try:
    do_something()
except Exception:
    pass  # ❌

# ✅ Log and re-raise if you can't handle it
except Exception:
    logger.error("unexpected_error", exc_info=True)
    raise
```

### Comments and Docstrings

```python
# ✅ Module-level docstring (brief, one line)
"""User service — business logic for user lifecycle management."""

# ✅ Public function/class docstring (Google style)
def send_password_reset(email: str) -> bool:
    """Send a password reset email to the given address.

    Args:
        email: The recipient's email address (must be registered).

    Returns:
        True if the email was queued; False if the address is unknown.

    Raises:
        AppError: If the email provider is unavailable.
    """

# ✅ Inline comment — explain WHY, not WHAT
# Retry 3x: payment gateway returns transient 503s during peak hours
MAX_RETRIES = 3

# ❌ No obvious comments
user_count += 1  # increment user count  ❌
```

## File Organization (Python)

- One class or cohesive group of functions per file
- Module name = `snake_case.py`
- Package `__init__.py` exports only the public interface
- Co-locate tests next to source or mirror structure under `tests/`
- Never put business logic in `__init__.py`
