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
TYPING_INTERVAL = 4  # seconds between typing indicator sends


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

        # Configure proxy if provided (for both API requests and updater polling)
        if self.config.proxy:
            builder = builder.proxy(self.config.proxy)
            builder = builder.get_updates_proxy(self.config.proxy)
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

    @staticmethod
    async def _send_typing_periodically(chat: Any) -> None:
        """Send typing action periodically until cancelled.

        Runs in a background task, sending typing indicators at regular intervals
        until cancelled. Handles errors gracefully without interrupting the task.

        Args:
            chat: The Telegram chat object to send typing actions to.
        """
        while True:
            await asyncio.sleep(TYPING_INTERVAL)
            try:
                await chat.send_action(ChatAction.TYPING)
                logger.debug("Sent typing indicator")
            except Exception as e:
                logger.debug(f"Failed to send typing indicator: {e}")

    async def _handle_message_streaming(
        self, update: Update, user_id: str, message_text: str
    ) -> None:
        """Handle message with streaming response using message editing.

        Uses a background periodic flush mechanism: a background task flushes the
        buffer every stream_interval seconds during streaming, ensuring users see
        progressive updates even while the stream is ongoing.

        Args:
            update: The Telegram update.
            user_id: The user identifier.
            message_text: The message text.
        """
        # Buffer for accumulating content
        content_buffer: list[str] = []
        sent_message: Any = None
        stop_flush = asyncio.Event()
        flush_task: asyncio.Task[None] | None = None
        last_sent_content: str | None = None  # Track last sent content to avoid duplicate edits

        async def flush_buffer() -> None:
            """Flush the buffer content to the sent message."""
            nonlocal last_sent_content

            if sent_message is None or not content_buffer:
                return

            current_content = "".join(content_buffer)
            # Truncate if exceeds limit during streaming
            display_content = current_content[:TELEGRAM_MAX_MESSAGE_LENGTH]

            # Skip edit if content unchanged (avoids Telegram API error)
            if display_content == last_sent_content:
                return

            try:
                await sent_message.edit_text(display_content)
                last_sent_content = display_content
            except Exception as e:
                logger.error(f"Failed to edit message: {e}")

        async def periodic_flush() -> None:
            """Background task that flushes buffer every stream_interval seconds."""
            while not stop_flush.is_set():
                try:
                    await asyncio.wait_for(stop_flush.wait(), timeout=self.config.stream_interval)
                    # stop_flush was set, exit the loop
                    break
                except TimeoutError:
                    # Timeout reached, flush if there's content
                    await flush_buffer()

        def on_chunk(chunk: str) -> None:
            """Callback for each streaming chunk.

            Accumulates the chunk in the buffer. The background periodic_flush
            task will flush the buffer at regular intervals.
            """
            content_buffer.append(chunk)

        # Send initial message placeholder
        if update.message is None:
            return

        # Send typing indicator before streaming starts and start periodic typing task
        typing_task: asyncio.Task[None] | None = None
        try:
            await update.message.chat.send_action(ChatAction.TYPING)
            # Start periodic typing indicator task
            typing_task = asyncio.create_task(self._send_typing_periodically(update.message.chat))
        except Exception as e:
            logger.debug(f"Failed to send typing indicator: {e}")

        try:
            sent_message = await update.message.reply_text("...")
        except Exception as e:
            logger.error(f"Failed to send initial message: {e}")
            # Cancel typing task if message send failed
            if typing_task is not None and not typing_task.done():
                typing_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await typing_task
            return

        # Start the periodic flush background task
        flush_task = asyncio.create_task(periodic_flush())

        try:
            # Get streaming response
            response = await self.client.send_message_stream(message_text, user_id, on_chunk)
        finally:
            # Cancel typing task when streaming ends
            if typing_task is not None and not typing_task.done():
                typing_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await typing_task
            # Stop the periodic flush task
            stop_flush.set()
            with contextlib.suppress(asyncio.CancelledError):
                await flush_task

        # Final flush with complete content
        final_content = "".join(content_buffer) if content_buffer else response

        # Handle message splitting if content exceeds limit
        if len(final_content) > TELEGRAM_MAX_MESSAGE_LENGTH:
            chunks = split_message(final_content)
            first_chunk = chunks[0]
            # Edit first message with first chunk (skip if unchanged)
            if first_chunk != last_sent_content:
                try:
                    await sent_message.edit_text(first_chunk)
                    last_sent_content = first_chunk
                except Exception as e:
                    logger.error(f"Failed to edit final message: {e}")

            # Send remaining content as new messages
            assert update.message is not None
            for chunk in chunks[1:]:  # Skip first chunk (already sent)
                try:
                    await update.message.reply_text(chunk)
                except Exception as e:
                    logger.error(f"Failed to send additional message: {e}")
                    break
        else:
            # Edit with complete content (skip if unchanged)
            if final_content != last_sent_content:
                try:
                    await sent_message.edit_text(final_content)
                    last_sent_content = final_content
                except Exception as e:
                    logger.error(f"Failed to edit final message: {e}")
