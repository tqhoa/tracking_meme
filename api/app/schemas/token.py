import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

_EVM_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]


class TokenSearchRequest(BaseModel):
    address: str
    chain: Literal["eth", "bsc"] | None = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not _EVM_RE.match(v):
            raise ValueError("Invalid EVM address")
        return v.lower()


class TokenInfo(BaseModel):
    address: str
    name: str
    symbol: str
    chain: str
    dex: str | None = None


class VolumeData(BaseModel):
    m5: float = 0
    h1: float = 0
    h6: float = 0
    h24: float = 0


class PriceChange(BaseModel):
    m5: float = 0
    h1: float = 0
    h6: float = 0
    h24: float = 0


class TxnCount(BaseModel):
    buys: int = 0
    sells: int = 0


class MarketData(BaseModel):
    price_usd: float = 0
    market_cap: float = 0
    fdv: float = 0
    liquidity_usd: float = 0
    volume: VolumeData = VolumeData()
    price_change: PriceChange = PriceChange()
    txns_h24: TxnCount = TxnCount()


class SecurityData(BaseModel):
    is_honeypot: bool | None = None
    buy_tax: float | None = None
    sell_tax: float | None = None
    is_open_source: bool | None = None
    owner_address: str | None = None
    creator_address: str | None = None
    holder_count: int | None = None
    top_10_holders_pct: float | None = None
    lp_locked: bool | None = None


class SocialData(BaseModel):
    twitter: str | None = None
    website: str | None = None
    telegram: str | None = None


class AnalysisResult(BaseModel):
    risk_flags: list[str] = []
    positive_flags: list[str] = []
    summary: str = ""
    risk_level: RiskLevel = "MEDIUM"


class TokenReport(BaseModel):
    token: TokenInfo
    market: MarketData
    security: SecurityData
    social: SocialData
    analysis: AnalysisResult
    data_source: str
    fetched_at: datetime


class ApiResponse(BaseModel):
    success: bool
    data: TokenReport | None = None
    error: dict[str, str] | None = None
