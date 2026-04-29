"""Telegram bot handler for psi-agent."""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from psi_agent.channel.telegram.client import TelegramClient
from psi_agent.channel.telegram.config import TelegramConfig

TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def split_message(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """Split a message into chunks that fit within Telegram's character limit.

    Args:
        text: The text to split.
        max_length: Maximum length per chunk (default: 4096).

    Returns:
        List of text chunks.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # Try to split at a newline or space near the limit
        split_pos = max_length
        newline_pos = remaining.rfind("\n", 0, max_length)
        space_pos = remaining.rfind(" ", 0, max_length)

        if newline_pos > max_length // 2:
            split_pos = newline_pos + 1
        elif space_pos > max_length // 2:
            split_pos = space_pos + 1

        chunks.append(remaining[:split_pos])
        remaining = remaining[split_pos:]

    return chunks


class TelegramBot:
    """Telegram bot handler for psi-agent."""

    def __init__(self, config: TelegramConfig) -> None:
        """Initialize the bot.

        Args:
            config: The configuration for the bot.
        """
        self.config = config
        self.client = TelegramClient(config)
        self._app: Application[Any, Any, Any, Any, Any, Any] | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Start the Telegram bot."""
        builder = Application.builder().token(self.config.token)

        # Configure proxy if provided
        if self.config.proxy:
            builder = builder.proxy(self.config.proxy)
            # Log proxy without credentials (show host only)
            proxy_display = (
                self.config.proxy.split("@")[-1] if "@" in self.config.proxy else self.config.proxy
            )
            logger.debug(f"Using proxy: {proxy_display}")

        self._app = builder.build()

        # Add handlers
        self._app.add_handler(CommandHandler("start", self._start_command))
        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

        logger.info("Starting Telegram bot polling")

        async with self.client:
            await self._app.initialize()
            await self._app.start()
            assert self._app is not None
            assert self._app.updater is not None
            await self._app.updater.start_polling()

            # Keep running until stopped
            try:
                await self._stop_event.wait()
            finally:
                await self._stop()

    async def _stop(self) -> None:
        """Stop the bot gracefully."""
        if self._app is not None:
            logger.info("Stopping Telegram bot")
            if self._app.updater is not None:
                await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    async def _start_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - ignore it.

        Args:
            update: The Telegram update.
            _context: The callback context.
        """
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.debug(f"Received /start from user {user_id}, ignoring")

    async def _handle_message(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text message.

        Args:
            update: The Telegram update.
            _context: The callback context.
        """
        if update.message is None or update.message.text is None:
            return

        user = update.effective_user
        if user is None:
            return

        user_id = f"telegram:{user.id}"
        message_text = update.message.text

        logger.info(f"Received message from {user_id}: {message_text[:50]}...")

        # Forward to session
        response = await self.client.send_message(message_text, user_id)

        # Split and send response
        chunks = split_message(response)
        for chunk in chunks:
            try:
                await update.message.reply_text(chunk)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                break
