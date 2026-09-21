# Plan: Token Search Bot

**Spec**: `docs/specs/token-search-bot.md`
**Layer**: Backend (FastAPI API) + Bot (python-telegram-bot)

---

## Phase 1: Foundation

- [x] **Task 1.1**: Project scaffolding + Docker Compose
  - `docker-compose.yml`, `.env.example`
  - `api/Dockerfile`, `api/requirements.txt`
  - `bot/Dockerfile`, `bot/requirements.txt`
  - `api/app/main.py` (bare FastAPI app, health endpoint)
  - `bot/app/main.py` (bare PTB Application, /start command)
  - **AC**: `docker compose up` starts both services, `GET /api/v1/health` returns `{"status":"ok"}`

- [x] **Task 1.2**: API config + schemas + exceptions
  - `api/app/config.py` (pydantic-settings: ANTHROPIC_API_KEY, GOPLUS_API_KEY, LOG_LEVEL)
  - `api/app/schemas/token.py` (TokenSearchRequest, TokenInfo, MarketData, SecurityData, SocialData, AnalysisResult, TokenReport, ApiResponse)
  - `api/app/exceptions.py` (AppError + FastAPI exception handlers: INVALID_ADDRESS, TOKEN_NOT_FOUND, CHAIN_NOT_DETECTED, UPSTREAM_ERROR)
  - **Test**: `tests/api/unit/test_schemas.py` — Pydantic validation, address regex
  - **AC**: Invalid address → 400 INVALID_ADDRESS; schemas serialize correctly

- [x] **Task 1.3**: Bot config + address extractor
  - `bot/app/config.py` (TELEGRAM_BOT_TOKEN, API_BASE_URL)
  - `bot/app/utils/address.py` — `extract_evm_address(text) -> str | None` (regex `0x[0-9a-fA-F]{40}`)
  - **Test**: `tests/bot/unit/test_address.py` — valid/invalid/embedded addresses
  - **AC**: Extracts address from natural language message; returns None if none found

---

## Checkpoint: Foundation Complete

- [ ] `docker compose up` — both containers start healthy
- [ ] `GET /api/v1/health` → 200
- [ ] Schemas validate correctly
- [ ] Address regex passes all unit tests

---

## Phase 2: API Data Clients

- [x] **Task 2.1**: DexScreener client
  - `api/app/services/dexscreener_client.py`
  - `fetch_by_address(address, chain=None) -> dict | None`
  - Hits `GET /latest/dex/tokens/{address}`
  - Parses: name, symbol, chain, dex, price, mcap, fdv, liquidity, volume, price_change, txns, social links
  - Returns `None` if no pairs found
  - **Test**: `tests/api/unit/test_dexscreener_client.py` — mock httpx responses, parse logic, None on empty
  - **AC**: Returns parsed dict for valid token; None for unknown address

- [x] **Task 2.2**: GMGN client
  - `api/app/services/gmgn_client.py`
  - `fetch_token_info(address, chain) -> dict | None`
  - `fetch_token_security(address, chain) -> dict | None`
  - Hits GMGN quotation API for ETH and BSC
  - Returns `None` on 404 or empty data
  - **Test**: `tests/api/unit/test_gmgn_client.py` — mock responses, 404 → None
  - **AC**: Returns data for known token; None triggers fallback

- [x] **Task 2.3**: GoPlus security client
  - `api/app/services/goplus_client.py`
  - `fetch_security(address, chain_id) -> dict | None`
  - Hits `GET /api/v1/token_security/{chain_id}?contract_addresses={address}`
  - Parses: is_honeypot, buy_tax, sell_tax, is_open_source, owner_address, creator_address, holder_count, top_10_holders_pct, lp_locked
  - **Test**: `tests/api/unit/test_goplus_client.py` — mock response parsing
  - **AC**: Returns SecurityData fields; None on API error (non-blocking)

---

## Checkpoint: Clients Complete

