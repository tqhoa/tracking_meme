import logging

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from app.config import get_settings
from app.formatters.report import format_report
from app.services.api_client import ApiClient
from app.utils.address import extract_evm_address

logger = logging.getLogger(__name__)

_ERROR_MESSAGES = {
    "TOKEN_NOT_FOUND": "❌ Không tìm thấy token với địa chỉ này.",
    "INVALID_ADDRESS": "❌ Địa chỉ không hợp lệ.",
    "NETWORK_ERROR": "❌ Không thể kết nối tới server. Thử lại sau.",
}
_DEFAULT_ERROR = "❌ Có lỗi xảy ra khi tra cứu token."
_MAX_MSG_LEN = 4096


async def _send_report(update: Update, text: str) -> None:
    """Split at 4096 chars; fallback to plain text when Markdown parse fails."""
    chunks = [text[i : i + _MAX_MSG_LEN] for i in range(0, len(text), _MAX_MSG_LEN)]
    for chunk in chunks:
        try:
            await update.message.reply_text(chunk, parse_mode="Markdown")  # type: ignore[union-attr]
        except TelegramError:
            # Dynamic content (names, summaries) may contain unescaped Markdown chars
            try:
                await update.message.reply_text(chunk)  # type: ignore[union-attr]
            except TelegramError:
                logger.exception("message.send_failed")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    address = extract_evm_address(update.message.text)
    if not address:
        return

    await update.message.reply_text("🔍 Đang tra cứu...")

    settings = get_settings()
    client = ApiClient(base_url=settings.api_base_url)
    result = await client.search_token(address)

    if not result.get("success"):
        error = result.get("error") or {}
        code = error.get("code", "UNKNOWN")
        msg = _ERROR_MESSAGES.get(code, _DEFAULT_ERROR)
        await update.message.reply_text(msg)
        return

    try:
        report_text = format_report(result["data"])
    except Exception:
        logger.exception("message.format_failed", extra={"address": address})
        await update.message.reply_text(_DEFAULT_ERROR)
        return

    await _send_report(update, report_text)
