"""Tests for Schedule dataclass."""

from datetime import datetime
from pathlib import Path

from psi_agent.session.schedule import Schedule


class TestSchedule:
    """Tests for Schedule class."""

    def test_schedule_creation(self) -> None:
        """Test Schedule can be created with required fields."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",
            content="Test task content",
            task_dir=Path("/tmp/test"),
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
            task_dir=Path("/tmp/test"),
        )

        assert schedule.description == "A test task"

    def test_get_next_run(self) -> None:
        """Test get_next_run returns a future datetime."""
        schedule = Schedule(
            name="test-task",
            cron="0 9 * * *",  # 9am daily
            content="Test task content",
            task_dir=Path("/tmp/test"),
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
            task_dir=Path("/tmp/test"),
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
            task_dir=Path("/tmp/test"),
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
            task_dir=Path("/tmp/test"),
        )

        next_run = schedule.get_next_run()

        assert next_run.minute == 30
        assert next_run.hour == 14
