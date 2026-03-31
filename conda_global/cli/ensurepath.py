"""Handler for ``conda global ensurepath``."""

from __future__ import annotations

from typing import TYPE_CHECKING

import userpath
from rich.console import Console

from ..paths import global_bin_dir

if TYPE_CHECKING:
    import argparse


def execute_ensurepath(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Add the global binary directory to PATH.

    Uses the ``userpath`` library for cross-platform shell config
    management (bash, zsh, fish, PowerShell, Windows registry).
    """
    console = console or Console(highlight=False)
    location = str(global_bin_dir())

    if userpath.in_current_path(location):
        console.print(f"[bold]{location}[/bold] is already on your PATH.")
        return 0

    if userpath.need_shell_restart(location):
        console.print(f"[bold]{location}[/bold] is already configured in your shell.")
        console.print("Restart your shell or open a new terminal for the change to take effect.")
        return 0

    if userpath.append(location, "conda-global"):
        console.print(f"Added [bold]{location}[/bold] to your PATH.")
        console.print("Restart your shell or open a new terminal for the change to take effect.")
        return 0

    console.print(
        f"[bold red]Error:[/bold red] could not add {location} to PATH. "
        "You may need to add it manually."
    )
    return 1
