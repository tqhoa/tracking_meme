# Security Rules

## 🚨 CRITICAL — Never Violate These

- **Never** hardcode secrets, API keys, passwords, or tokens in source code
- **Never** commit `.env` files to version control
- **Never** log sensitive data (passwords, tokens, PII)
- **Never** use `eval()` / `Function()` (JS) or `exec()` / `eval()` (Python) with user input
- **Always** validate all user inputs at system boundaries

---

## Environment Variables

**JavaScript:**

```js
// ✅ Always use environment variables for secrets
const dbPassword = process.env.DB_PASSWORD;
const jwtSecret = process.env.JWT_SECRET;

// ❌ Never hardcode secrets
const dbPassword = "mypassword123";
```

**Python (pydantic-settings):**

```python
# ✅ shared/config.py — loaded once, validated at startup
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    bcrypt_rounds: int = 12

    class Config:
        env_file = ".env"

settings = Settings()  # raises ValidationError if any required var is missing
```

---

## Input Validation

**JavaScript (Zod):**

```js
// ✅ Validate all incoming data with a schema
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128),
});

// Sanitize HTML to prevent XSS (client-side rendering)
import DOMPurify from "dompurify";
const cleanContent = DOMPurify.sanitize(userInput);
```

**Python (Pydantic v2):**

```python
# ✅ FastAPI validates all request bodies against Pydantic schemas automatically
from pydantic import BaseModel, EmailStr, field_validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 128:
            raise ValueError('Password must be 8-128 characters')
        return v
```

---

## Authentication

- Use **JWT** with short expiry (15 min access token, 7 day refresh token)
- Hash passwords with **bcrypt** (rounds: 12+)
- Implement rate limiting on auth endpoints

**JavaScript:**

```js
import bcrypt from "bcrypt";
const SALT_ROUNDS = 12;
const hashed = await bcrypt.hash(password, SALT_ROUNDS);
const valid = await bcrypt.compare(plain, hashed);
```

**Python (passlib):**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

## Authorization

**JavaScript:**

```js
// ✅ Check permissions on every protected route
router.delete(
  "/posts/:id",
  authenticate,
  authorize("admin"),
  asyncHandler(deletePost),
);

// ✅ Verify resource ownership
if (post.authorId !== req.user.id && req.user.role !== "admin") {
  throw new AppError("Forbidden", 403);
}
```

**Python (FastAPI dependency):**

```python
# ✅ Inject auth dependency on every protected endpoint
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    ...

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await post_repo.find_by_id(post_id)
    if post.author_id != current_user.id and current_user.role != "admin":
        raise AppError("Forbidden", 403, "ACCESS_DENIED")
```

---

## HTTP Security Headers

**JavaScript (Helmet.js):**

```js
import helmet from "helmet";
app.use(helmet());

app.use(
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(",") || [],
    credentials: true,
  }),
);
```

**Python (FastAPI + starlette):**

```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)  # production only
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # explicit list, never ["*"] in prod
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Rate Limiting

**JavaScript (express-rate-limit):**

```js
import rateLimit from "express-rate-limit";

const apiLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 });
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 5 });

app.use("/api/", apiLimiter);
app.use("/api/auth/", authLimiter);
```

**Python (slowapi):**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/auth/login")
@limiter.limit("5/15minutes")
async def login(request: Request, body: LoginRequest):
    ...
```

---

## SQL Injection Prevention

- Always use ORM — never raw string concatenation
- If raw SQL is needed, use **parameterized queries**

```python
# ❌ Never
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ SQLAlchemy parameterized
result = await db.execute(select(UserModel).where(UserModel.email == email))

# ✅ Raw SQL with parameters (last resort)
result = await db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```

---

## Dependency Security

```bash
# JavaScript
npm audit
npm audit fix

# Python
pip-audit
pip-audit --fix
```
