"""Conda plugin hooks for conda-global."""

from __future__ import annotations

from conda.plugins import CondaSubcommand, hookimpl


@hookimpl
def conda_subcommands():
    from .cli.main import execute, generate_parser

    yield CondaSubcommand(
        name="global",
        summary="Install and manage globally available CLI tools.",
        action=execute,
        configure_parser=generate_parser,
    )
