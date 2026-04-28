"""Tests for workspace watcher change detection."""

from __future__ import annotations

from pathlib import Path

from psi_agent.session.workspace_watcher import (
    ChangeSummary,
    WorkspaceWatcher,
    compute_file_hash,
    scan_schedules_directory,
    scan_skills_directory,
    scan_tools_directory,
)


class TestComputeFileHash:
    """Tests for compute_file_hash function."""

    def test_compute_hash_returns_string(self, tmp_path: Path) -> None:
        """Test that compute_file_hash returns a string."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        result = compute_file_hash(test_file)

        assert isinstance(result, str)
        assert len(result) == 32  # MD5 hash is 32 hex characters

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        """Test that same content produces same hash."""
        test_file1 = tmp_path / "test1.py"
        test_file2 = tmp_path / "test2.py"
        content = "print('hello')"
        test_file1.write_text(content)
        test_file2.write_text(content)

        hash1 = compute_file_hash(test_file1)
        hash2 = compute_file_hash(test_file2)

        assert hash1 == hash2

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        """Test that different content produces different hash."""
        test_file1 = tmp_path / "test1.py"
        test_file2 = tmp_path / "test2.py"
        test_file1.write_text("print('hello')")
        test_file2.write_text("print('world')")

        hash1 = compute_file_hash(test_file1)
        hash2 = compute_file_hash(test_file2)

        assert hash1 != hash2


class TestScanToolsDirectory:
    """Tests for scan_tools_directory function."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning empty directory."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()

        result = scan_tools_directory(tools_dir)

        assert result == {}

    def test_scan_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test scanning nonexistent directory."""
        result = scan_tools_directory(tmp_path / "nonexistent")

        assert result == {}

    def test_scan_finds_python_files(self, tmp_path: Path) -> None:
        """Test that scan finds .py files."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "read.py").write_text("async def tool(): pass")
        (tools_dir / "write.py").write_text("async def tool(): pass")

        result = scan_tools_directory(tools_dir)

        assert len(result) == 2
        assert "read" in result
        assert "write" in result

    def test_scan_ignores_non_python_files(self, tmp_path: Path) -> None:
        """Test that scan ignores non-.py files."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "read.py").write_text("async def tool(): pass")
        (tools_dir / "read.txt").write_text("not a tool")

        result = scan_tools_directory(tools_dir)

        assert len(result) == 1
        assert "read" in result


class TestScanSkillsDirectory:
    """Tests for scan_skills_directory function."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning empty directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        result = scan_skills_directory(skills_dir)

        assert result == {}

    def test_scan_finds_skill_md_files(self, tmp_path: Path) -> None:
        """Test that scan finds SKILL.md files."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill1_dir = skills_dir / "skill1"
        skill1_dir.mkdir()
        (skill1_dir / "SKILL.md").write_text("---\nname: skill1\n---\nContent")
        skill2_dir = skills_dir / "skill2"
        skill2_dir.mkdir()
        (skill2_dir / "SKILL.md").write_text("---\nname: skill2\n---\nContent")

        result = scan_skills_directory(skills_dir)

        assert len(result) == 2
        assert "skill1" in result
        assert "skill2" in result

    def test_scan_ignores_dirs_without_skill_md(self, tmp_path: Path) -> None:
        """Test that scan ignores directories without SKILL.md."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "skill1"
        skill_dir.mkdir()
        (skill_dir / "README.md").write_text("Not a skill")

        result = scan_skills_directory(skills_dir)

        assert result == {}


