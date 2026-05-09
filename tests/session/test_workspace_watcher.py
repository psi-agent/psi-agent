"""Tests for workspace watcher change detection."""

from __future__ import annotations

import anyio
import pytest

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

    @pytest.mark.asyncio
    async def test_compute_hash_returns_string(self, tmp_path) -> None:
        """Test that compute_file_hash returns a string."""
        test_file = anyio.Path(tmp_path) / "test.py"
        await test_file.write_text("print('hello')")

        result = await compute_file_hash(test_file)

        assert isinstance(result, str)
        assert len(result) == 32  # MD5 hash is 32 hex characters

    @pytest.mark.asyncio
    async def test_same_content_same_hash(self, tmp_path) -> None:
        """Test that same content produces same hash."""
        test_file1 = anyio.Path(tmp_path) / "test1.py"
        test_file2 = anyio.Path(tmp_path) / "test2.py"
        content = "print('hello')"
        await test_file1.write_text(content)
        await test_file2.write_text(content)

        hash1 = await compute_file_hash(test_file1)
        hash2 = await compute_file_hash(test_file2)

        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_different_content_different_hash(self, tmp_path) -> None:
        """Test that different content produces different hash."""
        test_file1 = anyio.Path(tmp_path) / "test1.py"
        test_file2 = anyio.Path(tmp_path) / "test2.py"
        await test_file1.write_text("print('hello')")
        await test_file2.write_text("print('world')")

        hash1 = await compute_file_hash(test_file1)
        hash2 = await compute_file_hash(test_file2)

        assert hash1 != hash2


class TestScanToolsDirectory:
    """Tests for scan_tools_directory function."""

    @pytest.mark.asyncio
    async def test_scan_empty_directory(self, tmp_path) -> None:
        """Test scanning empty directory."""
        tools_dir = anyio.Path(tmp_path) / "tools"
        await tools_dir.mkdir()

        result = await scan_tools_directory(tools_dir)

        assert result == {}

    @pytest.mark.asyncio
    async def test_scan_nonexistent_directory(self, tmp_path) -> None:
        """Test scanning nonexistent directory."""
        result = await scan_tools_directory(anyio.Path(tmp_path) / "nonexistent")

        assert result == {}

    @pytest.mark.asyncio
    async def test_scan_finds_python_files(self, tmp_path) -> None:
        """Test that scan finds .py files."""
        tools_dir = anyio.Path(tmp_path) / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")
        await (tools_dir / "write.py").write_text("async def tool(): pass")

        result = await scan_tools_directory(tools_dir)

        assert len(result) == 2
        assert "read" in result
        assert "write" in result

    @pytest.mark.asyncio
    async def test_scan_ignores_non_python_files(self, tmp_path) -> None:
        """Test that scan ignores non-.py files."""
        tools_dir = anyio.Path(tmp_path) / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")
        await (tools_dir / "read.txt").write_text("not a tool")

        result = await scan_tools_directory(tools_dir)

        assert len(result) == 1
        assert "read" in result


class TestScanSkillsDirectory:
    """Tests for scan_skills_directory function."""

    @pytest.mark.asyncio
    async def test_scan_empty_directory(self, tmp_path) -> None:
        """Test scanning empty directory."""
        skills_dir = anyio.Path(tmp_path) / "skills"
        await skills_dir.mkdir()

        result = await scan_skills_directory(skills_dir)

        assert result == {}

    @pytest.mark.asyncio
    async def test_scan_finds_skill_md_files(self, tmp_path) -> None:
        """Test that scan finds SKILL.md files."""
        skills_dir = anyio.Path(tmp_path) / "skills"
        await skills_dir.mkdir()
        skill1_dir = skills_dir / "skill1"
        await skill1_dir.mkdir()
        await (skill1_dir / "SKILL.md").write_text("---\nname: skill1\n---\nContent")
        skill2_dir = skills_dir / "skill2"
        await skill2_dir.mkdir()
        await (skill2_dir / "SKILL.md").write_text("---\nname: skill2\n---\nContent")

        result = await scan_skills_directory(skills_dir)

        assert len(result) == 2
        assert "skill1" in result
        assert "skill2" in result

    @pytest.mark.asyncio
    async def test_scan_ignores_dirs_without_skill_md(self, tmp_path) -> None:
        """Test that scan ignores directories without SKILL.md."""
        skills_dir = anyio.Path(tmp_path) / "skills"
        await skills_dir.mkdir()
        skill_dir = skills_dir / "skill1"
        await skill_dir.mkdir()
        await (skill_dir / "README.md").write_text("Not a skill")

        result = await scan_skills_directory(skills_dir)

        assert result == {}


