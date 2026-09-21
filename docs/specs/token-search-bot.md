# Feature: Token Search Bot

## Objective

Build 2 services: a FastAPI token data API and a Telegram bot that lets users paste a contract address in natural language, then returns a Vietnamese market report with risk analysis.

## Target Users

Crypto traders/meme coin hunters using Telegram who want a fast token lookup without needing to know which chain or use specific commands.

## Layer

- [x] Backend only (FastAPI) — `api` service
- [x] Bot service (Python + python-telegram-bot) — `bot` service

---

## Architecture Overview

```
Telegram User
     │ natural language + contract address
     ▼
[bot service]
     │ POST /api/v1/token/search
     ▼
[api service]
     ├── parallel: GMGN info + GMGN security
     │       └── fallback: DexScreener (if GMGN no data)
     ├── parallel: GoPlus security check
     └── Claude Haiku: generate risk analysis (Vietnamese)
     │
     ▼
Structured TokenReport JSON
     │
     ▼
[bot service] formats + sends to Telegram
```

---

## Services

### Service 1: `api` (FastAPI)

Port: `8000`

#### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/token/search` | Main token lookup |
| `GET`  | `/api/v1/health` | Health check |

#### POST /api/v1/token/search

**Request:**
```json
{
  "address": "0x8FB3...",
  "chain": null
}
```
- `chain`: optional — `"eth"` or `"bsc"`. If null → auto-detect.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "token": {
      "address": "0x...",
      "name": "Henry",
      "symbol": "HENRY",
      "chain": "eth",
      "dex": "uniswap_v2"
    },
    "market": {
      "price_usd": 0.000285,
      "market_cap": 285000,
      "fdv": 285000,
      "liquidity_usd": 41000,
      "volume": {
        "m5": 1200,
        "h1": 74000,
        "h6": 1820000,
        "h24": 2190000
      },
      "price_change": {
        "m5": 3.67,
        "h1": -8.47,
        "h6": 274.0,
        "h24": 23572.0
      },
      "txns_h24": {
        "buys": 4220,
        "sells": 3779
      }
    },
    "security": {
      "is_honeypot": false,
      "buy_tax": 0,
      "sell_tax": 0,
      "is_open_source": true,
      "owner_address": "0x...",
      "creator_address": "0x...",
      "holder_count": 1200,
      "top_10_holders_pct": 45.2,
      "lp_locked": false,
      "goplus_score": null
    },
    "social": {
      "twitter": "https://twitter.com/...",
      "website": null,
      "telegram": null
    },
    "analysis": {
      "risk_flags": [
        "Volume 24h gấp ~8x MCap — dấu hiệu pump/dump",
        "Liquidity chỉ $41K — dễ slippage cao",
        "Không có website chính thức"
      ],
      "positive_flags": [
        "Tỉ lệ buy/sell cân bằng (4220/3779)",
        "Volume thực với 8000+ giao dịch/24h"
      ],
      "summary": "Token rủi ro cao. Có dấu hiệu pump ngắn hạn. Không phù hợp đầu tư dài hạn.",
      "risk_level": "HIGH"
    },
    "data_source": "dexscreener",
    "fetched_at": "2026-09-21T10:00:00Z"
  }
}
```

**Error responses:**
```json
{ "success": false, "error": { "code": "TOKEN_NOT_FOUND", "message": "..." } }
{ "success": false, "error": { "code": "CHAIN_NOT_DETECTED", "message": "..." } }
{ "success": false, "error": { "code": "INVALID_ADDRESS", "message": "..." } }
```

#### Data Fetching Logic

```
1. Validate address format (EVM: 0x + 40 hex chars)
2. If chain=null → try GMGN eth first, then GMGN bsc
3. If GMGN no data → fallback DexScreener (auto-detects chain)
4. Parallel: [market data fetch] + [GoPlus security check]
5. Claude Haiku: generate risk_flags, positive_flags, summary, risk_level
6. Return unified TokenReport
```

#### Supported Chains

| Chain | ID | GMGN slug | DexScreener slug | GoPlus chain_id |
|-------|----|-----------|------------------|-----------------|
| Ethereum | `eth` | `eth` | `ethereum` | `1` |
| BSC | `bsc` | `bsc` | `bsc` | `56` |

#### External APIs

| API | Purpose | Auth |
|-----|---------|------|
| GMGN `https://gmgn.ai/defi/quotation/v1/` | Market info + security | No key (public) |
| DexScreener `https://api.dexscreener.com/latest/dex/` | Fallback market data | No key |
| GoPlus `https://api.gopluslabs.io/api/v1/token_security/` | Security analysis | Optional API key |
| Anthropic API | Risk analysis generation | `ANTHROPIC_API_KEY` |