class TestScanSchedulesDirectory:
    """Tests for scan_schedules_directory function."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning empty directory."""
        schedules_dir = tmp_path / "schedules"
        schedules_dir.mkdir()

        result = scan_schedules_directory(schedules_dir)

        assert result == {}

    def test_scan_finds_task_md_files(self, tmp_path: Path) -> None:
        """Test that scan finds TASK.md files."""
        schedules_dir = tmp_path / "schedules"
        schedules_dir.mkdir()
        task1_dir = schedules_dir / "task1"
        task1_dir.mkdir()
        (task1_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")
        task2_dir = schedules_dir / "task2"
        task2_dir.mkdir()
        (task2_dir / "TASK.md").write_text("---\ncron: '0 10 * * *'\n---\nContent")

        result = scan_schedules_directory(schedules_dir)

        assert len(result) == 2
        assert "task1" in result
        assert "task2" in result


class TestChangeSummary:
    """Tests for ChangeSummary class."""

    def test_empty_summary_has_no_changes(self) -> None:
        """Test that empty summary reports no changes."""
        summary = ChangeSummary()

        assert not summary.tools_changed
        assert not summary.skills_changed
        assert not summary.schedules_changed
        assert not summary.has_changes

    def test_tools_added_triggers_tools_changed(self) -> None:
        """Test that tools_added triggers tools_changed."""
        summary = ChangeSummary(tools_added=["new_tool"])

        assert summary.tools_changed
        assert not summary.skills_changed
        assert summary.has_changes

    def test_skills_modified_triggers_skills_changed(self) -> None:
        """Test that skills_modified triggers skills_changed."""
        summary = ChangeSummary(skills_modified=["skill1"])

        assert not summary.tools_changed
        assert summary.skills_changed
        assert summary.has_changes

    def test_schedules_removed_triggers_schedules_changed(self) -> None:
        """Test that schedules_removed triggers schedules_changed."""
        summary = ChangeSummary(schedules_removed=["old_schedule"])

        assert summary.schedules_changed
        assert summary.has_changes

    def test_to_dict_structure(self) -> None:
        """Test that to_dict returns correct structure."""
        summary = ChangeSummary(
            tools_added=["tool1"],
            skills_modified=["skill1"],
            schedules_removed=["schedule1"],
        )

        result = summary.to_dict()

        assert result["tools"]["added"] == ["tool1"]
        assert result["skills"]["modified"] == ["skill1"]
        assert result["schedules"]["removed"] == ["schedule1"]


class TestWorkspaceWatcher:
    """Tests for WorkspaceWatcher class."""

    def test_initialize_scans_all_directories(self, tmp_path: Path) -> None:
        """Test that initialize scans all workspace directories."""
        # Create workspace structure
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "read.py").write_text("async def tool(): pass")

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "skill1"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: skill1\n---\nContent")

        schedules_dir = tmp_path / "schedules"
        schedules_dir.mkdir()
        task_dir = schedules_dir / "task1"
        task_dir.mkdir()
        (task_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")

        watcher = WorkspaceWatcher(tmp_path)
        watcher.initialize()

        assert len(watcher.get_tool_hashes()) == 1
        assert len(watcher.get_skill_hashes()) == 1
        assert len(watcher.get_schedule_hashes()) == 1

    def test_check_for_changes_detects_new_tool(self, tmp_path: Path) -> None:
        """Test that check_for_changes detects new tool."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "read.py").write_text("async def tool(): pass")

        watcher = WorkspaceWatcher(tmp_path)
        watcher.initialize()

        # Add new tool
        (tools_dir / "write.py").write_text("async def tool(): pass")

        changes = watcher.check_for_changes()

        assert "write" in changes.tools_added
        assert changes.tools_changed

    def test_check_for_changes_detects_modified_skill(self, tmp_path: Path) -> None:
        """Test that check_for_changes detects modified skill."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "skill1"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: skill1\n---\nOriginal content")

        watcher = WorkspaceWatcher(tmp_path)
        watcher.initialize()

        # Modify skill
        skill_md.write_text("---\nname: skill1\n---\nModified content")

        changes = watcher.check_for_changes()

        assert "skill1" in changes.skills_modified
        assert changes.skills_changed

    def test_check_for_changes_detects_removed_schedule(self, tmp_path: Path) -> None:
        """Test that check_for_changes detects removed schedule."""
        schedules_dir = tmp_path / "schedules"
        schedules_dir.mkdir()
        task_dir = schedules_dir / "task1"
        task_dir.mkdir()
        (task_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")

        watcher = WorkspaceWatcher(tmp_path)
        watcher.initialize()

        # Remove schedule
        (task_dir / "TASK.md").unlink()
        task_dir.rmdir()

        changes = watcher.check_for_changes()

        assert "task1" in changes.schedules_removed
        assert changes.schedules_changed

    def test_check_for_changes_no_changes(self, tmp_path: Path) -> None:
        """Test that check_for_changes returns empty when no changes."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "read.py").write_text("async def tool(): pass")

        watcher = WorkspaceWatcher(tmp_path)
        watcher.initialize()

        # No changes made
        changes = watcher.check_for_changes()

        assert not changes.has_changes
