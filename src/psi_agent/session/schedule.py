"""Schedule loading and execution for psi-session."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

import anyio
import croniter
from loguru import logger

if TYPE_CHECKING:
    from psi_agent.session.runner import SessionRunner


@dataclass
class Schedule:
    """A scheduled task with cron expression.

    Attributes:
        name: Task name from frontmatter.
        description: Task description from frontmatter.
        cron: Cron expression for scheduling.
        content: Task instruction content (after frontmatter).
        task_dir: Path to the task directory.
    """

    name: str
    cron: str
    content: str
    task_dir: Path
    description: str = ""
    _croniter: croniter.croniter | None = field(default=None, repr=False, compare=False)

    def get_next_run(self) -> datetime:
        """Get the next run time based on cron expression.

        Returns:
            Next scheduled datetime.
        """
        if self._croniter is None:
            self._croniter = croniter.croniter(self.cron, datetime.now())
        return cast(datetime, self._croniter.get_next(datetime))

    def get_seconds_until_next_run(self) -> float:
        """Get seconds until next scheduled run.

        Returns:
            Seconds until next run.
        """
        next_run = self.get_next_run()
        now = datetime.now()
        delta = next_run - now
        return max(0.0, delta.total_seconds())


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from content.

    Args:
        content: File content with optional frontmatter.

    Returns:
        Tuple of (frontmatter dict, remaining content).
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    remaining = match.group(2)

    # Parse simple YAML key: value pairs
    frontmatter: dict[str, str] = {}
    for line in frontmatter_str.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            value = value.strip()
            # Strip quotes if present
            is_double_quoted = value.startswith('"') and value.endswith('"')
            is_single_quoted = value.startswith("'") and value.endswith("'")
            if is_double_quoted or is_single_quoted:
                value = value[1:-1]
            frontmatter[key.strip()] = value

    return frontmatter, remaining


async def load_schedule(task_dir: Path) -> Schedule | None:
    """Load a schedule from a task directory.

    Args:
        task_dir: Path to the task directory containing TASK.md.

    Returns:
        Schedule object, or None if invalid.
    """
    task_file = task_dir / "TASK.md"
    if not await anyio.Path(task_file).exists():
        logger.debug(f"No TASK.md in {task_dir}")
        return None

    try:
        async with await anyio.open_file(task_file) as f:
            content = await f.read()

        frontmatter, task_content = parse_frontmatter(content)

        # Check required fields
        if "cron" not in frontmatter:
            logger.warning(f"Missing 'cron' field in {task_file}")
            return None

        name = frontmatter.get("name", task_dir.name)
        description = frontmatter.get("description", "")

        return Schedule(
            name=name,
            description=description,
            cron=frontmatter["cron"],
            content=task_content.strip(),
            task_dir=task_dir,
        )

    except Exception as e:
        logger.error(f"Failed to load schedule from {task_dir}: {e}")
        return None


async def load_schedules(workspace: Path) -> list[Schedule]:
    """Load all schedules from workspace.

    Args:
        workspace: Path to workspace directory.

    Returns:
        List of valid Schedule objects.
    """
    schedules_dir = workspace / "schedules"
    if not await anyio.Path(schedules_dir).exists():
        logger.debug("No schedules directory in workspace")
        return []

    schedules = []
    async for entry in anyio.Path(schedules_dir).iterdir():
        if await anyio.Path(entry).is_dir():
            schedule = await load_schedule(Path(entry))
            if schedule is not None:
                schedules.append(schedule)
                logger.info(f"Loaded schedule: {schedule.name} (cron: {schedule.cron})")

    return schedules


class ScheduleExecutor:
    """Executor for running scheduled tasks."""

    def __init__(self, schedules: list[Schedule], runner: SessionRunner) -> None:
        """Initialize the executor.

        Args:
            schedules: List of schedules to execute.
            runner: Session runner to use for task execution.
        """
        self.schedules = schedules
        self.runner = runner
        self._tasks: list[asyncio.Task[None]] = []
        self._running = False
        self._schedule_map: dict[str, asyncio.Task[None]] = {}

    async def start(self) -> None:
        """Start all schedule loops."""
        if not self.schedules:
            logger.info("No schedules to run")
            return

        self._running = True
        for schedule in self.schedules:
            task = asyncio.create_task(self._schedule_loop(schedule))
            self._tasks.append(task)
            self._schedule_map[schedule.name] = task
            logger.info(f"Started schedule loop for: {schedule.name}")

    async def stop(self) -> None:
        """Stop all schedule loops."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        logger.info("Stopped all schedule loops")

    async def _schedule_loop(self, schedule: Schedule) -> None:
        """Run a single schedule loop.

        Args:
            schedule: The schedule to run.
        """
        while self._running:
            try:
                # Calculate wait time
                delay = schedule.get_seconds_until_next_run()
                next_run = schedule.get_next_run()
                logger.debug(f"Schedule '{schedule.name}' next run at {next_run}")

                # Wait until scheduled time
                await asyncio.sleep(delay)

                if not self._running:
                    break

                # Execute the task
                logger.info(f"Executing scheduled task: {schedule.name}")
                await self._execute_task(schedule)

            except asyncio.CancelledError:
                logger.debug(f"Schedule loop cancelled for: {schedule.name}")
                break
            except Exception as e:
                logger.error(f"Error in schedule loop for {schedule.name}: {e}")
                # Continue running despite errors
                await asyncio.sleep(60)  # Wait a minute before retry

    async def _execute_task(self, schedule: Schedule) -> None:
        """Execute a scheduled task.

        Args:
            schedule: The schedule to execute.
        """
        try:
            logger.debug(
                f"Executing schedule '{schedule.name}' with content: {schedule.content[:200]}..."
            )
            user_message = {"role": "user", "content": schedule.content}
            await self.runner.process_request(user_message)
            logger.info(f"Completed scheduled task: {schedule.name}")
        except Exception as e:
            logger.error(f"Failed to execute scheduled task {schedule.name}: {e}")

    async def add_schedule(self, schedule: Schedule) -> None:
        """Add a new schedule to the executor.

        Args:
            schedule: The schedule to add.
        """
        self.schedules.append(schedule)
        if self._running:
            task = asyncio.create_task(self._schedule_loop(schedule))
            self._tasks.append(task)
            self._schedule_map[schedule.name] = task
            logger.info(f"Added and started schedule: {schedule.name}")

    async def remove_schedule(self, schedule_name: str) -> None:
        """Remove a schedule from the executor.

        Args:
            schedule_name: Name of the schedule to remove.
        """
        # Find and remove from list
        schedule_to_remove = None
        for schedule in self.schedules:
            if schedule.name == schedule_name:
                schedule_to_remove = schedule
                break

        if schedule_to_remove is None:
            logger.warning(f"Schedule not found: {schedule_name}")
            return

        self.schedules.remove(schedule_to_remove)

        # Cancel running task if exists
        if schedule_name in self._schedule_map:
            task = self._schedule_map[schedule_name]
            task.cancel()
            del self._schedule_map[schedule_name]
            # Also remove from _tasks list
            if task in self._tasks:
                self._tasks.remove(task)
            logger.info(f"Removed schedule: {schedule_name}")

    async def update_schedule(self, schedule: Schedule) -> None:
        """Update an existing schedule.

        Args:
            schedule: The updated schedule.
        """
        # Remove old one and add new one
        await self.remove_schedule(schedule.name)
        await self.add_schedule(schedule)
        logger.info(f"Updated schedule: {schedule.name}")
