"""Find binaries in tool environments."""

from __future__ import annotations

import stat
from typing import TYPE_CHECKING

from conda.base.constants import on_win

if TYPE_CHECKING:
    from pathlib import Path


def discover_binaries(prefix: Path) -> list[str]:
    """Return a list of executable binary names in a conda prefix.

    Looks in ``bin/`` on Unix or ``Scripts/`` on Windows.
    """
    bin_dir = prefix / ("Scripts" if on_win else "bin")
    if not bin_dir.is_dir():
        return []

    binaries = []
    for entry in sorted(bin_dir.iterdir()):
        if not entry.is_file():
            continue
        if on_win:
            if entry.suffix.lower() in (".exe", ".bat", ".cmd"):
                binaries.append(entry.stem)
        else:
            if _is_executable(entry):
                binaries.append(entry.name)
    return binaries


def _is_executable(path: Path) -> bool:
    """Check if a file has the executable bit set."""
    return bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def find_binary(prefix: Path, name: str) -> Path | None:
    """Find a specific binary by name in a conda prefix."""
    bin_dir = prefix / ("Scripts" if on_win else "bin")
    if not bin_dir.is_dir():
        return None

    if on_win:
        for ext in (".exe", ".bat", ".cmd", ""):
            candidate = bin_dir / f"{name}{ext}"
            if candidate.is_file():
                return candidate
    else:
        candidate = bin_dir / name
        if candidate.is_file():
            return candidate

    return None
