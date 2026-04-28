"""Tests for mask_sensitive_args function."""

from __future__ import annotations

import sys
from unittest import mock

import pytest

from psi_agent.utils.proctitle import mask_sensitive_args


class TestMaskSensitiveArgs:
    """Tests for mask_sensitive_args function."""

    def test_mask_single_argument_with_underscore(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test masking a single argument with underscore in key name."""
        monkeypatch.setattr(sys, "argv", ["program", "--api-key", "secret123", "--other", "value"])

        with (
            mock.patch("psi_agent.utils.proctitle.setproctitle") as mock_setproctitle,
            mock.patch("psi_agent.utils.proctitle._HAS_SETPROCTITLE", True),
        ):
            mask_sensitive_args(["api_key"])

        # Check that setproctitle was called with masked value
        mock_setproctitle.setproctitle.assert_called_once()
        call_arg = mock_setproctitle.setproctitle.call_args[0][0]
        assert "secret123" not in call_arg
        assert "***" in call_arg

    def test_mask_single_argument_with_hyphen(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test masking a single argument with hyphen in key name."""
        monkeypatch.setattr(sys, "argv", ["program", "--api-key", "secret123", "--other", "value"])

        with (
            mock.patch("psi_agent.utils.proctitle.setproctitle") as mock_setproctitle,
            mock.patch("psi_agent.utils.proctitle._HAS_SETPROCTITLE", True),
        ):
            mask_sensitive_args(["api-key"])

        call_arg = mock_setproctitle.setproctitle.call_args[0][0]
        assert "secret123" not in call_arg
        assert "***" in call_arg

    def test_mask_equals_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test masking argument in --key=value format."""
        monkeypatch.setattr(sys, "argv", ["program", "--api-key=secret123", "--other", "value"])

        with (
            mock.patch("psi_agent.utils.proctitle.setproctitle") as mock_setproctitle,
            mock.patch("psi_agent.utils.proctitle._HAS_SETPROCTITLE", True),
        ):
            mask_sensitive_args(["api_key"])

        call_arg = mock_setproctitle.setproctitle.call_args[0][0]
        assert "secret123" not in call_arg
        assert "--api-key=***" in call_arg

    def test_mask_multiple_arguments(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test masking multiple sensitive arguments."""
        monkeypatch.setattr(
            sys, "argv", ["program", "--api-key", "secret123", "--token", "token456"]
        )

        with (
            mock.patch("psi_agent.utils.proctitle.setproctitle") as mock_setproctitle,
            mock.patch("psi_agent.utils.proctitle._HAS_SETPROCTITLE", True),
        ):
            mask_sensitive_args(["api_key", "token"])

        call_arg = mock_setproctitle.setproctitle.call_args[0][0]
        assert "secret123" not in call_arg
        assert "token456" not in call_arg
        assert call_arg.count("***") == 2

    def test_no_setproctitle_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test graceful fallback when setproctitle is not available."""
        monkeypatch.setattr(sys, "argv", ["program", "--api-key", "secret123"])

        with mock.patch("psi_agent.utils.proctitle._HAS_SETPROCTITLE", False):
            # Should not raise, just log warning
            mask_sensitive_args(["api_key"])

    def test_non_sensitive_args_unchanged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that non-sensitive arguments are not masked."""
        monkeypatch.setattr(
            sys, "argv", ["program", "--api-key", "secret", "--model", "gpt-4", "--port", "8080"]
        )

        with (
            mock.patch("psi_agent.utils.proctitle.setproctitle") as mock_setproctitle,
            mock.patch("psi_agent.utils.proctitle._HAS_SETPROCTITLE", True),
        ):
            mask_sensitive_args(["api_key"])

        call_arg = mock_setproctitle.setproctitle.call_args[0][0]
        assert "gpt-4" in call_arg
        assert "8080" in call_arg
        assert "secret" not in call_arg
