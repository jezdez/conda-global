"""Tests for path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from conda_global import paths


@pytest.mark.parametrize(
    "func,expected_suffix",
    [
        (paths.global_envs_dir, "envs"),
        (paths.global_bin_dir, "bin"),
        (paths.trampoline_config_dir, "bin/trampoline"),
        (paths.trampoline_master_path, "bin/trampoline/_cg_trampoline"),
        (paths.manifest_path, "global.toml"),
    ],
)
def test_path_helpers(func, expected_suffix, monkeypatch, tmp_path):
    data = tmp_path / ".cg"
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    assert func() == data / expected_suffix


def test_data_dir_default():
    assert paths.data_dir() == Path.home() / ".cg"


def test_data_dir_respects_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("CONDA_GLOBAL_HOME", str(tmp_path / "custom"))
    assert paths.data_dir() == tmp_path / "custom"
    assert paths.global_envs_dir() == tmp_path / "custom" / "envs"
    assert paths.manifest_path() == tmp_path / "custom" / "global.toml"


@pytest.mark.parametrize(
    "env_value,expected",
    [
        pytest.param("~/my-conda", Path.home() / "my-conda", id="tilde-expansion"),
        pytest.param("", Path.home() / ".cg", id="empty-ignored"),
    ],
)
def test_data_dir_env_var_edge_cases(monkeypatch, env_value, expected):
    monkeypatch.setenv("CONDA_GLOBAL_HOME", env_value)
    assert paths.data_dir() == expected
