"""Tests for environment management."""

from __future__ import annotations

import pytest

from conda_global.envs import EnvironmentManager


@pytest.mark.parametrize(
    "setup,expected",
    [
        pytest.param(None, False, id="dir-missing"),
        pytest.param("dir-only", False, id="dir-no-conda-meta"),
        pytest.param("with-conda-meta", True, id="dir-with-conda-meta"),
    ],
)
def test_exists(tmp_path, setup, expected):
    if setup == "dir-only":
        (tmp_path / "gh").mkdir()
    elif setup == "with-conda-meta":
        (tmp_path / "gh").mkdir()
        (tmp_path / "gh" / "conda-meta").mkdir()

    assert EnvironmentManager(tmp_path).exists("gh") is expected


def test_remove(tmp_path):
    env_dir = tmp_path / "gh"
    env_dir.mkdir()
    (env_dir / "conda-meta").mkdir()
    (env_dir / "conda-meta" / "history").write_text("test")

    envs = EnvironmentManager(tmp_path)
    assert envs.exists("gh")

    envs.remove("gh")
    assert not env_dir.exists()


def test_remove_nonexistent(tmp_path):
    EnvironmentManager(tmp_path).remove("nonexistent")
