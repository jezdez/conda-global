"""Data models for conda-global."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from conda.base.constants import on_win

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ExposedBinary:
    """A binary exposed on PATH via a trampoline."""

    exposed_name: str
    binary_name: str
    env_name: str


@dataclass
class ToolEnv:
    """A globally installed tool environment."""

    name: str
    channels: list[str] = field(default_factory=lambda: ["conda-forge"])
    dependencies: dict[str, str] = field(default_factory=dict)
    exposed: dict[str, str] = field(default_factory=dict)
    pinned: bool = False

    @property
    def specs(self) -> list[str]:
        """Return dependency specs suitable for passing to the solver."""
        return [f"{name}{ver}" if ver != "*" else name for name, ver in self.dependencies.items()]

    def prefix_path(self, envs_dir: Path) -> Path:
        """Return the conda prefix path for this tool within *envs_dir*."""
        return envs_dir / self.name

    def bin_path(self, envs_dir: Path) -> Path:
        """Return the platform-correct binary directory within the prefix."""
        return self.prefix_path(envs_dir) / ("Scripts" if on_win else "bin")
