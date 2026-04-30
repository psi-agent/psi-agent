"""Tests for session config module - workspace path resolution."""

from __future__ import annotations

import os
import tempfile

import anyio
import pytest

from psi_agent.session.config import SessionConfig


class TestWorkspacePathResolution:
    """Tests for workspace path resolution to absolute paths."""

    @pytest.mark.asyncio
    async def test_relative_workspace_path_resolved_to_absolute(self) -> None:
        """Test that relative workspace path is resolved to absolute path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a workspace directory
            workspace_dir = os.path.join(tmpdir, "workspace")
            os.makedirs(workspace_dir)

            # Change to the temp directory so we can use a relative path
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                config = SessionConfig(
                    channel_socket="/tmp/channel.sock",
                    ai_socket="/tmp/ai.sock",
                    workspace="./workspace",
                )

                resolved_path = await config.workspace_path()

                # Should be an absolute path
                assert resolved_path.is_absolute()
                # Should point to the correct location
                expected = anyio.Path(tmpdir) / "workspace"
                assert resolved_path == expected
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_absolute_workspace_path_remains_unchanged(self) -> None:
        """Test that absolute workspace path remains unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = anyio.Path(tmpdir) / "workspace"
            await workspace_path.mkdir()

            config = SessionConfig(
                channel_socket="/tmp/channel.sock",
                ai_socket="/tmp/ai.sock",
                workspace=str(workspace_path),
            )

            resolved_path = await config.workspace_path()

            # Should be the same absolute path
            assert resolved_path == workspace_path
            assert resolved_path.is_absolute()

    @pytest.mark.asyncio
    async def test_workspace_path_caching(self) -> None:
        """Test that resolved workspace path is cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = os.path.join(tmpdir, "workspace")
            os.makedirs(workspace_dir)

            config = SessionConfig(
                channel_socket="/tmp/channel.sock",
                ai_socket="/tmp/ai.sock",
                workspace=workspace_dir,
            )

            # First call resolves and caches
            resolved_path1 = await config.workspace_path()
            # Second call returns cached value
            resolved_path2 = await config.workspace_path()

            # Should be the same object (cached)
            assert resolved_path1 is resolved_path2

    @pytest.mark.asyncio
    async def test_workspace_path_with_symlinks(self) -> None:
        """Test that workspace path with symlinks is resolved correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create actual workspace
            actual_workspace = anyio.Path(tmpdir) / "actual_workspace"
            await actual_workspace.mkdir()

            # Create symlink to workspace
            symlink_path = anyio.Path(tmpdir) / "workspace_link"
            await symlink_path.symlink_to(actual_workspace)

            config = SessionConfig(
                channel_socket="/tmp/channel.sock",
                ai_socket="/tmp/ai.sock",
                workspace=str(symlink_path),
            )

            resolved_path = await config.workspace_path()

            # Should resolve to the actual target, not the symlink
            assert resolved_path.is_absolute()
            # The resolved path should point to the actual directory
            assert await resolved_path.samefile(actual_workspace)

    @pytest.mark.asyncio
    async def test_tools_dir_uses_resolved_workspace_path(self) -> None:
        """Test that tools_dir returns path derived from resolved workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = os.path.join(tmpdir, "workspace")
            os.makedirs(workspace_dir)

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                config = SessionConfig(
                    channel_socket="/tmp/channel.sock",
                    ai_socket="/tmp/ai.sock",
                    workspace="./workspace",
                )

                tools_dir = await config.tools_dir()

                # Should be an absolute path
                assert tools_dir.is_absolute()
                # Should be derived from resolved workspace
                expected = anyio.Path(tmpdir) / "workspace" / "tools"
                assert tools_dir == expected
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_systems_dir_uses_resolved_workspace_path(self) -> None:
        """Test that systems_dir returns path derived from resolved workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = os.path.join(tmpdir, "workspace")
            os.makedirs(workspace_dir)

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                config = SessionConfig(
                    channel_socket="/tmp/channel.sock",
                    ai_socket="/tmp/ai.sock",
                    workspace="./workspace",
                )

                systems_dir = await config.systems_dir()

                # Should be an absolute path
                assert systems_dir.is_absolute()
                # Should be derived from resolved workspace
                expected = anyio.Path(tmpdir) / "workspace" / "systems"
                assert systems_dir == expected
            finally:
                os.chdir(original_cwd)


class TestSessionConfigPaths:
    """Tests for various SessionConfig path methods."""

    def test_channel_socket_path(self) -> None:
        """Test channel_socket_path returns anyio.Path."""
        config = SessionConfig(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )

        path = config.channel_socket_path()
        assert isinstance(path, anyio.Path)
        assert path == anyio.Path("/tmp/channel.sock")

    def test_ai_socket_path(self) -> None:
        """Test ai_socket_path returns anyio.Path."""
        config = SessionConfig(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )

        path = config.ai_socket_path()
        assert isinstance(path, anyio.Path)
        assert path == anyio.Path("/tmp/ai.sock")

    def test_history_file_path_with_file(self) -> None:
        """Test history_file_path returns anyio.Path when file is set."""
        config = SessionConfig(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            history_file="/tmp/history.json",
        )

        path = config.history_file_path()
        assert path is not None
        assert isinstance(path, anyio.Path)
        assert path == anyio.Path("/tmp/history.json")

    def test_history_file_path_without_file(self) -> None:
        """Test history_file_path returns None when no file is set."""
        config = SessionConfig(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )

        path = config.history_file_path()
        assert path is None
