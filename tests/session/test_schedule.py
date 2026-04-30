"""Tests for schedule module."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import anyio

from psi_agent.session.schedule import (
    Schedule,
    ScheduleExecutor,
    load_schedule,
    load_schedules,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_parse_valid_frontmatter(self) -> None:
        """Test parsing valid YAML frontmatter."""
        content = """---
name: daily-summary
description: Generate daily summary
cron: "0 9 * * *"
---

Task instructions here...
"""
        frontmatter, remaining = parse_frontmatter(content)

        assert frontmatter["name"] == "daily-summary"
        assert frontmatter["description"] == "Generate daily summary"
        assert frontmatter["cron"] == "0 9 * * *"
        assert "Task instructions here" in remaining

    def test_parse_no_frontmatter(self) -> None:
        """Test parsing content without frontmatter."""
        content = "Just regular content\nNo frontmatter here"
        frontmatter, remaining = parse_frontmatter(content)

        assert frontmatter == {}
        assert remaining == content

    def test_parse_frontmatter_with_single_quotes(self) -> None:
        """Test parsing frontmatter with single quotes."""
        content = """---
name: 'test-task'
cron: '0 9 * * *'
---

Content
"""
        frontmatter, _ = parse_frontmatter(content)

        assert frontmatter["name"] == "test-task"
        assert frontmatter["cron"] == "0 9 * * *"

    def test_parse_frontmatter_without_quotes(self) -> None:
        """Test parsing frontmatter without quotes."""
        content = """---
name: test-task
cron: 0 9 * * *
---

Content
"""
        frontmatter, _ = parse_frontmatter(content)

        assert frontmatter["name"] == "test-task"
        assert frontmatter["cron"] == "0 9 * * *"


class TestSchedule:
    """Tests for Schedule dataclass."""

    def test_schedule_creation(self, tmp_path: anyio.Path) -> None:
        """Test creating a Schedule object."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Task content",
            task_dir=tmp_path,
        )

        assert schedule.name == "test-task"
        assert schedule.cron == "0 9 * * *"
        assert schedule.content == "Task content"
        assert schedule.task_dir == tmp_path
        assert schedule.description == ""

    def test_schedule_with_description(self, tmp_path: anyio.Path) -> None:
        """Test Schedule with description."""
        schedule = Schedule(
            name="test-task",
            description="A test task",
            cron="0 9 * * *",
            content="Task content",
            task_dir=tmp_path,
        )

        assert schedule.description == "A test task"

    def test_get_next_run(self, tmp_path: anyio.Path) -> None:
        """Test get_next_run returns a future datetime."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",  # 9am daily
            content="Task content",
            task_dir=tmp_path,
        )

        next_run = schedule.get_next_run()
        assert isinstance(next_run, datetime)
        assert next_run > datetime.now()

    def test_get_seconds_until_next_run(self, tmp_path: anyio.Path) -> None:
        """Test get_seconds_until_next_run returns positive value."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Task content",
            task_dir=tmp_path,
        )

        seconds = schedule.get_seconds_until_next_run()
        assert seconds >= 0


class TestLoadSchedule:
    """Tests for load_schedule function."""

    async def test_load_valid_schedule(self, tmp_path: anyio.Path) -> None:
        """Test loading a valid schedule."""
        tmp = anyio.Path(tmp_path)
        task_dir = tmp / "daily-summary"
        await task_dir.mkdir()

        task_file = task_dir / "TASK.md"
        await task_file.write_text("""---
name: daily-summary
description: Daily summary task
cron: "0 9 * * *"
---

Generate a daily summary of activities.
""")

        schedule = await load_schedule(task_dir)

        assert schedule is not None
        assert schedule.name == "daily-summary"
        assert schedule.description == "Daily summary task"
        assert schedule.cron == "0 9 * * *"
        assert "Generate a daily summary" in schedule.content

    async def test_load_schedule_missing_task_file(self, tmp_path: anyio.Path) -> None:
        """Test loading schedule when TASK.md is missing."""
        tmp = anyio.Path(tmp_path)
        task_dir = tmp / "missing-task"
        await task_dir.mkdir()

        schedule = await load_schedule(task_dir)

        assert schedule is None

    async def test_load_schedule_missing_cron(self, tmp_path: anyio.Path) -> None:
        """Test loading schedule when cron field is missing."""
        tmp = anyio.Path(tmp_path)
        task_dir = tmp / "no-cron"
        await task_dir.mkdir()

        task_file = task_dir / "TASK.md"
        await task_file.write_text("""---
name: no-cron-task
---

No cron field here.
""")

        schedule = await load_schedule(task_dir)

        assert schedule is None

    async def test_load_schedule_invalid_cron(self, tmp_path: anyio.Path) -> None:
        """Test loading schedule with invalid cron expression."""
        tmp = anyio.Path(tmp_path)
        task_dir = tmp / "invalid-cron"
        await task_dir.mkdir()

        task_file = task_dir / "TASK.md"
        await task_file.write_text("""---
name: invalid-cron-task
cron: "invalid cron"
---

Invalid cron expression.
""")

        # load_schedule should still return the schedule
        # The invalid cron will cause issues when trying to get next run
        schedule = await load_schedule(task_dir)

        # It should load, but getting next run will fail
        assert schedule is not None
        assert schedule.cron == "invalid cron"


