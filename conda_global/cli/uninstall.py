"""Handler for ``conda global uninstall``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ..envs import EnvironmentManager
from ..exceptions import ToolNotFoundError
from ..manifest import Manifest
from ..trampolines import TrampolineManager
from . import status

if TYPE_CHECKING:
    import argparse


def execute_uninstall(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Remove a tool and its environment."""
    console = console or Console(highlight=False)
    env_name = args.environment

    manifest = Manifest()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    status.message(
        console,
        "Uninstalling",
        "tool",
        env_name,
        style="bold blue",
        ellipsis=True,
    )

    tool = tools[env_name]
    trampolines = TrampolineManager()
    for exposed_name in tool.exposed:
        trampolines.remove(exposed_name)

    EnvironmentManager().remove(env_name)
    manifest.remove(env_name)

    status.message(console, "Uninstalled", "tool", env_name)
    return 0
