"""Handler for ``conda global update``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ..envs import EnvironmentManager
from ..exceptions import ToolNotFoundError
from ..manifest import Manifest
from . import status

if TYPE_CHECKING:
    import argparse

    from ..models import ToolEnv


def execute_update(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Update one or all tools."""
    console = console or Console(highlight=False)
    env_name = args.environment

    manifest = Manifest()
    envs = EnvironmentManager()
    tools = manifest.load()

    if env_name:
        if env_name not in tools:
            raise ToolNotFoundError(env_name, list(tools.keys()))
        _update_tool(console, envs, tools[env_name])
    else:
        for tool in tools.values():
            if tool.pinned:
                status.message(
                    console,
                    "Skipped",
                    "tool",
                    tool.name,
                    suffix="pinned",
                )
                continue
            _update_tool(console, envs, tool)

    return 0


def _update_tool(console: Console, envs: EnvironmentManager, tool: ToolEnv) -> None:
    """Update a single tool environment."""
    status.message(
        console,
        "Updating",
        "tool",
        tool.name,
        style="bold blue",
        ellipsis=True,
    )
    envs.create(tool.name, tool.specs, tool.channels)
    status.message(console, "Updated", "tool", tool.name)
