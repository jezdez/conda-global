"""Shared status helpers for CLI output.

Provides verb-based status messages that are accessible and
colorblind-safe.  Every state is distinguishable by word alone;
color is supplementary, using blue/cyan/yellow instead of green/red.

Example output::

    Installing gh tool...
    Installed gh tool

    Uninstalling gh tool...
    Uninstalled gh tool

    Exposing ruff-format from ruff tool
    Hidden ruff-format from ruff tool

Error output::

    Error: tool environment 'foo' not found.
    Hint: available tools: gh, ruff, bat
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rich.markup import escape as _escape

if TYPE_CHECKING:
    from rich.console import Console


def _format(
    verb: str,
    noun: str,
    name: str,
    *,
    style: str = "",
    ellipsis: bool = False,
    detail: str | None = None,
    suffix: str | None = None,
) -> str:
    """Build a Rich markup status line.

    *verb* is the action word (``Installing``, ``Installed``, ...),
    *noun* is the object type (``tool``, ``binary``),
    *name* is the specific item.
    """
    if style:
        text = f"[{style}]{verb}[/{style}]"
    else:
        text = verb
    text += f" [bold]{_escape(name)}[/bold] {noun}"
    if ellipsis:
        text += "[dim]...[/dim]"
    if detail:
        text += f"  [dim]{_escape(detail)}[/dim]"
    if suffix:
        text += f" [dim]({suffix})[/dim]"
    return text


def message(
    console: Console,
    verb: str,
    noun: str,
    name: str,
    *,
    style: str = "bold cyan",
    ellipsis: bool = False,
    detail: str | None = None,
    suffix: str | None = None,
) -> None:
    """Print a verb-based status line.

    Examples::

        status.message(console, "Installing", "tool", "gh",
                       style="bold blue", ellipsis=True)
        # -> Installing gh tool...

        status.message(console, "Installed", "tool", "gh")
        # -> Installed gh tool
    """
    console.print(
        _format(
            verb,
            noun,
            name,
            style=style,
            ellipsis=ellipsis,
            detail=detail,
            suffix=suffix,
        )
    )


def message_label(
    verb: str,
    noun: str,
    name: str,
    *,
    style: str = "bold yellow",
    detail: str | None = None,
) -> str:
    """Build a status label string for Rich Tree nodes."""
    return _format(verb, noun, name, style=style, detail=detail)


def _class_name_to_label(cls_name: str) -> str:
    """Derive a readable label from a CamelCase exception class name."""
    name = cls_name.removesuffix("Error")
    words = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", name)
    words = re.sub(r"([a-z])([A-Z])", r"\1 \2", words)
    return " ".join(w if w.isupper() and len(w) > 1 else w.lower() for w in words.split())


def _format_error_message(exc: Exception) -> str:
    """Extract a human-readable error message from an exception."""
    error_message = getattr(exc, "error_message", None)
    if error_message:
        return error_message
    label = _class_name_to_label(type(exc).__name__)
    detail = str(exc)
    return f"{label}: {detail}" if detail else label


def print_error(
    console: Console,
    exc: Exception,
) -> None:
    """Render a structured error with optional hints.

    Example::

        Error: tool environment 'foo' not found.
        Hint: available tools: gh, ruff, bat
    """
    inner_errors = getattr(exc, "errors", None)
    if inner_errors:
        seen: set[str] = set()
        for inner in inner_errors:
            msg = _format_error_message(inner)
            if msg not in seen:
                seen.add(msg)
                console.print(f"[bold red]Error:[/bold red] {_escape(msg)}")
                for hint in getattr(inner, "hints", []):
                    console.print(f"[bold cyan]Hint:[/bold cyan] {_escape(hint)}")
    else:
        msg = _format_error_message(exc)
        console.print(f"[bold red]Error:[/bold red] {_escape(msg)}")
        for hint in getattr(exc, "hints", []):
            console.print(f"[bold cyan]Hint:[/bold cyan] {_escape(hint)}")
