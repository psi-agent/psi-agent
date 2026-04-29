"""Tests for cron expression parsing."""

from __future__ import annotations

from datetime import datetime

import anyio

from psi_agent.session.schedule import Schedule


class TestCronParsing:
    """Tests for cron expression parsing."""

    def test_every_minute(self) -> None:
        """Test every minute cron expression."""
        schedule = Schedule(
            name="test",
            cron="* * * * *",
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert next_run > datetime.now()

    def test_specific_hour(self) -> None:
        """Test specific hour cron expression."""
        schedule = Schedule(
            name="test",
            cron="0 9 * * *",  # 9am daily
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert next_run.hour == 9
        assert next_run.minute == 0

    def test_specific_day_of_week(self) -> None:
        """Test specific day of week cron expression."""
        schedule = Schedule(
            name="test",
            cron="0 9 * * 1",  # 9am every Monday
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        # Monday is 0 in Python, but cron uses 0-7 where 0 and 7 are Sunday
        # croniter follows cron convention
        assert next_run.hour == 9
        assert next_run.minute == 0

    def test_specific_day_of_month(self) -> None:
        """Test specific day of month cron expression."""
        schedule = Schedule(
            name="test",
            cron="0 9 15 * *",  # 9am on 15th of every month
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert next_run.hour == 9
        assert next_run.minute == 0
        assert next_run.day == 15

    def test_specific_month(self) -> None:
        """Test specific month cron expression."""
        schedule = Schedule(
            name="test",
            cron="0 9 1 1 *",  # 9am on January 1st
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert next_run.hour == 9
        assert next_run.minute == 0
        assert next_run.day == 1
        assert next_run.month == 1

    def test_multiple_values(self) -> None:
        """Test multiple values in cron expression."""
        schedule = Schedule(
            name="test",
            cron="0 9,18 * * *",  # 9am and 6pm daily
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert next_run.hour in [9, 18]
        assert next_run.minute == 0

    def test_range(self) -> None:
        """Test range in cron expression."""
        schedule = Schedule(
            name="test",
            cron="0 9-17 * * *",  # Every hour from 9am to 5pm
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert 9 <= next_run.hour <= 17
        assert next_run.minute == 0

    def test_step(self) -> None:
        """Test step in cron expression."""
        schedule = Schedule(
            name="test",
            cron="*/15 * * * *",  # Every 15 minutes
            content="test",
            task_dir=anyio.Path("/tmp"),
        )

        next_run = schedule.get_next_run()
        assert next_run.minute % 15 == 0
