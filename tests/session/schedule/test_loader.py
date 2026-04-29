"""Tests for ScheduleLoader functions."""

from __future__ import annotations

import tempfile

import anyio
import pytest

from psi_agent.session.schedule import load_schedule, load_schedules, parse_frontmatter


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_no_frontmatter(self) -> None:
        """Test content without frontmatter."""
        content = "Just some content\nwithout frontmatter"
        frontmatter, remaining = parse_frontmatter(content)

        assert frontmatter == {}
        assert remaining == content

    def test_with_frontmatter(self) -> None:
        """Test content with frontmatter."""
        content = """---
name: test-task
description: A test task
cron: "0 9 * * *"
---

Task content here."""
        frontmatter, remaining = parse_frontmatter(content)

        assert frontmatter["name"] == "test-task"
        assert frontmatter["description"] == "A test task"
        assert frontmatter["cron"] == "0 9 * * *"
        assert remaining.strip() == "Task content here."

    def test_frontmatter_with_multiline_content(self) -> None:
        """Test frontmatter with multiline content."""
        content = """---
name: test-task
cron: "0 9 * * *"
---

Line 1
Line 2
Line 3"""
        frontmatter, remaining = parse_frontmatter(content)

        assert frontmatter["name"] == "test-task"
        assert "Line 1" in remaining
        assert "Line 2" in remaining
        assert "Line 3" in remaining


class TestLoadSchedule:
    """Tests for load_schedule function."""

    @pytest.mark.asyncio
    async def test_load_valid_schedule(self) -> None:
        """Test loading a valid schedule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = anyio.Path(tmpdir) / "test-task"
            await task_dir.mkdir()

            task_file = task_dir / "TASK.md"
            await task_file.write_text("""---
name: test-task
description: A test task
cron: "0 9 * * *"
---

Do something daily.""")

            schedule = await load_schedule(task_dir)

            assert schedule is not None
            assert schedule.name == "test-task"
            assert schedule.description == "A test task"
            assert schedule.cron == "0 9 * * *"
            assert schedule.content == "Do something daily."

    @pytest.mark.asyncio
    async def test_load_missing_task_md(self) -> None:
        """Test loading from directory without TASK.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = anyio.Path(tmpdir) / "test-task"
            await task_dir.mkdir()

            schedule = await load_schedule(task_dir)

            assert schedule is None

    @pytest.mark.asyncio
    async def test_load_missing_cron(self) -> None:
        """Test loading schedule without cron field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = anyio.Path(tmpdir) / "test-task"
            await task_dir.mkdir()

            task_file = task_dir / "TASK.md"
            await task_file.write_text("""---
name: test-task
---

No cron here.""")

            schedule = await load_schedule(task_dir)

            assert schedule is None


class TestLoadSchedules:
    """Tests for load_schedules function."""

    @pytest.mark.asyncio
    async def test_load_multiple_schedules(self) -> None:
        """Test loading multiple schedules from workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = anyio.Path(tmpdir)
            schedules_dir = workspace / "schedules"
            await schedules_dir.mkdir()

            # Create first task
            task1_dir = schedules_dir / "task1"
            await task1_dir.mkdir()
            await (task1_dir / "TASK.md").write_text("""---
name: task1
cron: "0 9 * * *"
---

Task 1 content.""")

            # Create second task
            task2_dir = schedules_dir / "task2"
            await task2_dir.mkdir()
            await (task2_dir / "TASK.md").write_text("""---
name: task2
cron: "0 18 * * *"
---

Task 2 content.""")

            schedules = await load_schedules(workspace)

            assert len(schedules) == 2
            names = [s.name for s in schedules]
            assert "task1" in names
            assert "task2" in names

    @pytest.mark.asyncio
    async def test_load_no_schedules_dir(self) -> None:
        """Test loading from workspace without schedules directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = anyio.Path(tmpdir)

            schedules = await load_schedules(workspace)

            assert schedules == []

    @pytest.mark.asyncio
    async def test_load_empty_schedules_dir(self) -> None:
        """Test loading from empty schedules directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = anyio.Path(tmpdir)
            schedules_dir = workspace / "schedules"
            await schedules_dir.mkdir()

            schedules = await load_schedules(workspace)

            assert schedules == []
