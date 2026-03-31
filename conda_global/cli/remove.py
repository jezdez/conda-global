"""Handler for ``conda global remove``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ..envs import EnvironmentManager
from ..exceptions import ToolNotFoundError
from ..manifest import Manifest
from . import status

if TYPE_CHECKING:
    import argparse


def execute_remove(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Remove a dependency from a tool environment."""
    console = console or Console(highlight=False)
    package = args.package
    env_name = args.environment

    manifest = Manifest()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]
    if package not in tool.dependencies:
        console.print(
            f"Package [bold]{package}[/bold] is not in environment [bold]{env_name}[/bold]"
        )
        return 1

    status.message(
        console,
        "Removing",
        "package",
        package,
        style="bold blue",
        detail=f"from {env_name}",
    )

    del tool.dependencies[package]
    EnvironmentManager().create(env_name, tool.specs, tool.channels)
    manifest.add(tool)

    status.message(
        console,
        "Removed",
        "package",
        package,
        detail=f"from {env_name}",
    )
    return 0
