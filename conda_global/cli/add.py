"""Handler for ``conda global add``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ..envs import EnvironmentManager
from ..exceptions import ToolNotFoundError
from ..manifest import Manifest
from . import status

if TYPE_CHECKING:
    import argparse


def execute_add(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Add a dependency to an existing tool environment."""
    console = console or Console(highlight=False)
    package = args.package
    env_name = args.environment

    manifest = Manifest()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]

    status.message(
        console,
        "Adding",
        "package",
        package,
        style="bold blue",
        detail=f"to {env_name}",
    )

    tool.dependencies[package] = "*"
    EnvironmentManager().create(env_name, tool.specs, tool.channels)
    manifest.add(tool)

    status.message(
        console,
        "Added",
        "package",
        package,
        detail=f"to {env_name}",
    )
    return 0
