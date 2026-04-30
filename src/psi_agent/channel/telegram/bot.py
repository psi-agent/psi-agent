"""Telegram bot handler for psi-agent."""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any
from urllib.parse import urlparse, urlunparse

from loguru import logger
from telegram import Update
from telegram.constants import ChatAction
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
            proxy_display = self._mask_proxy_credentials(self.config.proxy)
            logger.info(f"Using proxy: {proxy_display}")

        try:
            self._app = builder.build()
        except ImportError as e:
            if "socksio" in str(e).lower():
                msg = (
                    "SOCKS5 proxy support requires the 'socksio' package.\n"
                    "Install it with one of:\n"
                    "  pip install 'python-telegram-bot[socks]'\n"
                    "  uv sync --extra socks"
                )
                raise RuntimeError(msg) from e
            raise
        except RuntimeError as e:
            if "Socks5 proxies" in str(e):
                msg = (
                    "SOCKS5 proxy support requires the 'socksio' package.\n"
                    "Install it with one of:\n"
                    "  pip install 'python-telegram-bot[socks]'\n"
                    "  uv sync --extra socks"
                )
                raise RuntimeError(msg) from e
            raise

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

    @staticmethod
    def _mask_proxy_credentials(proxy_url: str) -> str:
        """Mask credentials in proxy URL for safe logging.

        Args:
            proxy_url: The proxy URL potentially containing credentials.

        Returns:
            Proxy URL with credentials replaced by '***'.
        """
        try:
            parsed = urlparse(proxy_url)
            if parsed.username or parsed.password:
                # Replace credentials with ***
                netloc = f"***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                masked = parsed._replace(netloc=netloc)
                return urlunparse(masked)
            return proxy_url
        except Exception:
            # If parsing fails, return original
            return proxy_url

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

        # Use streaming or non-streaming based on config
        if self.config.stream:
            await self._handle_message_streaming(update, user_id, message_text)
        else:
            await self._handle_message_non_streaming(update, user_id, message_text)

    async def _handle_message_non_streaming(
        self, update: Update, user_id: str, message_text: str
    ) -> None:
        """Handle message with non-streaming response.

        Args:
            update: The Telegram update.
            user_id: The user identifier.
            message_text: The message text.
        """
        if update.message is None:
            return

        response = await self.client.send_message(message_text, user_id)

        # Split and send response
        chunks = split_message(response)
        for chunk in chunks:
            try:
                await update.message.reply_text(chunk)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                break

    async def _handle_message_streaming(
        self, update: Update, user_id: str, message_text: str
    ) -> None:
        """Handle message with streaming response using message editing.

        Uses a time-window buffer mechanism: chunks are accumulated and flushed
        after stream_interval seconds from the last chunk, ensuring no content
        is stuck in the buffer even when no new chunks arrive.

        Args:
            update: The Telegram update.
            user_id: The user identifier.
            message_text: The message text.
        """
        # Buffer for accumulating content
        content_buffer: list[str] = []
        sent_message: Any = None
        flush_task: asyncio.Task[None] | None = None

        async def flush_buffer() -> None:
            """Flush the buffer content to the sent message."""
            if sent_message is None or not content_buffer:
                return

            current_content = "".join(content_buffer)
            # Truncate if exceeds limit during streaming
            display_content = current_content[:TELEGRAM_MAX_MESSAGE_LENGTH]

            try:
                await sent_message.edit_text(display_content)
            except Exception as e:
                logger.error(f"Failed to edit message: {e}")

        async def schedule_flush() -> None:
            """Wait for stream_interval then flush the buffer."""
            await asyncio.sleep(self.config.stream_interval)
            await flush_buffer()

        def on_chunk(chunk: str) -> None:
            """Callback for each streaming chunk.

            Accumulates the chunk and schedules a flush task. If a flush task
            is already pending, cancel it and start a new one to ensure flush
            happens stream_interval seconds after the last chunk.
            """
            nonlocal flush_task

            content_buffer.append(chunk)

            # Cancel existing flush task if any
            if flush_task is not None and not flush_task.done():
                flush_task.cancel()

            # Schedule new flush task
            flush_task = asyncio.create_task(schedule_flush())

        # Send initial message placeholder
        if update.message is None:
            return

        # Send typing indicator before streaming starts
        try:
            await update.message.chat.send_action(ChatAction.TYPING)
        except Exception as e:
            logger.debug(f"Failed to send typing indicator: {e}")

        try:
            sent_message = await update.message.reply_text("...")
        except Exception as e:
            logger.error(f"Failed to send initial message: {e}")
            return

        # Get streaming response
        response = await self.client.send_message_stream(message_text, user_id, on_chunk)

        # Wait for any pending flush task to complete
        if flush_task is not None and not flush_task.done():
            with contextlib.suppress(asyncio.CancelledError):
                await flush_task

        # Final flush with complete content
        final_content = "".join(content_buffer) if content_buffer else response

        # Handle message splitting if content exceeds limit
        if len(final_content) > TELEGRAM_MAX_MESSAGE_LENGTH:
            # Edit first message with truncated content
            try:
                await sent_message.edit_text(final_content[:TELEGRAM_MAX_MESSAGE_LENGTH])
            except Exception as e:
                logger.error(f"Failed to edit final message: {e}")

            # Send remaining content as new messages
            chunks = split_message(final_content)
            assert update.message is not None
            for chunk in chunks[1:]:  # Skip first chunk (already sent)
                try:
                    await update.message.reply_text(chunk)
                except Exception as e:
                    logger.error(f"Failed to send additional message: {e}")
                    break
        else:
            # Edit with complete content
            try:
                await sent_message.edit_text(final_content)
            except Exception as e:
                logger.error(f"Failed to edit final message: {e}")