class TestLoadSchedules:
    """Tests for load_schedules function."""

    async def test_load_schedules_from_workspace(self, tmp_path: anyio.Path) -> None:
        """Test loading all schedules from workspace."""
        tmp = anyio.Path(tmp_path)
        # Create schedules directory
        schedules_dir = tmp / "schedules"
        await schedules_dir.mkdir()

        # Create first task
        task1_dir = schedules_dir / "task1"
        await task1_dir.mkdir()
        await (task1_dir / "TASK.md").write_text("""---
name: task1
cron: "0 9 * * *"
---

Task 1 content.
""")

        # Create second task
        task2_dir = schedules_dir / "task2"
        await task2_dir.mkdir()
        await (task2_dir / "TASK.md").write_text("""---
name: task2
cron: "0 17 * * *"
---

Task 2 content.
""")

        schedules = await load_schedules(tmp)

        assert len(schedules) == 2
        names = [s.name for s in schedules]
        assert "task1" in names
        assert "task2" in names

    async def test_load_schedules_missing_directory(self, tmp_path: anyio.Path) -> None:
        """Test loading schedules when schedules directory doesn't exist."""
        tmp = anyio.Path(tmp_path)
        schedules = await load_schedules(tmp)

        assert schedules == []

    async def test_load_schedules_skips_invalid(self, tmp_path: anyio.Path) -> None:
        """Test that invalid schedules are skipped."""
        tmp = anyio.Path(tmp_path)
        schedules_dir = tmp / "schedules"
        await schedules_dir.mkdir()

        # Valid task
        task1_dir = schedules_dir / "valid-task"
        await task1_dir.mkdir()
        await (task1_dir / "TASK.md").write_text("""---
name: valid-task
cron: "0 9 * * *"
---

Valid task.
""")

        # Invalid task (no cron)
        task2_dir = schedules_dir / "invalid-task"
        await task2_dir.mkdir()
        await (task2_dir / "TASK.md").write_text("""---
name: invalid-task
---

No cron field.
""")

        schedules = await load_schedules(tmp)

        assert len(schedules) == 1
        assert schedules[0].name == "valid-task"


class TestScheduleExecutor:
    """Tests for ScheduleExecutor class."""

    def test_executor_creation(self) -> None:
        """Test creating a ScheduleExecutor."""
        mock_runner = MagicMock()
        schedules = [
            Schedule(
                name="test-task",
                cron="0 9 * * *",
                content="Test content",
                task_dir=anyio.Path("/tmp/test"),
            )
        ]

        executor = ScheduleExecutor(schedules, mock_runner)

        assert executor.schedules == schedules
        assert executor.runner == mock_runner
        assert executor._running is False

    async def test_executor_start_stop(self) -> None:
        """Test starting and stopping the executor."""
        mock_runner = MagicMock()
        schedules = [
            Schedule(
                name="test-task",
                cron="0 9 * * *",
                content="Test content",
                task_dir=anyio.Path("/tmp/test"),
            )
        ]

        executor = ScheduleExecutor(schedules, mock_runner)

        # Start executor
        await executor.start()
        assert executor._running is True
        assert len(executor._tasks) == 1

        # Stop executor
        await executor.stop()
        assert executor._running is False

    async def test_executor_start_empty_schedules(self) -> None:
        """Test starting executor with no schedules."""
        mock_runner = MagicMock()
        executor = ScheduleExecutor([], mock_runner)

        await executor.start()

        assert executor._running is False
        assert len(executor._tasks) == 0

    async def test_executor_add_schedule(self) -> None:
        """Test adding a schedule to running executor."""
        mock_runner = MagicMock()
        # Start with one schedule so executor starts properly
        initial_schedule = Schedule(
            name="initial-task",
            cron="0 9 * * *",
            content="Initial task content",
            task_dir=anyio.Path("/tmp/initial"),
        )
        executor = ScheduleExecutor([initial_schedule], mock_runner)

        await executor.start()

        new_schedule = Schedule(
            name="new-task",
            cron="0 10 * * *",
            content="New task content",
            task_dir=anyio.Path("/tmp/new"),
        )

        await executor.add_schedule(new_schedule)

        assert len(executor.schedules) == 2
        assert "new-task" in executor._schedule_map

        await executor.stop()

    async def test_executor_remove_schedule(self) -> None:
        """Test removing a schedule from running executor."""
        mock_runner = MagicMock()
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Test content",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)

        await executor.start()
        assert len(executor.schedules) == 1

        await executor.remove_schedule("test-task")
        assert len(executor.schedules) == 0
        assert "test-task" not in executor._schedule_map

        await executor.stop()

    async def test_executor_remove_nonexistent_schedule(self) -> None:
        """Test removing a schedule that doesn't exist."""
        mock_runner = MagicMock()
        executor = ScheduleExecutor([], mock_runner)

        # Should not raise error
        await executor.remove_schedule("nonexistent")

    async def test_executor_update_schedule(self) -> None:
        """Test updating a schedule."""
        mock_runner = MagicMock()
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Original content",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)

        await executor.start()

        updated_schedule = Schedule(
            name="test-task",
            cron="0 10 * * *",
            content="Updated content",
            task_dir=anyio.Path("/tmp/test"),
        )

        await executor.update_schedule(updated_schedule)

        assert len(executor.schedules) == 1
        assert executor.schedules[0].cron == "0 10 * * *"
        assert executor.schedules[0].content == "Updated content"

        await executor.stop()

    async def test_executor_handles_task_execution_error(self) -> None:
        """Test that executor handles errors during task execution."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock(side_effect=Exception("Test error"))

        schedule = Schedule(
            name="test-task",
            cron="* * * * *",  # Every minute
            content="Test content",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)

        # Execute task directly
        await executor._execute_task(schedule)

        # Should not raise, error is logged
        mock_runner.process_request.assert_called_once()
