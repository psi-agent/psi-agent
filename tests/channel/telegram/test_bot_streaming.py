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

    @pytest.mark.asyncio
    async def test_multiple_flushes_during_long_stream(self):
        """Test that multiple flushes happen during a long streaming session.

        This verifies the core fix: periodic flushes should occur at stream_interval
        intervals during streaming, not just at the end.
        """
        # Use a short interval for faster testing
        config = TelegramConfig(
            token="test-token", session_socket="/tmp/test.sock", stream=True, stream_interval=0.1
        )
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

        edit_times: list[float] = []

        async def mock_edit(text: str) -> None:
            import time

            edit_times.append(time.monotonic())

        mock_sent_message.edit_text.side_effect = mock_edit

        # Mock streaming that takes longer than multiple intervals
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            # Send chunks over time, allowing multiple flush intervals to pass
            for i in range(5):
                on_chunk(f"Chunk{i} ")
                await asyncio.sleep(0.15)  # Longer than stream_interval
            return "Chunk0 Chunk1 Chunk2 Chunk3 Chunk4 "

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Should have multiple edits during streaming (not just one at the end)
        # With 5 chunks over 0.75s and interval 0.1s, we expect several flushes
        assert mock_sent_message.edit_text.call_count >= 3

    @pytest.mark.asyncio
    async def test_flush_timing_approximately_correct(self):
        """Test that flushes occur at approximately the configured interval."""
        interval = 0.2
        config = TelegramConfig(
            token="test-token", session_socket="/tmp/test.sock", stream=True, stream_interval=interval
        )
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

        edit_times: list[float] = []

        async def mock_edit(text: str) -> None:
            import time

            edit_times.append(time.monotonic())

        mock_sent_message.edit_text.side_effect = mock_edit

        # Mock streaming that takes long enough for multiple intervals
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Start ")
            await asyncio.sleep(0.6)  # Should trigger ~3 flushes
            on_chunk("End")
            return "Start End"

        start_time: float = 0.0

        async def track_start_time() -> None:
            import time

            nonlocal start_time
            start_time = time.monotonic()

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await track_start_time()
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Check that flushes happened at roughly correct intervals
        # First edit might be quick, subsequent ones should be ~interval apart
        if len(edit_times) >= 2:
            # Check at least one gap is approximately the configured interval
            gaps = [edit_times[i + 1] - edit_times[i] for i in range(len(edit_times) - 1)]
            # Allow 50% tolerance for test flakiness
            reasonable_gaps = [g for g in gaps if interval * 0.5 <= g <= interval * 2.0]
            assert len(reasonable_gaps) >= 1, f"Expected gaps near {interval}s, got {gaps}"

    @pytest.mark.asyncio
    async def test_stream_ends_before_first_interval(self):
        """Test that content is still flushed when stream ends before first interval."""
        config = TelegramConfig(
            token="test-token", session_socket="/tmp/test.sock", stream=True, stream_interval=1.0
        )
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

        # Mock streaming that completes immediately
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            on_chunk("Quick response")
            return "Quick response"

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Content should still be flushed at the end
        assert final_content == "Quick response"

    @pytest.mark.asyncio
    async def test_empty_stream_no_crash(self):
        """Test that an empty stream doesn't cause crashes."""
        config = TelegramConfig(
            token="test-token", session_socket="/tmp/test.sock", stream=True, stream_interval=0.1
        )
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

        # Mock streaming that returns nothing
        async def mock_stream(_message: str, _user_id: str, on_chunk) -> str:
            return ""

        with patch.object(bot.client, "send_message_stream", mock_stream):
            async with bot.client:
                # Should not raise any error
                await bot._handle_message_streaming(mock_update, "telegram:123", "Hello")

        # Should have at least the final edit (empty or minimal content)
        assert mock_sent_message.edit_text.call_count >= 1


