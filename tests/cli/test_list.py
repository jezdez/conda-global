"""Tests for ``conda global list``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.list import execute_list


def test_list_empty(mock_conda_home, rich_console):
    args = argparse.Namespace(json=False)
    result = execute_list(args, console=rich_console)
    assert result == 0
    assert "No tools installed" in rich_console.file.getvalue()


@pytest.mark.parametrize("json_flag", [False, True], ids=["table", "json"])
def test_list_with_tools(mock_conda_home, seeded_manifest, rich_console, json_flag):
    seeded_manifest(
        "gh",
        dependencies={"gh": "*"},
        exposed={"gh": "gh"},
        channels=["conda-forge"],
    )

    args = argparse.Namespace(json=json_flag)
    result = execute_list(args, console=rich_console)
    assert result == 0
    output = rich_console.file.getvalue()
    assert "gh" in output
    assert "conda-forge" in output


def test_list_multiple_tools(mock_conda_home, seeded_manifest, rich_console):
    for name in ("gh", "ruff", "bat"):
        seeded_manifest(name, dependencies={name: "*"}, exposed={name: name})

    args = argparse.Namespace(json=False)
    result = execute_list(args, console=rich_console)
    assert result == 0
    output = rich_console.file.getvalue()
    for name in ("gh", "ruff", "bat"):
        assert name in output