- [ ] All 3 clients return correct parsed data from mocked responses
- [ ] All return `None` on error/empty (no exceptions leak up)
- [ ] Coverage ≥ 80% on client files

---

## Phase 3: API Orchestration

- [x] **Task 3.1**: Chain detection + GMGN→DexScreener fallback logic
  - `api/app/services/token_service.py` — `resolve_market_data(address, chain)`
  - Logic:
    1. If chain given → try GMGN(chain) → fallback DexScreener(chain)
    2. If chain=None → try GMGN(eth) → try GMGN(bsc) → try DexScreener(auto)
    3. Raise `TOKEN_NOT_FOUND` if all sources return None
  - **Test**: `tests/api/unit/test_token_service.py` — all fallback paths mocked
  - **AC**: Correct source selected; chain detected from DexScreener response; TOKEN_NOT_FOUND raised when all fail

- [x] **Task 3.2**: Parallel fetch orchestration
  - `token_service.py` — `search(address, chain) -> TokenReport`
  - `asyncio.gather(resolve_market_data(...), goplus_client.fetch_security(...))`
  - Security failure = non-fatal (returns None, continues)
  - **Test**: `tests/api/unit/test_token_service.py` — verify gather called, security None handled
  - **AC**: Both fetches run concurrently; GoPlus failure doesn't block market data

- [x] **Task 3.3**: Claude Haiku analysis service
  - `api/app/services/analysis_service.py` — `generate_analysis(market, security, social) -> AnalysisResult`
  - Sends structured prompt to Claude Haiku (`claude-haiku-4-5-20251001`)
  - Prompt asks for: risk_flags (list), positive_flags (list), summary (1 sentence), risk_level (LOW/MEDIUM/HIGH/VERY_HIGH)
  - Uses tool_use / structured output to avoid hallucinated JSON
  - Falls back to heuristic analysis if API fails
  - **Test**: `tests/api/unit/test_analysis_service.py` — mock Anthropic response, fallback path
  - **AC**: Returns AnalysisResult with all 4 fields; API failure → heuristic fallback (no crash)

- [x] **Task 3.4**: POST /api/v1/token/search endpoint (integration)
  - `api/app/routes/token.py` — wires request → token_service.search → response
  - Input validation: address format (Pydantic)
  - **Test**: `tests/api/integration/test_token_route.py` — mock all external calls, test happy path + error paths
  - **AC**:
    - Valid address + found token → 200 with full TokenReport
    - Invalid address format → 400 INVALID_ADDRESS
    - Token not found → 404 TOKEN_NOT_FOUND
    - Response matches `api-conventions.md` envelope

---

## Checkpoint: API Complete

- [ ] `POST /api/v1/token/search` works end-to-end (mocked externals)
- [ ] All 3 error codes return correctly
- [ ] Parallel fetch confirmed via test
- [ ] Coverage ≥ 80% on api/app/
- [ ] No mypy errors

---

## Phase 4: Bot Service

- [x] **Task 4.1**: API client in bot service
  - `bot/app/services/api_client.py` — `search_token(address) -> dict`
  - Calls `POST {API_BASE_URL}/api/v1/token/search`
  - Maps API errors (404, 400) to user-friendly Vietnamese error messages
  - 30s timeout, retries once on connection error
  - **Test**: `tests/bot/unit/test_api_client.py` — mock httpx, error mapping
  - **AC**: Returns parsed dict on success; returns error string on failure (no crash)

- [x] **Task 4.2**: Report formatter
  - `bot/app/formatters/report.py` — `format_report(data: dict) -> str`
  - Formats TokenReport dict → Telegram MarkdownV2 message (spec format)
  - Helper: `format_number(n)` → `$285K`, `$2.19M`
  - Helper: `format_pct(n)` → `+3.67%` with sign
  - Risk level → emoji: HIGH=⚠️, VERY_HIGH=🚨, MEDIUM=🟡, LOW=✅
  - **Test**: `tests/bot/unit/test_report_formatter.py` — snapshot test on full TokenReport dict
  - **AC**: Output matches spec message format; no MarkdownV2 escape errors

