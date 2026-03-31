"""Tests for ``conda global tree``."""

from __future__ import annotations

import argparse
import json

import pytest

from conda_global.cli.tree import execute_tree
from conda_global.exceptions import ToolNotFoundError


def test_tree_shows_packages(
    mock_conda_home,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh")

    env_dir = mock_conda_home / "envs" / "gh"
    conda_meta = env_dir / "conda-meta"
    conda_meta.mkdir(parents=True)

    (conda_meta / "gh-2.40.0-0.json").write_text(
        json.dumps(
            {
                "name": "gh",
                "version": "2.40.0",
                "build": "0",
                "build_number": 0,
                "channel": "https://conda.anaconda.org/conda-forge",
                "depends": ["openssl >=3.0", "libcurl >=8.0"],
            }
        )
    )
    (conda_meta / "openssl-3.2.0-0.json").write_text(
        json.dumps(
            {
                "name": "openssl",
                "version": "3.2.0",
                "build": "0",
                "build_number": 0,
                "channel": "https://conda.anaconda.org/conda-forge",
                "depends": [],
            }
        )
    )

    args = argparse.Namespace(environment="gh")
    result = execute_tree(args, console=rich_console)
    assert result == 0

    output = rich_console.file.getvalue()
    assert "gh" in output
    assert "2.40.0" in output
    assert "openssl" in output
    assert "libcurl" in output


def test_tree_no_conda_meta(
    mock_conda_home,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh")

    env_dir = mock_conda_home / "envs" / "gh"
    env_dir.mkdir(parents=True)

    args = argparse.Namespace(environment="gh")
    result = execute_tree(args, console=rich_console)
    assert result == 0
    assert "No packages installed" in rich_console.file.getvalue()


def test_tree_nonexistent_tool(mock_conda_home, rich_console):
    args = argparse.Namespace(environment="nonexistent")
    with pytest.raises(ToolNotFoundError):
        execute_tree(args, console=rich_console)
