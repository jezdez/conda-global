"""Handler for ``conda global sync``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda_trampoline import TrampolineManager
from rich.console import Console

from ..binaries import find_binary
from ..envs import EnvironmentManager
from ..manifest import Manifest
from ..paths import global_bin_dir
from . import status

if TYPE_CHECKING:
    import argparse


def execute_sync(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Reconcile filesystem with manifest."""
    console = console or Console(highlight=False)

    manifest = Manifest()
    envs = EnvironmentManager()
    trampolines = TrampolineManager(global_bin_dir())
    tools = manifest.load()

    if not tools:
        console.print("No tools defined in manifest. Nothing to sync.")
        return 0

    console.print("[bold]Syncing global tools...[/bold]")
    count = 0

    for name, tool in sorted(tools.items()):
        if not envs.exists(name):
            status.message(
                console,
                "  Installing",
                "tool",
                name,
                style="bold blue",
            )
            prefix = envs.create(name, tool.specs, tool.channels)
        else:
            prefix = tool.prefix_path(envs.envs_dir)

        bin_dir = tool.bin_path(envs.envs_dir)
        for exposed_name, binary_name in tool.exposed.items():
            binary_path = find_binary(prefix, binary_name)
            if binary_path:
                trampolines.deploy(
                    exposed_name=exposed_name,
                    exe_path=binary_path,
                    path_diff=str(bin_dir),
                )
        count += 1

    console.print(f"[bold]Synced {count} tool{'s' if count != 1 else ''}[/bold]")
    return 0
