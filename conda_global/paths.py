"""Path helpers for conda-global filesystem layout."""

from __future__ import annotations

import os
from pathlib import Path


def data_dir() -> Path:
    """Return the base data directory for conda-global (``~/.cg/``).

    Respects the ``CONDA_GLOBAL_HOME`` environment variable.
    Falls back to ``~/.cg/``.
    """
    env = os.environ.get("CONDA_GLOBAL_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".cg"


def global_envs_dir() -> Path:
    """Return the directory for tool environments."""
    return data_dir() / "envs"


def global_bin_dir() -> Path:
    """Return the directory for trampoline binaries."""
    return data_dir() / "bin"


def trampoline_config_dir() -> Path:
    """Return the directory for trampoline configs."""
    return global_bin_dir() / "trampoline"


def trampoline_master_path() -> Path:
    """Return the path to the master trampoline binary."""
    return trampoline_config_dir() / "_cg_trampoline"


def manifest_path() -> Path:
    """Return the path to the global manifest."""
    return data_dir() / "global.toml"
