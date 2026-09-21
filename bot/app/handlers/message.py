from telegram import Update
from telegram.ext import ContextTypes

from app.config import get_settings
from app.formatters.report import format_report
from app.services.api_client import ApiClient
from app.utils.address import extract_evm_address

_ERROR_MESSAGES = {
    "TOKEN_NOT_FOUND": "❌ Không tìm thấy token với địa chỉ này.",
    "INVALID_ADDRESS": "❌ Địa chỉ không hợp lệ.",
    "NETWORK_ERROR": "❌ Không thể kết nối tới server. Thử lại sau.",
}
_DEFAULT_ERROR = "❌ Có lỗi xảy ra khi tra cứu token."


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

    report_text = format_report(result["data"])
    await update.message.reply_text(report_text, parse_mode="Markdown")