class TestScanSchedulesDirectory:
    """Tests for scan_schedules_directory function."""

    @pytest.mark.asyncio
    async def test_scan_empty_directory(self, tmp_path) -> None:
        """Test scanning empty directory."""
        schedules_dir = anyio.Path(tmp_path) / "schedules"
        await schedules_dir.mkdir()

        result = await scan_schedules_directory(schedules_dir)

        assert result == {}

    @pytest.mark.asyncio
    async def test_scan_finds_task_md_files(self, tmp_path) -> None:
        """Test that scan finds TASK.md files."""
        schedules_dir = anyio.Path(tmp_path) / "schedules"
        await schedules_dir.mkdir()
        task1_dir = schedules_dir / "task1"
        await task1_dir.mkdir()
        await (task1_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")
        task2_dir = schedules_dir / "task2"
        await task2_dir.mkdir()
        await (task2_dir / "TASK.md").write_text("---\ncron: '0 10 * * *'\n---\nContent")

        result = await scan_schedules_directory(schedules_dir)

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

    @pytest.mark.asyncio
    async def test_initialize_scans_all_directories(self, tmp_path) -> None:
        """Test that initialize scans all workspace directories."""
        workspace = anyio.Path(tmp_path)
        # Create workspace structure
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")

        skills_dir = workspace / "skills"
        await skills_dir.mkdir()
        skill_dir = skills_dir / "skill1"
        await skill_dir.mkdir()
        await (skill_dir / "SKILL.md").write_text("---\nname: skill1\n---\nContent")

        schedules_dir = workspace / "schedules"
        await schedules_dir.mkdir()
        task_dir = schedules_dir / "task1"
        await task_dir.mkdir()
        await (task_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        assert len(watcher.get_tool_hashes()) == 1
        assert len(watcher.get_skill_hashes()) == 1
        assert len(watcher.get_schedule_hashes()) == 1

    @pytest.mark.asyncio
    async def test_check_for_changes_detects_new_tool(self, tmp_path) -> None:
        """Test that check_for_changes detects new tool."""
        workspace = anyio.Path(tmp_path)
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # Add new tool
        await (tools_dir / "write.py").write_text("async def tool(): pass")

        changes = await watcher.check_for_changes()

        assert "write" in changes.tools_added
        assert changes.tools_changed

    @pytest.mark.asyncio
    async def test_check_for_changes_detects_modified_skill(self, tmp_path) -> None:
        """Test that check_for_changes detects modified skill."""
        workspace = anyio.Path(tmp_path)
        skills_dir = workspace / "skills"
        await skills_dir.mkdir()
        skill_dir = skills_dir / "skill1"
        await skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        await skill_md.write_text("---\nname: skill1\n---\nOriginal content")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # Modify skill
        await skill_md.write_text("---\nname: skill1\n---\nModified content")

        changes = await watcher.check_for_changes()

        assert "skill1" in changes.skills_modified
        assert changes.skills_changed

    @pytest.mark.asyncio
    async def test_check_for_changes_detects_removed_schedule(self, tmp_path) -> None:
        """Test that check_for_changes detects removed schedule."""
        workspace = anyio.Path(tmp_path)
        schedules_dir = workspace / "schedules"
        await schedules_dir.mkdir()
        task_dir = schedules_dir / "task1"
        await task_dir.mkdir()
        await (task_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # Remove schedule
        await (task_dir / "TASK.md").unlink()
        await task_dir.rmdir()

        changes = await watcher.check_for_changes()

        assert "task1" in changes.schedules_removed
        assert changes.schedules_changed

    @pytest.mark.asyncio
    async def test_check_for_changes_no_changes(self, tmp_path) -> None:
        """Test that check_for_changes returns empty when no changes."""
        workspace = anyio.Path(tmp_path)
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # No changes made
        changes = await watcher.check_for_changes()

        assert not changes.has_changes


class TestWorkspaceWatcherCompositeChanges:
    """Composite change tests for WorkspaceWatcher."""

    @pytest.mark.asyncio
    async def test_initialize_with_empty_workspace(self, tmp_path) -> None:
        """Initialize with empty workspace (no tools/skills/schedules dirs)."""
        workspace = anyio.Path(tmp_path)
        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        assert watcher.get_tool_hashes() == {}
        assert watcher.get_skill_hashes() == {}
        assert watcher.get_schedule_hashes() == {}

    @pytest.mark.asyncio
    async def test_simultaneous_add_modify_remove(self, tmp_path) -> None:
        """Simultaneous add+modify+remove across tools/skills/schedules."""
        workspace = anyio.Path(tmp_path)

        # Set up initial state
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "keep.py").write_text("v1")
        await (tools_dir / "modify.py").write_text("v1")

        skills_dir = workspace / "skills"
        await skills_dir.mkdir()
        skill_dir = skills_dir / "keep_skill"
        await skill_dir.mkdir()
        await (skill_dir / "SKILL.md").write_text("v1")

        schedules_dir = workspace / "schedules"
        await schedules_dir.mkdir()
        task_dir = schedules_dir / "keep_task"
        await task_dir.mkdir()
        await (task_dir / "TASK.md").write_text("v1")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # Add new tool, modify existing tool, remove another
        await (tools_dir / "new.py").write_text("v1")
        await (tools_dir / "modify.py").write_text("v2")
        await (tools_dir / "keep.py").unlink()

        # Add new skill, modify existing
        new_skill_dir = skills_dir / "new_skill"
        await new_skill_dir.mkdir()
        await (new_skill_dir / "SKILL.md").write_text("new")
        await (skill_dir / "SKILL.md").write_text("v2")

        # Add new schedule, remove existing
        new_task_dir = schedules_dir / "new_task"
        await new_task_dir.mkdir()
        await (new_task_dir / "TASK.md").write_text("new")
        await (task_dir / "TASK.md").unlink()
        await task_dir.rmdir()

        changes = await watcher.check_for_changes()

        assert "new" in changes.tools_added
        assert "keep" in changes.tools_removed
        assert "modify" in changes.tools_modified

        assert "new_skill" in changes.skills_added
        assert "keep_skill" in changes.skills_modified

        assert "new_task" in changes.schedules_added
        assert "keep_task" in changes.schedules_removed

    @pytest.mark.asyncio
    async def test_add_then_remove_same_tool_between_checks(self, tmp_path) -> None:
        """Add then immediately remove same tool between checks."""
        workspace = anyio.Path(tmp_path)
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # Add and remove before check
        tool_file = tools_dir / "ephemeral.py"
        await tool_file.write_text("v1")
        await tool_file.unlink()

        changes = await watcher.check_for_changes()
        assert not changes.has_changes

    @pytest.mark.asyncio
    async def test_modify_then_modify_again(self, tmp_path) -> None:
        """Modify then modify again (hash updates twice)."""
        workspace = anyio.Path(tmp_path)
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "tool.py").write_text("v1")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # First modification
        await (tools_dir / "tool.py").write_text("v2")
        changes1 = await watcher.check_for_changes()
        assert "tool" in changes1.tools_modified

        # Second modification
        await (tools_dir / "tool.py").write_text("v3")
        changes2 = await watcher.check_for_changes()
        assert "tool" in changes2.tools_modified


class TestWorkspaceWatcherIdempotency:
    """Idempotency tests for WorkspaceWatcher."""

    @pytest.mark.asyncio
    async def test_consecutive_checks_no_changes(self, tmp_path) -> None:
        """Consecutive check_for_changes with no changes returns empty summary."""
        workspace = anyio.Path(tmp_path)
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "tool.py").write_text("v1")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        changes1 = await watcher.check_for_changes()
        changes2 = await watcher.check_for_changes()

        assert not changes1.has_changes
        assert not changes2.has_changes

    @pytest.mark.asyncio
    async def test_check_updates_hashes_so_no_rereport(self, tmp_path) -> None:
        """check_for_changes updates internal hashes so subsequent check does not re-report."""
        workspace = anyio.Path(tmp_path)
        tools_dir = workspace / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "tool.py").write_text("v1")

        watcher = WorkspaceWatcher(workspace)
        await watcher.initialize()

        # Modify tool
        await (tools_dir / "tool.py").write_text("v2")
        changes1 = await watcher.check_for_changes()
        assert "tool" in changes1.tools_modified

        # Check again without further changes
        changes2 = await watcher.check_for_changes()
        assert not changes2.has_changes


