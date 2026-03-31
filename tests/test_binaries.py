"""Tests for binary discovery."""

from __future__ import annotations

import stat

import pytest

from conda_global.binaries import discover_binaries, find_binary


@pytest.fixture
def unix_prefix(tmp_path, monkeypatch):
    """Create a fake Unix-style prefix with bin/ directory."""
    monkeypatch.setattr("conda_global.binaries.on_win", False)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    return tmp_path


def _make_executable(path):
    """Make a file executable."""
    path.write_bytes(b"#!/bin/sh\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_discover_binaries_empty_prefix(unix_prefix):
    result = discover_binaries(unix_prefix)
    assert result == []


def test_discover_binaries_unix(unix_prefix):
    bin_dir = unix_prefix / "bin"
    _make_executable(bin_dir / "gh")
    _make_executable(bin_dir / "ruff")
    (bin_dir / "not_executable").write_text("data")

    result = discover_binaries(unix_prefix)
    assert "gh" in result
    assert "ruff" in result
    assert "not_executable" not in result


def test_discover_binaries_no_bin_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.binaries.on_win", False)
    result = discover_binaries(tmp_path)
    assert result == []


@pytest.mark.parametrize(
    "name,create,expected_found",
    [
        pytest.param("gh", True, True, id="found"),
        pytest.param("nonexistent", False, False, id="not-found"),
    ],
)
def test_find_binary(unix_prefix, name, create, expected_found):
    if create:
        _make_executable(unix_prefix / "bin" / name)
    result = find_binary(unix_prefix, name)
    if expected_found:
        assert result is not None
        assert result.name == name
    else:
        assert result is None
