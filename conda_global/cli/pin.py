"""Handlers for ``conda global pin`` and ``conda global unpin``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ..exceptions import ToolNotFoundError
from ..manifest import Manifest
from . import status

if TYPE_CHECKING:
    import argparse


def execute_pin(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Prevent a tool from being upgraded."""
    console = console or Console(highlight=False)
    env_name = args.environment

    manifest = Manifest()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]
    tool.pinned = True
    manifest.add(tool)

    status.message(console, "Pinned", "tool", env_name)
    return 0


def execute_unpin(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Allow upgrades for a tool."""
    console = console or Console(highlight=False)
    env_name = args.environment

    manifest = Manifest()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]
    tool.pinned = False
    manifest.add(tool)

    status.message(console, "Unpinned", "tool", env_name)
    return 0
