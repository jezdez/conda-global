"""Tests for trampoline deployment."""

from __future__ import annotations

import json

import pytest
from conda_trampoline import TrampolineManager


@pytest.fixture
def trampolines(tmp_path):
    """Set up a TrampolineManager with a fake master binary."""
    bin_dir = tmp_path / "bin"
    mgr = TrampolineManager(bin_dir)
    mgr.bin_dir.mkdir()
    mgr.config_dir.mkdir()
    mgr.master_path.write_bytes(b"fake trampoline binary")
    return mgr


@pytest.mark.parametrize(
    "name,env,expected_env",
    [
        pytest.param("gh", None, {}, id="no-env-vars"),
        pytest.param("tool", {"CUSTOM_VAR": "value"}, {"CUSTOM_VAR": "value"}, id="with-env-vars"),
    ],
)
def test_deploy_creates_hardlink_and_config(trampolines, name, env, expected_env):
    kwargs = {
        "exposed_name": name,
        "exe_path": trampolines.bin_dir.parent / "envs" / name / "bin" / name,
        "path_diff": f"/{name}/bin",
    }
    if env is not None:
        kwargs["env"] = env
    trampolines.deploy(**kwargs)

    assert (trampolines.bin_dir / name).exists()

    config = json.loads((trampolines.config_dir / f"{name}.json").read_text())
    assert config["env"] == expected_env


def test_remove(trampolines):
    trampolines.deploy(
        exposed_name="gh",
        exe_path=trampolines.bin_dir.parent / "envs" / "gh" / "bin" / "gh",
        path_diff="/some/path",
    )
    assert (trampolines.bin_dir / "gh").exists()
    assert (trampolines.config_dir / "gh.json").exists()

    trampolines.remove("gh")

    assert not (trampolines.bin_dir / "gh").exists()
    assert not (trampolines.config_dir / "gh.json").exists()


def test_remove_nonexistent(trampolines):
    trampolines.remove("nonexistent")


def test_deploy_multiple(trampolines):
    for name in ("gh", "ruff", "bat"):
        trampolines.deploy(
            exposed_name=name,
            exe_path=trampolines.bin_dir.parent / "envs" / name / "bin" / name,
            path_diff=f"/path/{name}",
        )

    for name in ("gh", "ruff", "bat"):
        assert (trampolines.bin_dir / name).exists()

    assert len(list(trampolines.config_dir.glob("*.json"))) == 3


def test_deploy_idempotent(trampolines):
    trampolines.deploy(
        exposed_name="gh",
        exe_path=trampolines.bin_dir.parent / "envs" / "gh" / "bin" / "gh",
        path_diff="/some/path",
    )
    trampolines.deploy(
        exposed_name="gh",
        exe_path=trampolines.bin_dir.parent / "envs" / "gh" / "bin" / "gh",
        path_diff="/updated/path",
    )

    config = json.loads((trampolines.config_dir / "gh.json").read_text())
    assert config["path_diff"] == "/updated/path"