- [x] **Task 4.3**: Message handler + bot wiring
  - `bot/app/handlers/message.py` — `handle_message(update, context)`
    1. Extract address via `address.extract_evm_address(text)`
    2. If no address → ignore (non-command messages)
    3. Send typing action
    4. Call api_client.search_token
    5. Format + send report
  - `bot/app/handlers/commands.py` — `/start`, `/help` → usage instructions
  - `bot/app/main.py` — wire all handlers into PTB Application
  - **Test**: `tests/bot/integration/test_message_handler.py` — mock api_client, verify send_message called with formatted report
  - **AC**:
    - Message with address → report sent
    - Message without address → no response
    - TOKEN_NOT_FOUND → "❌ Không tìm thấy token..." sent
    - INVALID_ADDRESS → "❌ Địa chỉ không hợp lệ..." sent

---

## Checkpoint: Bot Complete

- [ ] Bot receives message → sends formatted report (manual smoke test)
- [ ] Error messages display correctly in Vietnamese
- [ ] Coverage ≥ 80% on bot/app/
- [ ] No mypy errors

---

## Phase 5: Integration & Polish

- [x] **Task 5.1**: Live smoke test against real APIs
  - Test with known ETH token (e.g. USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`)
  - Test with BSC token
  - Test with unknown address → TOKEN_NOT_FOUND
  - Document any GMGN rate limits or bot detection encountered

- [x] **Task 5.2**: Heuristic analysis fallback (if Claude API unavailable)
  - `analysis_service.py` — `_heuristic_analysis(market, security) -> AnalysisResult`
  - Rules:
    - volume_24h > 5x mcap → risk flag
    - liquidity_usd < 50K → risk flag
    - price_change_24h > 1000% → risk flag
    - is_honeypot → VERY_HIGH immediately
    - buy_tax > 10% or sell_tax > 10% → risk flag
    - lp_locked = False → risk flag
  - **AC**: Returns sensible risk_level without Claude API

- [x] **Task 5.3**: Logging + error observability
  - structlog bound context: `service`, `address`, `chain`, `data_source`
  - Log: request received, source selected, parallel fetch duration, analysis duration
  - **AC**: Each request produces structured log entries with address + timings

- [x] **Task 5.4**: Coverage audit
  - `pytest --cov=api/app --cov=bot/app --cov-report=term-missing --cov-fail-under=80`
  - Fill gaps if < 80%

---

## Checkpoint: Ship Ready

- [ ] `docker compose up` — both services start, no errors
- [ ] End-to-end: paste real ETH contract in Telegram → full report received
- [ ] All error paths tested (invalid address, not found, API timeout)
- [ ] Coverage ≥ 80%
- [ ] No hardcoded secrets
- [ ] `.env.example` documents all required vars

---

## Dependency Graph

```
1.1 (scaffold)
 └─ 1.2 (schemas/exceptions)
 └─ 1.3 (bot address util)
      └─ 2.1 (dexscreener)
      └─ 2.2 (gmgn)
      └─ 2.3 (goplus)
           └─ 3.1 (chain detection + fallback)
           └─ 3.2 (parallel fetch)  ← needs 2.1, 2.2, 2.3
           └─ 3.3 (analysis service)
                └─ 3.4 (route endpoint) ← needs 3.1, 3.2, 3.3
                     └─ 4.1 (bot api client)
                     └─ 4.2 (formatter)
                          └─ 4.3 (message handler)
                               └─ 5.1–5.4 (polish)
```

## Estimated Order

1.1 → 1.2 → 1.3 → 2.1 → 2.2 → 2.3 → 3.1 → 3.2 → 3.3 → 3.4 → 4.1 → 4.2 → 4.3 → 5.1 → 5.2 → 5.3 → 5.4