---

### Service 2: `bot` (Telegram Bot)

Uses `python-telegram-bot` (async).

#### Bot Behavior

1. User sends any message containing an EVM address (`0x[40 hex]`)
2. Bot extracts address via regex — no specific command needed
3. Bot sends "🔍 Đang tra cứu..." typing indicator
4. Bot calls `POST api:8000/api/v1/token/search`
5. Bot formats and sends Vietnamese report

#### Message Format (output)

```
🔍 *$HENRY* — Ethereum Mainnet
📍 `0x8FB3...` | Uniswap v2

💰 *Thị trường*
• Giá: $0.000285
• MCap: $285K | FDV: $285K
• Liquidity: $41K ⚠️ Thấp

📈 *Biến động giá*
• 5m: +3.67% | 1h: -8.47% | 6h: +274% | 24h: +23,572%

📊 *Volume 24h*
• $2.19M (~8x MCap) 🚨 Bất thường
• 6h: $1.82M | 1h: $74K

🔄 *Giao dịch 24h*
• Mua: 4,220 | Bán: 3,779

🔒 *Security*
• Honeypot: ✅ Không
• Tax mua/bán: 0% / 0%
• LP Locked: ❌

🌐 *Social*
• Twitter: @... | Website: ❌

⚠️ *Rủi ro: CAO*
🚩 Volume 24h gấp ~8x MCap — dấu hiệu pump/dump
🚩 Liquidity thấp $41K — dễ slippage
🚩 Không có website

✅ *Tín hiệu tốt*
• Buy/sell cân bằng (4220/3779)
• Volume thực 8000+ txns/24h

📝 *Nhận định:* Token rủi ro cao...

🕐 _Dữ liệu từ: DexScreener | 10:00 21/09/2026_
```

#### Commands

| Command | Action |
|---------|--------|
| `/start` | Hướng dẫn sử dụng |
| `/help` | Giống /start |

---

## Project Structure

```
bot-meme/
├── api/                        # FastAPI service
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py           # pydantic-settings
│   │   ├── routes/
│   │   │   └── token.py
│   │   ├── services/
│   │   │   ├── token_service.py    # orchestration
│   │   │   ├── gmgn_client.py
│   │   │   ├── dexscreener_client.py
│   │   │   ├── goplus_client.py
│   │   │   └── analysis_service.py # Claude Haiku
│   │   ├── schemas/
│   │   │   └── token.py
│   │   └── exceptions.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── bot/                        # Telegram bot service
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── handlers/
│   │   │   ├── message.py      # address detection
│   │   │   └── commands.py
│   │   ├── services/
│   │   │   └── api_client.py   # calls api service
│   │   └── formatters/
│   │       └── report.py       # format TokenReport → Telegram markdown
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
└── .env.example
```

---

## Environment Variables

```bash
# api service
ANTHROPIC_API_KEY=sk-ant-...
GOPLUS_API_KEY=               # optional, empty = free tier
LOG_LEVEL=info
ENVIRONMENT=development

# bot service
TELEGRAM_BOT_TOKEN=...
API_BASE_URL=http://api:8000
LOG_LEVEL=info
```

---

## Core Features & Acceptance Criteria

| # | Feature | Acceptance Criteria |
|---|---------|---------------------|
| 1 | Auto-detect contract address | Regex extracts `0x[40 hex]` from any message |
| 2 | Chain auto-detect | ETH/BSC detected without user specifying |
| 3 | GMGN → DexScreener fallback | If GMGN 404/empty → DexScreener used transparently |
| 4 | Parallel fetch | Market + security fetched concurrently (`asyncio.gather`) |
| 5 | GoPlus security | Honeypot, tax, LP lock, holder distribution returned |
| 6 | Claude Haiku analysis | risk_flags, positive_flags, summary, risk_level in Vietnamese |
| 7 | Formatted Telegram report | All data sections + risk analysis sent as single message |
| 8 | Error handling | TOKEN_NOT_FOUND, INVALID_ADDRESS, API timeouts handled gracefully |

---

## Out of Scope (MVP)

- Solana / Base chains
- Price alerts / watchlist
- User authentication
- Database persistence
- Rate limiting per user
- Inline keyboard buttons

---

## Testing Strategy

- Unit: `token_service.py` logic, address regex, chain detection
- Integration: `POST /api/v1/token/search` with mocked external APIs
- Coverage target: ≥ 80%

---

## Mandatory Standards

- Python 3.12, FastAPI, async/await everywhere
- httpx for all external calls (async)
- pydantic-settings for config
- structlog for logging
- No secrets in code — `.env` only
- AppError class for all domain errors
