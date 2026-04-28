"""Workspace file change detection for hot-reload support."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class ChangeSummary:
    """Summary of detected workspace changes.

    Attributes:
        tools_added: List of newly added tool names.
        tools_removed: List of removed tool names.
        tools_modified: List of modified tool names.
        skills_added: List of newly added skill names.
        skills_removed: List of removed skill names.
        skills_modified: List of modified skill names.
        schedules_added: List of newly added schedule names.
        schedules_removed: List of removed schedule names.
        schedules_modified: List of modified schedule names.
    """

    tools_added: list[str] = field(default_factory=list)
    tools_removed: list[str] = field(default_factory=list)
    tools_modified: list[str] = field(default_factory=list)
    skills_added: list[str] = field(default_factory=list)
    skills_removed: list[str] = field(default_factory=list)
    skills_modified: list[str] = field(default_factory=list)
    schedules_added: list[str] = field(default_factory=list)
    schedules_removed: list[str] = field(default_factory=list)
    schedules_modified: list[str] = field(default_factory=list)

    @property
    def tools_changed(self) -> bool:
        """Check if any tools changed."""
        return bool(self.tools_added or self.tools_removed or self.tools_modified)

    @property
    def skills_changed(self) -> bool:
        """Check if any skills changed."""
        return bool(self.skills_added or self.skills_removed or self.skills_modified)

    @property
    def schedules_changed(self) -> bool:
        """Check if any schedules changed."""
        return bool(self.schedules_added or self.schedules_removed or self.schedules_modified)

    @property
    def has_changes(self) -> bool:
        """Check if any changes were detected."""
        return self.tools_changed or self.skills_changed or self.schedules_changed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "tools": {
                "added": self.tools_added,
                "removed": self.tools_removed,
                "modified": self.tools_modified,
            },
            "skills": {
                "added": self.skills_added,
                "removed": self.skills_removed,
                "modified": self.skills_modified,
            },
            "schedules": {
                "added": self.schedules_added,
                "removed": self.schedules_removed,
                "modified": self.schedules_modified,
            },
        }


def compute_file_hash(file_path: Path) -> str:
    """Compute MD5 hash of a file.

    Args:
        file_path: Path to the file.

    Returns:
        MD5 hash string.
    """
    content = file_path.read_bytes()
    return hashlib.md5(content).hexdigest()


def scan_tools_directory(tools_dir: Path) -> dict[str, tuple[Path, str]]:
    """Scan tools directory and return file info.

    Args:
        tools_dir: Path to the tools directory.

    Returns:
        Dict mapping tool name to (file_path, file_hash).
    """
    if not tools_dir.exists():
        return {}

    tool_files: dict[str, tuple[Path, str]] = {}

    for file_path in tools_dir.iterdir():
        if file_path.is_file() and file_path.suffix == ".py":
            tool_name = file_path.stem
            file_hash = compute_file_hash(file_path)
            tool_files[tool_name] = (file_path, file_hash)

    return tool_files


def scan_skills_directory(skills_dir: Path) -> dict[str, tuple[Path, str]]:
    """Scan skills directory and return file info.

    Args:
        skills_dir: Path to the skills directory.

    Returns:
        Dict mapping skill name to (skill_md_path, file_hash).
    """
    if not skills_dir.exists():
        return {}

    skill_files: dict[str, tuple[Path, str]] = {}

    for entry in skills_dir.iterdir():
        if entry.is_dir():
            skill_md = entry / "SKILL.md"
            if skill_md.exists():
                skill_name = entry.name
                file_hash = compute_file_hash(skill_md)
                skill_files[skill_name] = (skill_md, file_hash)

    return skill_files


def scan_schedules_directory(schedules_dir: Path) -> dict[str, tuple[Path, str]]:
    """Scan schedules directory and return file info.

    Args:
        schedules_dir: Path to the schedules directory.

    Returns:
        Dict mapping schedule name to (task_md_path, file_hash).
    """
    if not schedules_dir.exists():
        return {}

    schedule_files: dict[str, tuple[Path, str]] = {}

    for entry in schedules_dir.iterdir():
        if entry.is_dir():
            task_md = entry / "TASK.md"
            if task_md.exists():
                schedule_name = entry.name
                file_hash = compute_file_hash(task_md)
                schedule_files[schedule_name] = (task_md, file_hash)

    return schedule_files


class WorkspaceWatcher:
    """Watches workspace files for changes and detects modifications."""

    def __init__(self, workspace: Path) -> None:
        """Initialize the workspace watcher.

        Args:
            workspace: Path to the workspace directory.
        """
        self.workspace = workspace
        self._tool_hashes: dict[str, str] = {}
        self._skill_hashes: dict[str, str] = {}
        self._schedule_hashes: dict[str, str] = {}

    def initialize(self) -> None:
        """Initialize hashes for all workspace files.

        Should be called once at session startup.
        """
        tools_dir = self.workspace / "tools"
        skills_dir = self.workspace / "skills"
        schedules_dir = self.workspace / "schedules"

        # Scan and store initial hashes
        tool_files = scan_tools_directory(tools_dir)
        self._tool_hashes = {name: hash_ for name, (_, hash_) in tool_files.items()}

        skill_files = scan_skills_directory(skills_dir)
        self._skill_hashes = {name: hash_ for name, (_, hash_) in skill_files.items()}

        schedule_files = scan_schedules_directory(schedules_dir)
        self._schedule_hashes = {name: hash_ for name, (_, hash_) in schedule_files.items()}

        logger.debug(
            f"WorkspaceWatcher initialized: {len(self._tool_hashes)} tools, "
            f"{len(self._skill_hashes)} skills, {len(self._schedule_hashes)} schedules"
        )

    def check_for_changes(self) -> ChangeSummary:
        """Check for changes in workspace files.

        Returns:
            ChangeSummary with all detected changes.
        """
        tools_dir = self.workspace / "tools"
        skills_dir = self.workspace / "skills"
        schedules_dir = self.workspace / "schedules"

        summary = ChangeSummary()

        # Check tools
        current_tools = scan_tools_directory(tools_dir)
        current_tool_names = set(current_tools.keys())
        stored_tool_names = set(self._tool_hashes.keys())

        # New tools
        for name in current_tool_names - stored_tool_names:
            summary.tools_added.append(name)
            _, hash_ = current_tools[name]
            self._tool_hashes[name] = hash_
            logger.info(f"Detected new tool: {name}")

        # Removed tools
        for name in stored_tool_names - current_tool_names:
            summary.tools_removed.append(name)
            del self._tool_hashes[name]
            logger.info(f"Detected removed tool: {name}")

        # Modified tools
        for name in current_tool_names & stored_tool_names:
            _, new_hash = current_tools[name]
            if new_hash != self._tool_hashes[name]:
                summary.tools_modified.append(name)
                self._tool_hashes[name] = new_hash
                logger.info(f"Detected modified tool: {name}")

        # Check skills
        current_skills = scan_skills_directory(skills_dir)
        current_skill_names = set(current_skills.keys())
        stored_skill_names = set(self._skill_hashes.keys())

        # New skills
        for name in current_skill_names - stored_skill_names:
            summary.skills_added.append(name)
            _, hash_ = current_skills[name]
            self._skill_hashes[name] = hash_
            logger.info(f"Detected new skill: {name}")

        # Removed skills
        for name in stored_skill_names - current_skill_names:
            summary.skills_removed.append(name)
            del self._skill_hashes[name]
            logger.info(f"Detected removed skill: {name}")

        # Modified skills
        for name in current_skill_names & stored_skill_names:
            _, new_hash = current_skills[name]
            if new_hash != self._skill_hashes[name]:
                summary.skills_modified.append(name)
                self._skill_hashes[name] = new_hash
                logger.info(f"Detected modified skill: {name}")

        # Check schedules
        current_schedules = scan_schedules_directory(schedules_dir)
        current_schedule_names = set(current_schedules.keys())
        stored_schedule_names = set(self._schedule_hashes.keys())

        # New schedules
        for name in current_schedule_names - stored_schedule_names:
            summary.schedules_added.append(name)
            _, hash_ = current_schedules[name]
            self._schedule_hashes[name] = hash_
            logger.info(f"Detected new schedule: {name}")

        # Removed schedules
        for name in stored_schedule_names - current_schedule_names:
            summary.schedules_removed.append(name)
            del self._schedule_hashes[name]
            logger.info(f"Detected removed schedule: {name}")

        # Modified schedules
        for name in current_schedule_names & stored_schedule_names:
            _, new_hash = current_schedules[name]
            if new_hash != self._schedule_hashes[name]:
                summary.schedules_modified.append(name)
                self._schedule_hashes[name] = new_hash
                logger.info(f"Detected modified schedule: {name}")

        if summary.has_changes:
            logger.info(f"Workspace changes detected: {summary.to_dict()}")

        return summary

    def get_tool_hashes(self) -> dict[str, str]:
        """Get current tool hashes.

        Returns:
            Dict mapping tool name to hash.
        """
        return dict(self._tool_hashes)

    def get_skill_hashes(self) -> dict[str, str]:
        """Get current skill hashes.

        Returns:
            Dict mapping skill name to hash.
        """
        return dict(self._skill_hashes)

    def get_schedule_hashes(self) -> dict[str, str]:
        """Get current schedule hashes.

        Returns:
            Dict mapping schedule name to hash.
        """
        return dict(self._schedule_hashes)