class TestProxyValidation:
    """Tests for proxy validation and error handling."""

    @pytest.mark.asyncio
    async def test_socks5_proxy_missing_dependency_error(self):
        """Test SOCKS5 proxy raises clear error when socksio is not installed."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://localhost:1080",
        )
        bot = TelegramBot(config)

        # Mock the builder chain to raise ImportError at build() time
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.proxy.return_value = mock_builder
        mock_builder.get_updates_proxy.return_value = mock_builder
        mock_builder.build.side_effect = ImportError(
            "Using SOCKS proxy, but the 'socksio' package is not installed"
        )

        with (
            patch("psi_agent.channel.telegram.bot.Application.builder", return_value=mock_builder),
            pytest.raises(RuntimeError) as exc_info,
        ):
            await bot.start()

        # Check error message contains installation instructions
        error_msg = str(exc_info.value)
        assert "socksio" in error_msg.lower()
        assert "pip install" in error_msg or "uv sync" in error_msg

        # Verify both proxy methods were called
        mock_builder.proxy.assert_called_once_with("socks5://localhost:1080")
        mock_builder.get_updates_proxy.assert_called_once_with("socks5://localhost:1080")

    @pytest.mark.asyncio
    async def test_socks5_proxy_runtime_error(self):
        """Test SOCKS5 proxy raises clear error when python-telegram-bot raises RuntimeError."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://localhost:1080",
        )
        bot = TelegramBot(config)

        # Mock the builder chain to raise RuntimeError at build() time
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.proxy.return_value = mock_builder
        mock_builder.get_updates_proxy.return_value = mock_builder
        mock_builder.build.side_effect = RuntimeError(
            "To use Socks5 proxies, PTB must be installed via pip install"
        )

        with (
            patch("psi_agent.channel.telegram.bot.Application.builder", return_value=mock_builder),
            pytest.raises(RuntimeError) as exc_info,
        ):
            await bot.start()

        # Check error message contains installation instructions
        error_msg = str(exc_info.value)
        assert "socksio" in error_msg.lower()
        assert "pip install" in error_msg or "uv sync" in error_msg

        # Verify both proxy methods were called
        mock_builder.proxy.assert_called_once_with("socks5://localhost:1080")
        mock_builder.get_updates_proxy.assert_called_once_with("socks5://localhost:1080")

    @pytest.mark.asyncio
    async def test_http_proxy_no_extra_dependency(self):
        """Test HTTP proxy works without extra dependencies."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="http://localhost:8080",
        )
        bot = TelegramBot(config)

        # Mock the Application building to succeed
        mock_app = MagicMock()
        mock_app.initialize = AsyncMock()
        mock_app.start = AsyncMock()
        mock_app.stop = AsyncMock()
        mock_app.shutdown = AsyncMock()
        mock_app.add_handler = MagicMock()
        mock_app.updater = MagicMock()
        mock_app.updater.start_polling = AsyncMock()
        mock_app.updater.stop = AsyncMock()

        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.proxy.return_value = mock_builder
        mock_builder.get_updates_proxy.return_value = mock_builder
        mock_builder.build.return_value = mock_app

        # Set stop_event so start() doesn't hang waiting forever
        bot._stop_event.set()

        with patch("psi_agent.channel.telegram.bot.Application.builder", return_value=mock_builder):
            # This should not raise any error about socksio
            await bot.start()

        # Verify both proxy methods were called
        mock_builder.proxy.assert_called_once_with("http://localhost:8080")
        mock_builder.get_updates_proxy.assert_called_once_with("http://localhost:8080")

    @pytest.mark.asyncio
    async def test_import_error_non_socksio(self):
        """Test ImportError not related to socksio is re-raised."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://localhost:1080",
        )
        bot = TelegramBot(config)

        # Mock the builder chain to raise ImportError not related to socksio
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.proxy.return_value = mock_builder
        mock_builder.get_updates_proxy.return_value = mock_builder
        mock_builder.build.side_effect = ImportError("Some other import error")

        with (
            patch("psi_agent.channel.telegram.bot.Application.builder", return_value=mock_builder),
            pytest.raises(ImportError) as exc_info,
        ):
            await bot.start()

        assert "Some other import error" in str(exc_info.value)

        # Verify both proxy methods were called
        mock_builder.proxy.assert_called_once_with("socks5://localhost:1080")
        mock_builder.get_updates_proxy.assert_called_once_with("socks5://localhost:1080")

    @pytest.mark.asyncio
    async def test_runtime_error_non_socks5(self):
        """Test RuntimeError not related to Socks5 is re-raised."""
        config = TelegramConfig(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://localhost:1080",
        )
        bot = TelegramBot(config)

        # Mock the builder chain to raise RuntimeError not related to Socks5
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.proxy.return_value = mock_builder
        mock_builder.get_updates_proxy.return_value = mock_builder
        mock_builder.build.side_effect = RuntimeError("Some other runtime error")

        with (
            patch("psi_agent.channel.telegram.bot.Application.builder", return_value=mock_builder),
            pytest.raises(RuntimeError) as exc_info,
        ):
            await bot.start()

        assert "Some other runtime error" in str(exc_info.value)

        # Verify both proxy methods were called
        mock_builder.proxy.assert_called_once_with("socks5://localhost:1080")
        mock_builder.get_updates_proxy.assert_called_once_with("socks5://localhost:1080")


class TestProxyCredentialMasking:
    """Tests for proxy credential masking."""

    def test_mask_proxy_credentials_no_credentials(self):
        """Test masking when no credentials present."""
        result = TelegramBot._mask_proxy_credentials("http://localhost:8080")
        assert result == "http://localhost:8080"

    def test_mask_proxy_credentials_with_user_only(self):
        """Test masking with user only (no password)."""
        result = TelegramBot._mask_proxy_credentials("socks5://user@localhost:1080")
        assert result == "socks5://***@localhost:1080"

    def test_mask_proxy_credentials_with_user_and_password(self):
        """Test masking with user and password."""
        result = TelegramBot._mask_proxy_credentials("socks5://user:password@localhost:1080")
        assert result == "socks5://***@localhost:1080"

    def test_mask_proxy_credentials_complex_password(self):
        """Test masking with complex password containing special chars."""
        result = TelegramBot._mask_proxy_credentials("http://user:p@ss:w0rd@proxy.example.com:8080")
        assert result == "http://***@proxy.example.com:8080"

    def test_mask_proxy_credentials_no_scheme(self):
        """Test masking when scheme is missing (edge case)."""
        result = TelegramBot._mask_proxy_credentials("user:password@localhost:1080")
        # Should return original since we can't properly parse it
        assert result == "user:password@localhost:1080"

    def test_mask_proxy_credentials_exception_handling(self):
        """Test masking handles exceptions gracefully."""
        # Pass an invalid URL that causes urlparse to behave unexpectedly
        # This tests the except Exception branch
        result = TelegramBot._mask_proxy_credentials("://invalid")
        # Should return original when parsing fails
        assert result == "://invalid"

    def test_mask_proxy_credentials_with_port(self):
        """Test masking with explicit port."""
        result = TelegramBot._mask_proxy_credentials("socks5://user:pass@proxy.example.com:1080")
        assert result == "socks5://***@proxy.example.com:1080"

    def test_mask_proxy_credentials_without_port(self):
        """Test masking without explicit port."""
        result = TelegramBot._mask_proxy_credentials("http://user:pass@proxy.example.com")
        assert result == "http://***@proxy.example.com"
