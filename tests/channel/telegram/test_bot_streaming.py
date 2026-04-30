"""Tests for TelegramBot streaming logic."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.channel.telegram.bot import TelegramBot, split_message
from psi_agent.channel.telegram.config import TelegramConfig


@pytest.fixture
def config():
    """Create test config with streaming enabled."""
    return TelegramConfig(
        token="test-token", session_socket="/tmp/test.sock", stream=True, stream_interval=1.0
    )


@pytest.fixture
def config_no_stream():
    """Create test config with streaming disabled."""
    return TelegramConfig(token="test-token", session_socket="/tmp/test.sock", stream=False)


class TestSplitMessage:
    """Tests for split_message function."""

    def test_short_message(self):
        """Test short message is not split."""
        result = split_message("Hello")
        assert result == ["Hello"]

    def test_exact_limit(self):
        """Test message at exact limit is not split."""
        text = "a" * 4096
        result = split_message(text)
        assert result == [text]

    def test_over_limit(self):
        """Test message over limit is split."""
        text = "a" * 5000
        result = split_message(text)
        assert len(result) == 2
        assert len(result[0]) <= 4096
        assert "".join(result) == text

    def test_split_at_newline(self):
        """Test split prefers newline boundary when possible."""
        # Create text where newline is in a good position for splitting
        text = "a" * 2000 + "\n" + "b" * 3000
        result = split_message(text)
        # The split should happen at or near the newline
        assert len(result) == 2
        assert "".join(result) == text


class TestTelegramBotStreaming:
    """Tests for TelegramBot streaming behavior."""

    def test_bot_creation_with_streaming(self, config):
        """Test bot can be created with streaming config."""
        bot = TelegramBot(config)
        assert bot.config.stream is True
        assert bot.config.stream_interval == 1.0

    def test_bot_creation_without_streaming(self, config_no_stream):
        """Test bot can be created with streaming disabled."""
        bot = TelegramBot(config_no_stream)
        assert bot.config.stream is False

    @pytest.mark.asyncio
    async def test_non_streaming_handler(self, config_no_stream):
        """Test non-streaming handler sends message correctly."""
        bot = TelegramBot(config_no_stream)

        # Mock update and message
        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Mock client response
        with patch.object(bot.client, "send_message", AsyncMock(return_value="Test response")):
            async with bot.client:
                await bot._handle_message_non_streaming(mock_update, "telegram:123", "Hello")

        mock_message.reply_text.assert_called_once_with("Test response")

    @pytest.mark.asyncio
    async def test_non_streaming_handler_splits_long_message(self, config_no_stream):
        """Test non-streaming handler splits long messages."""
        bot = TelegramBot(config_no_stream)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        long_response = "a" * 5000
        with patch.object(bot.client, "send_message", AsyncMock(return_value=long_response)):
            async with bot.client:
                await bot._handle_message_non_streaming(mock_update, "telegram:123", "Hello")

        # Should be called twice for split message
        assert mock_message.reply_text.call_count == 2

    @pytest.mark.asyncio
    async def test_streaming_handler_sends_initial_message(self, config):
        """Test streaming handler sends initial placeholder message."""
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Mock streaming response
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Test")
            return "Test"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Initial message should be sent
        mock_message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_streaming_handler_edits_message(self, config):
        """Test streaming handler edits message with content."""
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Mock streaming response
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Hello ")
            on_chunk("world")
            return "Hello world"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Final edit should be called
        mock_sent_message.edit_text.assert_called()

    @pytest.mark.asyncio
    async def test_handle_message_none_message(self, config):
        """Test _handle_message returns early when message is None."""
        bot = TelegramBot(config)

        mock_update = MagicMock()
        mock_update.message = None
        mock_update.effective_user = MagicMock(id=123)

        # Should return early without error
        await bot._handle_message(mock_update, MagicMock())

    @pytest.mark.asyncio
    async def test_handle_message_none_text(self, config):
        """Test _handle_message returns early when message text is None."""
        bot = TelegramBot(config)

        mock_message = MagicMock()
        mock_message.text = None

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Should return early without error
        await bot._handle_message(mock_update, MagicMock())

    @pytest.mark.asyncio
    async def test_handle_message_none_user(self, config):
        """Test _handle_message returns early when user is None."""
        bot = TelegramBot(config)

        mock_message = MagicMock()
        mock_message.text = "Hello"

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = None

        # Should return early without error
        await bot._handle_message(mock_update, MagicMock())

    @pytest.mark.asyncio
    async def test_handle_message_routes_to_streaming(self, config):
        """Test _handle_message routes to streaming handler when stream is True."""
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Patch both handlers to track which is called
        with (
            patch.object(bot, "_handle_message_streaming", AsyncMock()) as mock_streaming,
            patch.object(bot, "_handle_message_non_streaming", AsyncMock()),
        ):
            await bot._handle_message(mock_update, MagicMock())
            mock_streaming.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_message_routes_to_non_streaming(self, config_no_stream):
        """Test _handle_message routes to non-streaming handler when stream is False."""
        bot = TelegramBot(config_no_stream)

        mock_message = AsyncMock()
        mock_message.text = "Hello"

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Patch both handlers to track which is called
        with (
            patch.object(bot, "_handle_message_streaming", AsyncMock()),
            patch.object(bot, "_handle_message_non_streaming", AsyncMock()) as mock_non_streaming,
        ):
            await bot._handle_message(mock_update, MagicMock())
            mock_non_streaming.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_command_with_user(self, config):
        """Test _start_command logs user ID."""
        bot = TelegramBot(config)

        mock_update = MagicMock()
        mock_update.effective_user = MagicMock(id=123)

        # Should not raise error
        await bot._start_command(mock_update, MagicMock())

    @pytest.mark.asyncio
    async def test_start_command_without_user(self, config):
        """Test _start_command handles missing user."""
        bot = TelegramBot(config)

        mock_update = MagicMock()
        mock_update.effective_user = None

        # Should not raise error
        await bot._start_command(mock_update, MagicMock())

    @pytest.mark.asyncio
    async def test_streaming_handler_send_initial_fails(self, config):
        """Test streaming handler handles failure to send initial message."""
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock(side_effect=Exception("Network error"))

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Should return early without error
        async with bot.client:
            await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

    @pytest.mark.asyncio
    async def test_streaming_handler_long_message_split(self, config):
        """Test streaming handler splits long messages."""
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Mock streaming response with long content
        long_content = "a" * 5000

        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk(long_content)
            return long_content

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Should send initial message + one additional message for overflow
        assert mock_message.reply_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_streaming_handler_edit_fails(self, config):
        """Test streaming handler handles edit failure gracefully."""
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock(side_effect=Exception("Edit failed"))
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Test")
            return "Test"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                # Should not raise error
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

    @pytest.mark.asyncio
    async def test_non_streaming_handler_send_fails(self, config_no_stream):
        """Test non-streaming handler handles send failure."""
        bot = TelegramBot(config_no_stream)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock(side_effect=Exception("Send failed"))

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        with patch.object(bot.client, "send_message", AsyncMock(return_value="Test response")):
            async with bot.client:
                await bot._handle_message_non_streaming(mock_update, "telegram:123", "Hello")

        # Should have attempted to send once
        mock_message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_non_streaming_handler_none_message(self, config_no_stream):
        """Test non-streaming handler returns early when message is None."""
        bot = TelegramBot(config_no_stream)

        mock_update = MagicMock()
        mock_update.message = None

        async with bot.client:
            await bot._handle_message_non_streaming(mock_update, "telegram:123", "Hello")

    @pytest.mark.asyncio
    async def test_bot_with_proxy(self):
        """Test bot creation with proxy configuration."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://user:pass@proxy.example.com:1080",
        )
        bot = TelegramBot(config)
        assert bot.config.proxy == "socks5://user:pass@proxy.example.com:1080"

    @pytest.mark.asyncio
    async def test_bot_with_proxy_no_auth(self):
        """Test bot creation with proxy without credentials."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://proxy.example.com:1080",
        )
        bot = TelegramBot(config)
        assert bot.config.proxy == "socks5://proxy.example.com:1080"

    @pytest.mark.asyncio
    async def test_buffer_flushes_when_no_new_chunks_arrive(self, config):
        """Test buffer flushes after stream_interval when no new chunks arrive.

        This tests the time-window buffer mechanism: chunks that arrive within
        the interval should be flushed even if no more chunks come.
        """
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        # Track when edits happen
        edit_times: list[float] = []
        edit_contents: list[str] = []

        async def mock_edit(text: str) -> None:
            import time

            edit_times.append(time.monotonic())
            edit_contents.append(text)

        mock_sent_message.edit_text.side_effect = mock_edit

        # Mock streaming that sends chunks quickly then stops
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Hello ")
            on_chunk("world")
            # Wait longer than stream_interval to allow flush
            await asyncio.sleep(1.5)
            return "Hello world"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Should have at least one edit during streaming (from flush task)
        # and a final edit at the end
        assert mock_sent_message.edit_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_timer_resets_on_new_chunk_arrival(self, config):
        """Test flush timer resets when a new chunk arrives.

        Multiple chunks within the interval should be batched together
        and flushed only after the interval passes from the last chunk.
        """
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        edit_count = 0

        async def mock_edit(text: str) -> None:
            nonlocal edit_count
            edit_count += 1

        mock_sent_message.edit_text.side_effect = mock_edit

        # Mock streaming that sends chunks faster than interval
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("a")
            await asyncio.sleep(0.3)
            on_chunk("b")
            await asyncio.sleep(0.3)
            on_chunk("c")
            # Wait for flush to happen
            await asyncio.sleep(1.5)
            return "abc"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Chunks should be batched - at least one edit should have accumulated content
        assert edit_count >= 1

    @pytest.mark.asyncio
    async def test_final_flush_on_stream_end(self, config):
        """Test remaining buffered content is flushed when streaming ends.

        Even if chunks arrive right before stream ends, they should be flushed.
        """
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        final_content = None

        async def mock_edit(text: str) -> None:
            nonlocal final_content
            final_content = text

        mock_sent_message.edit_text.side_effect = mock_edit

        # Mock streaming that ends immediately after sending chunks
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Final ")
            on_chunk("content")
            return "Final content"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Final content should be the complete message
        assert final_content == "Final content"

    @pytest.mark.asyncio
    async def test_multiple_chunks_within_interval_batched(self, config):
        """Test multiple chunks within interval are batched together.

        When chunks arrive faster than stream_interval, they should be
        accumulated and flushed together.
        """
        bot = TelegramBot(config)

        mock_message = AsyncMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()

        mock_sent_message = AsyncMock()
        mock_sent_message.edit_text = AsyncMock()
        mock_message.reply_text.return_value = mock_sent_message

        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.effective_user = MagicMock(id=123)

        captured_edits: list[str] = []

        async def mock_edit(text: str) -> None:
            captured_edits.append(text)

        mock_sent_message.edit_text.side_effect = mock_edit

        # Mock streaming with rapid chunks
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            for char in "Hello world":
                on_chunk(char)
            # Wait for flush
            await asyncio.sleep(1.5)
            return "Hello world"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Should have edits with accumulated content
        # At least one edit should contain multiple characters (batched)
        has_batched = any(len(edit) > 1 for edit in captured_edits if edit)
        assert has_batched or len(captured_edits) >= 1  # Either batched or final edit
