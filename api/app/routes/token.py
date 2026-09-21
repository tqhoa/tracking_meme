from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.exceptions import AppError
from app.schemas.token import (
    AnalysisResult,
    MarketData,
    SecurityData,
    SocialData,
    TokenInfo,
    TokenReport,
    TokenSearchRequest,
)
from app.services.analysis_service import AnalysisService
from app.services.dexscreener_client import DexScreenerClient
from app.services.gmgn_client import GmgnClient
from app.services.goplus_client import GoplusClient
from app.services.token_service import TokenService

router = APIRouter()


def _build_service() -> TokenService:
    settings = get_settings()
    return TokenService(
        gmgn=GmgnClient(),
        dex=DexScreenerClient(),
        goplus=GoplusClient(api_key=settings.goplus_api_key),
        analysis=AnalysisService(api_key=settings.anthropic_api_key),
    )


@router.post("/token/search")
async def search_token(body: TokenSearchRequest) -> JSONResponse:
    svc = _build_service()
    raw = await svc.search(body.address, body.chain)

    report = TokenReport(
        token=TokenInfo(**raw["token"]),
        market=MarketData(**raw["market"]),
        security=SecurityData(**raw["security"]),
        social=SocialData(**raw["social"]),
        analysis=AnalysisResult(**raw["analysis"]),
        data_source=raw["data_source"],
        fetched_at=raw["fetched_at"],
    )
    return JSONResponse({"success": True, "data": report.model_dump(mode="json")})
