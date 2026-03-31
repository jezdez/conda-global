"""Handler for ``conda global tree``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda.core.prefix_data import PrefixData
from rich.console import Console
from rich.tree import Tree

from ..envs import EnvironmentManager
from ..exceptions import ToolNotFoundError
from ..manifest import Manifest

if TYPE_CHECKING:
    import argparse


def execute_tree(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Show dependency tree for a tool environment."""
    console = console or Console(highlight=False)
    env_name = args.environment

    manifest = Manifest()
    envs = EnvironmentManager()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    tool = tools[env_name]
    prefix = tool.prefix_path(envs.envs_dir)

    pd = PrefixData(str(prefix))
    records = sorted(pd.iter_records(), key=lambda r: r.name)

    if not records:
        console.print(f"No packages installed in [bold]{env_name}[/bold]")
        return 0

    tree = Tree(f"[bold]{env_name}[/bold]")

    for rec in records:
        label = f"[bold]{rec.name}[/bold] {rec.version}"
        if rec.channel:
            label += f"  [dim]({rec.channel.name})[/dim]"

        pkg_node = tree.add(label)

        for dep in rec.depends:
            pkg_node.add(f"[dim]{dep}[/dim]")

    console.print(tree)
    return 0
