import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

_subscribed_chats: set[int] = set()


def get_subscribed_chats() -> set[int]:
    return _subscribed_chats.copy()


async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return

    chat_id = update.effective_chat.id
    args = context.args or []

    if not args:
        status = "bật ✅" if chat_id in _subscribed_chats else "tắt ❌"
        await update.message.reply_text(
            f"📡 *Volume Alert*: {status}\n\n"
            "Dùng `/alert on` để bật, `/alert off` để tắt.\n"
            "Bot sẽ thông báo top token volume cao mỗi 5 phút.",
            parse_mode="Markdown",
        )
        return

    action = args[0].lower()
    if action == "on":
        _subscribed_chats.add(chat_id)
        logger.info("alert.subscribed", extra={"chat_id": chat_id})
        await update.message.reply_text(
            "✅ *Volume Alert bật!*\n"
            "Bot sẽ gửi top token có volume cao mỗi 5 phút.\n\n"
            "Dùng `/alert off` để tắt.",
            parse_mode="Markdown",
        )
    elif action == "off":
        _subscribed_chats.discard(chat_id)
        logger.info("alert.unsubscribed", extra={"chat_id": chat_id})
        await update.message.reply_text("❌ Đã tắt Volume Alert.")
    else:
        await update.message.reply_text(
            "Cú pháp: `/alert on` hoặc `/alert off`",
            parse_mode="Markdown",
        )
