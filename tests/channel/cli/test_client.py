"""Tests for channel/cli/client.py — CliClient HTTP interaction paths."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.channel.cli.client import CliClient
from psi_agent.channel.cli.config import CliConfig


def _make_config(stream: bool = False) -> CliConfig:
    return CliConfig(
        session_socket="/tmp/test.sock",
        stream=stream,
    )


class TestCliClientSendNonStreaming:
    """Tests for CliClient._send_non_streaming."""

    @pytest.mark.asyncio
    async def test_success_path(self) -> None:
        client = CliClient(_make_config())
        client._session = MagicMock()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Hello from session"}}]}
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        result = await client._send_non_streaming(url, headers, "Hi")

        assert result == "Hello from session"

    @pytest.mark.asyncio
    async def test_non_200_status(self) -> None:
        client = CliClient(_make_config())
        client._session = MagicMock()

        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        result = await client._send_non_streaming(url, headers, "Hi")

        assert "500" in result or "Error" in result

    @pytest.mark.asyncio
    async def test_empty_choices(self) -> None:
        client = CliClient(_make_config())
        client._session = MagicMock()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": []})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        result = await client._send_non_streaming(url, headers, "Hi")

        assert "Error" in result

    @pytest.mark.asyncio
    async def test_content_is_none(self) -> None:
        client = CliClient(_make_config())
        client._session = MagicMock()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": None}}]})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        result = await client._send_non_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert result == ""

    @pytest.mark.asyncio
    async def test_connection_error(self) -> None:
        import aiohttp

        client = CliClient(_make_config())
        client._session = MagicMock()
        client._session.post = MagicMock(
            side_effect=aiohttp.ClientConnectorError(
                connection_key=MagicMock(), os_error=OSError("Connection refused")
            )
        )

        result = await client._send_non_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert "Error" in result
        assert "connect" in result.lower()

    @pytest.mark.asyncio
    async def test_timeout_error(self) -> None:
        client = CliClient(_make_config())
        client._session = MagicMock()
        client._session.post = MagicMock(side_effect=TimeoutError("timed out"))

        result = await client._send_non_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert "Error" in result
        assert "timeout" in result.lower()


class TestCliClientSendStreaming:
    """Tests for CliClient._send_streaming."""

    @pytest.mark.asyncio
    async def test_success_path(self) -> None:
        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()

        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def _aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = _aiter_lines()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}

        chunks: list[str] = []

        def on_chunk(chunk: str) -> None:
            chunks.append(chunk)

        result = await client._send_streaming(url, headers, "Hi", on_chunk)

        assert "Hello" in result
        assert "world" in result
        assert chunks == ["Hello", " world"]

    @pytest.mark.asyncio
    async def test_non_200_status(self) -> None:
        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()

        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Error")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        result = await client._send_streaming(url, headers, "Hi")

        assert "Error" in result

    @pytest.mark.asyncio
    async def test_delta_content_is_none_skipped(self) -> None:
        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()

        sse_lines = [
            b'data: {"choices":[{"delta":{"content":null}}]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def _aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = _aiter_lines()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        result = await client._send_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert result == "Hello"

    @pytest.mark.asyncio
    async def test_malformed_json_line_skipped(self) -> None:
        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()

        sse_lines = [
            b"data: not-json\n",
            b'data: {"choices":[{"delta":{"content":"ok"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def _aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = _aiter_lines()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        result = await client._send_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_empty_lines_skipped(self) -> None:
        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()

        sse_lines = [
            b"\n",
            b'data: {"choices":[{"delta":{"content":"Hi"}}]}\n',
            b"\n",
            b"data: [DONE]\n",
        ]

        async def _aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = _aiter_lines()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        result = await client._send_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert result == "Hi"

    @pytest.mark.asyncio
    async def test_connection_error(self) -> None:
        import aiohttp

        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()
        client._session.post = MagicMock(
            side_effect=aiohttp.ClientConnectorError(
                connection_key=MagicMock(), os_error=OSError("Connection refused")
            )
        )

        result = await client._send_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert "Error" in result

    @pytest.mark.asyncio
    async def test_no_on_chunk_callback(self) -> None:
        client = CliClient(_make_config(stream=True))
        client._session = MagicMock()

        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def _aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = _aiter_lines()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        client._session.post = MagicMock(return_value=mock_response)

        result = await client._send_streaming(
            "http://localhost/v1/chat/completions",
            {"Content-Type": "application/json"},
            "Hi",
        )

        assert result == "Hello"


class TestCliClientSendMessageDispatch:
    """Tests for CliClient.send_message dispatching."""

    @pytest.mark.asyncio
    async def test_dispatches_to_non_streaming(self) -> None:
        config = _make_config(stream=False)
        client = CliClient(config)
        client._session = MagicMock()

        with patch.object(
            client, "_send_non_streaming", new_callable=AsyncMock, return_value="ok"
        ) as mock:
            result = await client.send_message("Hi")

        mock.assert_called_once()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_dispatches_to_streaming(self) -> None:
        config = _make_config(stream=True)
        client = CliClient(config)
        client._session = MagicMock()

        with patch.object(
            client, "_send_streaming", new_callable=AsyncMock, return_value="ok"
        ) as mock:
            result = await client.send_message("Hi")

        mock.assert_called_once()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_raises_runtime_error_without_session(self) -> None:
        client = CliClient(_make_config())

        with pytest.raises(RuntimeError, match="not initialized"):
            await client.send_message("Hi")

    @pytest.mark.asyncio
    async def test_passes_on_chunk_to_streaming(self) -> None:
        config = _make_config(stream=True)
        client = CliClient(config)
        client._session = MagicMock()

        def _my_callback(_chunk: str) -> None:
            pass

        with patch.object(
            client, "_send_streaming", new_callable=AsyncMock, return_value="ok"
        ) as mock:
            result = await client.send_message("Hi", on_chunk=_my_callback)

        mock.assert_called_once()
        call_kwargs = mock.call_args
        assert call_kwargs[1].get("on_chunk") is _my_callback or call_kwargs[0][3] is _my_callback
        assert result == "ok"
