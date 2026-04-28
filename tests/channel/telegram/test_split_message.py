"""Tests for message splitting logic."""

from __future__ import annotations

from psi_agent.channel.telegram.bot import split_message


class TestSplitMessage:
    """Tests for split_message function."""

    def test_short_message_not_split(self):
        """Test short message is not split."""
        text = "Hello, world!"
        result = split_message(text)

        assert result == [text]

    def test_exact_max_length(self):
        """Test message at exact max length is not split."""
        text = "a" * 4096
        result = split_message(text)

        assert result == [text]
        assert len(result[0]) == 4096

    def test_long_message_split(self):
        """Test long message is split."""
        text = "a" * 5000
        result = split_message(text)

        assert len(result) == 2
        assert len(result[0]) == 4096
        assert len(result[1]) == 904
        assert "".join(result) == text

    def test_split_at_newline(self):
        """Test message splits at newline when possible."""
        # Newline at position 3000, which is > 2048 (first half)
        # Total length > 4096 to trigger splitting
        text = "a" * 3000 + "\n" + "b" * 2000
        result = split_message(text)

        # Should split after the newline since it's in second half
        assert len(result) == 2
        assert result[0] == "a" * 3000 + "\n"
        assert result[1] == "b" * 2000

    def test_split_at_space(self):
        """Test message splits at space when possible."""
        # Space at position 3000, which is > 2048 (first half)
        # Total length > 4096 to trigger splitting
        text = "a" * 3000 + " " + "b" * 2000
        result = split_message(text)

        # Should split after the space since it's in second half
        assert len(result) == 2
        assert result[0] == "a" * 3000 + " "
        assert result[1] == "b" * 2000

    def test_very_long_line(self):
        """Test very long line without breaks is split at max length."""
        text = "a" * 10000
        result = split_message(text)

        # Should split at max length
        assert len(result) == 3
        assert len(result[0]) == 4096
        assert len(result[1]) == 4096
        assert len(result[2]) == 1808

    def test_custom_max_length(self):
        """Test custom max length."""
        text = "a" * 100
        result = split_message(text, max_length=50)

        assert len(result) == 2
        assert len(result[0]) == 50
        assert len(result[1]) == 50

    def test_empty_message(self):
        """Test empty message returns empty list."""
        result = split_message("")

        assert result == [""]
