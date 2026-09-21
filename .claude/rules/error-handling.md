# Error Handling

## Core Principles

- **Never swallow errors silently** — always log or rethrow
- Use a centralized error handler
- Return consistent error responses to the API
- Distinguish between operational errors (expected) and programmer errors (bugs)

---

## JavaScript / Express

### Custom Error Class

```js
// src/utils/app-error.js
class AppError extends Error {
  constructor(message, statusCode = 500, code = "INTERNAL_ERROR") {
    super(message);
    this.name = "AppError";
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export default AppError;
```

### Throwing Errors

```js
if (!user) throw new AppError("User not found", 404, "USER_NOT_FOUND");
if (!hasPermission) throw new AppError("Forbidden", 403, "ACCESS_DENIED");
```

### Async Error Handling

```js
// ✅ Wrap async route handlers
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

router.get(
  "/users/:id",
  asyncHandler(async (req, res) => {
    const user = await userService.findById(req.params.id);
    res.json({ success: true, data: user });
  }),
);
```

### Global Error Handler (Express)

```js
// middleware/error-handler.js
export function errorHandler(err, req, res, next) {
  const statusCode = err.statusCode || 500;
  logger.error({ err, req: { method: req.method, url: req.url } });

  if (!err.isOperational) {
    return res.status(500).json({
      success: false,
      error: {
        code: "INTERNAL_ERROR",
        message: "An unexpected error occurred",
      },
    });
  }

  res.status(statusCode).json({
    success: false,
    error: { code: err.code, message: err.message },
  });
}
```

### Validation Errors (Zod)

```js
const result = userSchema.safeParse(data);
if (!result.success) {
  throw new AppError("Validation failed", 422, "VALIDATION_ERROR");
}
```

---

## Python / FastAPI

### AppError Class

```python
# shared/exceptions.py
class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)
```

### Throwing Errors

```python
if not user:
    raise AppError("User not found", 404, "USER_NOT_FOUND")

if not has_permission:
    raise AppError("Forbidden", 403, "ACCESS_DENIED")
```

### Global Exception Handlers (FastAPI)

```python
# main.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from shared.exceptions import AppError


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": exc.errors(),
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_error", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
```

### Catching Specific Exceptions

```python
# ✅ Catch specific, preserve traceback with 'from'
try:
    user = await user_repo.find_by_id(user_id)
except sqlalchemy.exc.OperationalError as exc:
    raise AppError("Database unavailable", 503) from exc

# ❌ Never silence exceptions
try:
    do_something()
except Exception:
    pass  # ❌

# ✅ Log and re-raise if you can't handle it
try:
    do_something()
except Exception:
    logger.error("unexpected_error", exc_info=True)
    raise
```