class TestScanDirectoryEdgeCases:
    """Edge case tests for scan directories."""

    @pytest.mark.asyncio
    async def test_tools_dir_with_subdirectories(self, tmp_path) -> None:
        """Tools dir with subdirectories (should be ignored)."""
        tools_dir = anyio.Path(tmp_path) / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")
        sub_dir = tools_dir / "subdir"
        await sub_dir.mkdir()

        result = await scan_tools_directory(tools_dir)
        assert len(result) == 1
        assert "read" in result

    @pytest.mark.asyncio
    async def test_pycache_and_pyc_files_ignored(self, tmp_path) -> None:
        """__pycache__ and .pyc files are not .py so they're ignored."""
        tools_dir = anyio.Path(tmp_path) / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "read.py").write_text("async def tool(): pass")
        pycache = tools_dir / "__pycache__"
        await pycache.mkdir()
        await (pycache / "read.cpython-314.pyc").write_text("bytecode")

        result = await scan_tools_directory(tools_dir)
        assert len(result) == 1
        assert "read" in result

    @pytest.mark.asyncio
    async def test_init_py_as_tool(self, tmp_path) -> None:
        """__init__.py is a .py file so it would be scanned."""
        tools_dir = anyio.Path(tmp_path) / "tools"
        await tools_dir.mkdir()
        await (tools_dir / "__init__.py").write_text("")
        await (tools_dir / "read.py").write_text("async def tool(): pass")

        result = await scan_tools_directory(tools_dir)
        # __init__.py is a .py file, so it will be included
        assert "__init__" in result
        assert "read" in result

    @pytest.mark.asyncio
    async def test_skills_dir_with_special_characters(self, tmp_path) -> None:
        """Skills dir with special characters in name."""
        skills_dir = anyio.Path(tmp_path) / "skills"
        await skills_dir.mkdir()
        skill_dir = skills_dir / "my-skill_v2"
        await skill_dir.mkdir()
        await (skill_dir / "SKILL.md").write_text("---\nname: my-skill_v2\n---\nContent")

        result = await scan_skills_directory(skills_dir)
        assert "my-skill_v2" in result

    @pytest.mark.asyncio
    async def test_schedules_dir_with_non_directory_entries(self, tmp_path) -> None:
        """Schedules dir with non-directory entries (files should be ignored)."""
        schedules_dir = anyio.Path(tmp_path) / "schedules"
        await schedules_dir.mkdir()
        # Regular file in schedules dir (not a directory)
        await (schedules_dir / "README.md").write_text("Not a schedule")
        # Actual schedule
        task_dir = schedules_dir / "task1"
        await task_dir.mkdir()
        await (task_dir / "TASK.md").write_text("---\ncron: '0 9 * * *'\n---\nContent")

        result = await scan_schedules_directory(schedules_dir)
        assert len(result) == 1
        assert "task1" in result
