"""Handler for ``conda global list``."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from ..manifest import Manifest

if TYPE_CHECKING:
    import argparse


def execute_list(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """List installed tools."""
    console = console or Console(highlight=False)
    tools = Manifest().load()

    if not tools:
        console.print(
            "No tools installed. Use [bold]conda global install <pkg>[/bold] to get started."
        )
        return 0

    if args.json:
        data = {
            name: {
                "channels": tool.channels,
                "dependencies": tool.dependencies,
                "exposed": tool.exposed,
                "pinned": tool.pinned,
            }
            for name, tool in tools.items()
        }
        console.print_json(json.dumps(data))
        return 0

    table = Table(show_edge=False, pad_edge=False)
    table.add_column("Tool", style="bold")
    table.add_column("Dependencies")
    table.add_column("Channel")
    table.add_column("Exposed")
    table.add_column("Pinned")

    for name in sorted(tools):
        tool = tools[name]
        deps = ", ".join(
            f"{pkg}{ver}" if ver != "*" else pkg for pkg, ver in tool.dependencies.items()
        )
        channels = ", ".join(tool.channels)
        exposed = ", ".join(sorted(tool.exposed.keys())) if tool.exposed else "[dim]-[/dim]"
        pinned = "[dim]yes[/dim]" if tool.pinned else ""
        table.add_row(name, deps, channels, exposed, pinned)

    console.print(table)
    return 0
