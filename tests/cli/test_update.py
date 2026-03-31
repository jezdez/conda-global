"""Tests for ``conda global update``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.update import execute_update
from conda_global.exceptions import ToolNotFoundError


def test_update_single_tool(
    mock_conda_home,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh")

    args = argparse.Namespace(environment="gh")
    result = execute_update(args, console=rich_console)
    assert result == 0

    output = rich_console.file.getvalue()
    assert "Updating" in output
    assert "Updated" in output

    assert len(fake_envs_create) == 1
    assert fake_envs_create[0]["name"] == "gh"


def test_update_all_tools(
    mock_conda_home,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh")
    seeded_manifest("ruff")

    args = argparse.Namespace(environment=None)
    result = execute_update(args, console=rich_console)
    assert result == 0

    assert len(fake_envs_create) == 2
    updated_names = {c["name"] for c in fake_envs_create}
    assert updated_names == {"gh", "ruff"}


def test_update_skips_pinned(
    mock_conda_home,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh", pinned=True)
    seeded_manifest("ruff")

    args = argparse.Namespace(environment=None)
    result = execute_update(args, console=rich_console)
    assert result == 0

    assert len(fake_envs_create) == 1
    assert fake_envs_create[0]["name"] == "ruff"

    output = rich_console.file.getvalue()
    assert "Skipped" in output
    assert "pinned" in output


def test_update_nonexistent_tool(mock_conda_home, rich_console):
    args = argparse.Namespace(environment="nonexistent")
    with pytest.raises(ToolNotFoundError):
        execute_update(args, console=rich_console)


def test_update_empty_manifest(mock_conda_home, rich_console):
    args = argparse.Namespace(environment=None)
    result = execute_update(args, console=rich_console)
    assert result == 0
