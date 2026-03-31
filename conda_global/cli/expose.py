"""Handlers for ``conda global expose`` and ``conda global hide``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ..binaries import find_binary
from ..envs import EnvironmentManager
from ..exceptions import BinaryNotFoundError, ToolNotFoundError
from ..manifest import Manifest
from ..trampolines import TrampolineManager
from . import status

if TYPE_CHECKING:
    import argparse


def execute_expose(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Make a binary from an env available on PATH."""
    console = console or Console(highlight=False)
    env_name = args.environment
    mapping = args.mapping

    if "=" in mapping:
        exposed_name, binary_name = mapping.split("=", 1)
    else:
        exposed_name = binary_name = mapping

    manifest = Manifest()
    envs = EnvironmentManager()
    trampolines = TrampolineManager()

    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]
    prefix = tool.prefix_path(envs.envs_dir)
    binary_path = find_binary(prefix, binary_name)
    if binary_path is None:
        raise BinaryNotFoundError(binary_name, env_name)

    bin_dir = tool.bin_path(envs.envs_dir)
    trampolines.deploy(
        exposed_name=exposed_name,
        exe_path=binary_path,
        path_diff=str(bin_dir),
    )

    tool.exposed[exposed_name] = binary_name
    manifest.add(tool)

    status.message(
        console,
        "Exposed",
        "binary",
        exposed_name,
        detail=f"from {env_name}",
    )
    return 0


def execute_hide(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Remove an exposed binary from PATH."""
    console = console or Console(highlight=False)
    env_name = args.environment
    name = args.name

    manifest = Manifest()
    trampolines = TrampolineManager()

    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]
    trampolines.remove(name)

    tool.exposed.pop(name, None)
    manifest.add(tool)

    status.message(console, "Hidden", "binary", name, detail=f"from {env_name}")
    return 0
