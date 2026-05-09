"""Tests for Schedule dataclass."""

from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

from psi_agent.session.schedule import Schedule, ScheduleExecutor


class TestSchedule:
    """Tests for Schedule class."""

    def test_schedule_creation(self) -> None:
        """Test Schedule can be created with required fields."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Test task content",
            task_dir=anyio.Path("/tmp/test"),
        )

        assert schedule.name == "test-task"
        assert schedule.cron == "0 9 * * *"
        assert schedule.content == "Test task content"
        assert schedule.description == ""

    def test_schedule_with_description(self) -> None:
        """Test Schedule with optional description."""
        schedule = Schedule(
            name="test-task",
            description="A test task",
            cron="0 9 * * *",
            content="Test task content",
            task_dir=anyio.Path("/tmp/test"),
        )

        assert schedule.description == "A test task"

    def test_get_next_run(self) -> None:
        """Test get_next_run returns a future datetime."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",  # 9am daily
            content="Test task content",
            task_dir=anyio.Path("/tmp/test"),
        )

        next_run = schedule.get_next_run()

        assert isinstance(next_run, datetime)
        assert next_run > datetime.now()

    def test_get_seconds_until_next_run(self) -> None:
        """Test get_seconds_until_next_run returns positive value."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Test task content",
            task_dir=anyio.Path("/tmp/test"),
        )

        seconds = schedule.get_seconds_until_next_run()

        assert seconds >= 0
        assert isinstance(seconds, float)

    def test_cron_every_minute(self) -> None:
        """Test cron expression for every minute."""
        schedule = Schedule(
            name="test-task",
            cron="* * * * *",
            content="Test task content",
            task_dir=anyio.Path("/tmp/test"),
        )

        next_run = schedule.get_next_run()

        # Should be within the next minute
        assert isinstance(next_run, datetime)

    def test_cron_specific_time(self) -> None:
        """Test cron expression for specific time."""
        schedule = Schedule(
            name="test-task",
            cron="30 14 * * *",  # 2:30pm daily
            content="Test task content",
            task_dir=anyio.Path("/tmp/test"),
        )

        next_run = schedule.get_next_run()

        assert next_run.minute == 30
        assert next_run.hour == 14


class TestScheduleExecutorExceptionAndRetry:
    """Tests for _schedule_loop exception handling, CancelledError, and immediate execution."""

    @pytest.mark.asyncio
    async def test_schedule_loop_exception_sleeps_and_retries(self) -> None:
        """Test that _schedule_loop sleeps 60s on exception and retries."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="test_task",
            cron="* * * * *",
            content="Do something",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)
        executor._running = True

        call_count = 0

        def get_seconds_side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Transient error")
            # On subsequent calls, stop the loop after execution
            executor._running = False
            return 0.0

        with patch.object(
            schedule, "get_seconds_until_next_run", side_effect=get_seconds_side_effect
        ), patch.object(schedule, "get_next_run", return_value=datetime.now()), patch(
            "psi_agent.session.schedule.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            await executor._schedule_loop(schedule)

        # First call raised exception, second call succeeded
        assert call_count == 2
        # After exception, sleep(60) is called for retry
        mock_sleep.assert_any_call(60)

    @pytest.mark.asyncio
    async def test_schedule_loop_cancelled_error_clean_exit(self) -> None:
        """Test that CancelledError causes clean exit from _schedule_loop."""
        mock_runner = MagicMock()

        schedule = Schedule(
            name="test_task",
            cron="* * * * *",
            content="Do something",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)
        executor._running = True

        async def raise_cancelled(*args, **kwargs):
            raise asyncio.CancelledError()

        mock_runner.process_request = AsyncMock(side_effect=raise_cancelled)

        with (
            patch.object(schedule, "get_seconds_until_next_run", return_value=0.0),
            patch.object(schedule, "get_next_run", return_value=datetime.now()),
            patch("psi_agent.session.schedule.asyncio.sleep", new_callable=AsyncMock),
        ):
            await executor._schedule_loop(schedule)

        # CancelledError should cause clean exit after the call that raised it
        mock_runner.process_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_loop_immediate_execution_when_due(self) -> None:
        """Test immediate execution when next run is due (0 seconds delay)."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="test_task",
            cron="* * * * *",
            content="Do something",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)
        executor._running = True

        call_count = 0

        async def stop_after_one(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            executor._running = False

        mock_runner.process_request = AsyncMock(side_effect=stop_after_one)

        # Mock get_seconds_until_next_run to return 0 (immediate)
        with (
            patch.object(schedule, "get_seconds_until_next_run", return_value=0.0),
            patch.object(schedule, "get_next_run", return_value=datetime.now()),
            patch(
                "psi_agent.session.schedule.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep,
        ):
            await executor._schedule_loop(schedule)

        assert call_count == 1
        # sleep(0) should be called for immediate execution
        mock_sleep.assert_called_once_with(0.0)


class TestScheduleExecutorConcurrentOperation:
    """Tests for concurrent operations on the schedule executor."""

    @pytest.mark.asyncio
    async def test_add_schedule_with_duplicate_name(self) -> None:
        """Test that add_schedule with duplicate name creates a second task entry."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule1 = Schedule(
            name="duplicate_task",
            cron="0 9 * * *",
            content="First",
            task_dir=anyio.Path("/tmp/test1"),
        )
        schedule2 = Schedule(
            name="duplicate_task",
            cron="0 10 * * *",
            content="Second",
            task_dir=anyio.Path("/tmp/test2"),
        )

        executor = ScheduleExecutor([schedule1], mock_runner)
        await executor.start()

        # Adding a schedule with the same name should still add it
        await executor.add_schedule(schedule2)

        # Both schedules are in the list (no deduplication)
        assert len(executor.schedules) == 2
        # The _schedule_map maps name to task, so the second one overwrites
        assert "duplicate_task" in executor._schedule_map

        await executor.stop()

    @pytest.mark.asyncio
    async def test_add_schedule_when_executor_not_running(self) -> None:
        """Test that add_schedule when executor not running only adds to list, no task created."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="offline_task",
            cron="0 9 * * *",
            content="Test",
            task_dir=anyio.Path("/tmp/test"),
        )

        executor = ScheduleExecutor([], mock_runner)
        # Not started, so _running is False

        await executor.add_schedule(schedule)

        # Schedule should be in the list but no task created
        assert len(executor.schedules) == 1
        assert "offline_task" not in executor._schedule_map
        assert len(executor._tasks) == 0

    @pytest.mark.asyncio
    async def test_remove_schedule_that_is_currently_executing(self) -> None:
        """Test removing a schedule while its task is executing."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="executing_task",
            cron="* * * * *",
            content="Do something",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)
        await executor.start()

        # The task is running in the background; remove it
        await executor.remove_schedule("executing_task")

        assert len(executor.schedules) == 0
        assert "executing_task" not in executor._schedule_map
        assert len(executor._tasks) == 0

        await executor.stop()

    @pytest.mark.asyncio
    async def test_update_schedule_that_is_currently_executing(self) -> None:
        """Test updating a schedule while its task is executing."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="running_task",
            cron="0 9 * * *",
            content="Original",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)
        await executor.start()

        updated = Schedule(
            name="running_task",
            cron="0 10 * * *",
            content="Updated",
            task_dir=anyio.Path("/tmp/test"),
        )
        await executor.update_schedule(updated)

        assert len(executor.schedules) == 1
        assert executor.schedules[0].content == "Updated"
        assert executor.schedules[0].cron == "0 10 * * *"

        await executor.stop()


class TestScheduleExecutorDoubleStartStop:
    """Tests for double start and double stop behavior."""

    @pytest.mark.asyncio
    async def test_double_start_creates_duplicate_tasks(self) -> None:
        """Test that calling start twice creates duplicate tasks (documents current behavior)."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="test_task",
            cron="0 9 * * *",
            content="Test",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)

        await executor.start()
        initial_task_count = len(executor._tasks)

        # Call start again - currently creates duplicate tasks
        await executor.start()

        # Double start creates duplicate tasks since start() doesn't check for existing tasks
        assert len(executor._tasks) == initial_task_count + 1

        await executor.stop()

    @pytest.mark.asyncio
    async def test_double_stop_no_exception(self) -> None:
        """Test that calling stop twice does not raise an exception."""
        mock_runner = MagicMock()
        mock_runner.process_request = AsyncMock()

        schedule = Schedule(
            name="test_task",
            cron="0 9 * * *",
            content="Test",
            task_dir=anyio.Path("/tmp/test"),
        )
        executor = ScheduleExecutor([schedule], mock_runner)

        await executor.start()
        await executor.stop()

        # Second stop should not raise any exception
        await executor.stop()
        assert executor._running is False
