from unittest.mock import AsyncMock, MagicMock


async def test_start_replies_with_help_text() -> None:
    from app.handlers.commands import start

    update = MagicMock()
    update.message.reply_text = AsyncMock()
    ctx = MagicMock()

    await start(update, ctx)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Token Search Bot" in text


async def test_help_replies_with_help_text() -> None:
    from app.handlers.commands import help_command

    update = MagicMock()
    update.message.reply_text = AsyncMock()
    ctx = MagicMock()

    await help_command(update, ctx)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Token Search Bot" in text


async def test_start_no_message_does_nothing() -> None:
    from app.handlers.commands import start

    update = MagicMock()
    update.message = None
    ctx = MagicMock()

    await start(update, ctx)  # should not raise
