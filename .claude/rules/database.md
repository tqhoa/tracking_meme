# Database Rules

## General Rules

- **Never** write raw SQL strings directly in business logic
- Always use an ORM or query builder
- All database calls must be inside try/catch (JS) or try/except (Python) blocks
- Use **transactions** for multi-step operations

## Naming Conventions

- Tables: **snake_case** plural (`user_profiles`, `order_items`)
- Columns: **snake_case** (`created_at`, `user_id`)
- Indexes: `idx_[table]_[column]`
- Foreign keys: `fk_[child_table]_[parent_table]`

## Migrations

- Always use migration files — never modify schema directly
- Migration files are version-controlled and immutable
- Run migrations in CI/CD before deploying

## Security

- Never log query results containing sensitive data (passwords, tokens)
- Use parameterized queries — never string concatenation
- Apply row-level security where applicable

---

## JavaScript / Prisma + node-postgres

### Connection Management (node-postgres / pg)

```js
// ✅ Use connection pooling (node-postgres)
import { Pool } from "pg";
const pool = new Pool({ max: 10, idleTimeoutMillis: 30000 });

// ❌ Never create a new connection per request
```

### Prisma Client Singleton

```js
// src/lib/db.js — reuse one PrismaClient instance
import { PrismaClient } from "@prisma/client";
const globalForPrisma = globalThis;
export const db = globalForPrisma.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = db;
```

### Query Best Practices

```js
// ✅ Select only needed fields
const user = await db.user.findUnique({
  where: { id },
  select: { id: true, email: true, name: true },
});

// ✅ Use pagination for lists
const users = await db.user.findMany({
  take: limit,
  skip: (page - 1) * limit,
  orderBy: { createdAt: "desc" },
});
```

### Transactions (Prisma)

```js
// ✅ Atomic operations
await db.$transaction(async (tx) => {
  const order = await tx.order.create({ data: orderData });
  await tx.inventory.update({
    where: { id: productId },
    data: { stock: { decrement: 1 } },
  });
  return order;
});
```

---

## Python / SQLAlchemy 2.0 async

### Model Definition

```python
# infrastructure/database/models/user.py
import uuid
from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Mapped[str] is non-nullable by default in SA 2.0 — no need for nullable=False
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    # server_default ensures column is never NULL at DB level on INSERT
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)  # soft delete — intentionally nullable
```

### Session Factory

```python
# infrastructure/database/session.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from shared.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20)
# expire_on_commit=False required in async SA — prevents MissingGreenlet errors when
# accessing model attributes after commit outside an active session context
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

### Query Best Practices

```python
# ✅ Select specific columns
from sqlalchemy import select

result = await db.execute(
    select(UserModel.id, UserModel.email, UserModel.name)
    .where(UserModel.id == user_id)
)
user = result.one_or_none()

# ✅ Pagination
result = await db.execute(
    select(UserModel)
    .order_by(UserModel.created_at.desc())
    .offset((page - 1) * limit)
    .limit(limit)
)

# ✅ Prevent N+1 — eager load relationships
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(UserModel).options(selectinload(UserModel.orders))
)
```

### Transactions (SQLAlchemy)

```python
# ✅ Atomic operations — db is AsyncSession from get_db()
async with session.begin():
    order = OrderModel(**order_data)
    session.add(order)
    await session.execute(
        update(InventoryModel)
        .where(InventoryModel.product_id == product_id)
        .values(stock=InventoryModel.stock - 1)
    )
# session.begin() commits on exit, rolls back on exception
```

### Alembic Migrations

```bash
# Create migration
alembic revision --autogenerate -m "add_users_table"

# Apply to DB
alembic upgrade head

# Rollback one step
alembic downgrade -1
```
