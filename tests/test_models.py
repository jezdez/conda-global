"""Tests for data models."""

from __future__ import annotations

import pytest

from conda_global.models import ExposedBinary, ToolEnv


def test_tool_env_defaults():
    tool = ToolEnv(name="gh")
    assert tool.channels == ["conda-forge"]
    assert tool.dependencies == {}
    assert tool.exposed == {}
    assert tool.pinned is False


def test_tool_env_custom():
    tool = ToolEnv(
        name="ruff",
        channels=["conda-forge", "defaults"],
        dependencies={"ruff": ">=0.4"},
        exposed={"ruff": "ruff"},
        pinned=True,
    )
    assert tool.name == "ruff"
    assert tool.pinned is True
    assert tool.dependencies == {"ruff": ">=0.4"}


def test_exposed_binary():
    eb = ExposedBinary(
        exposed_name="gh",
        binary_name="gh",
        env_name="gh",
    )
    assert eb.exposed_name == "gh"
    assert eb.binary_name == "gh"
    assert eb.env_name == "gh"


@pytest.mark.parametrize(
    "deps,expected",
    [
        ({}, []),
        ({"gh": "*"}, ["gh"]),
        ({"ruff": ">=0.4"}, ["ruff>=0.4"]),
        ({"numpy": ">=1.20", "scipy": "*"}, ["numpy>=1.20", "scipy"]),
    ],
)
def test_specs(deps, expected):
    tool = ToolEnv(name="test", dependencies=deps)
    assert tool.specs == expected


def test_prefix_path(tmp_path):
    tool = ToolEnv(name="gh")
    assert tool.prefix_path(tmp_path) == tmp_path / "gh"
