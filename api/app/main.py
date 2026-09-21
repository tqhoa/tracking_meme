from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exceptions import register_exception_handlers
from app.routes import token

app = FastAPI(title="Token Search API", version="1.0.0")

register_exception_handlers(app)
app.include_router(token.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
