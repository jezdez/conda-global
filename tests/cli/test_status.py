"""Tests for CLI status helpers."""

from __future__ import annotations

import pytest

from conda_global.cli.status import message, print_error


@pytest.mark.parametrize(
    "kwargs,expected_strings",
    [
        pytest.param(
            {"verb": "Installed", "noun": "tool", "name": "gh"},
            ["Installed", "gh", "tool"],
            id="basic",
        ),
        pytest.param(
            {"verb": "Installing", "noun": "tool", "name": "gh", "ellipsis": True},
            ["Installing", "..."],
            id="ellipsis",
        ),
        pytest.param(
            {"verb": "Added", "noun": "package", "name": "numpy", "detail": "to ruff"},
            ["Added", "numpy", "to ruff"],
            id="detail",
        ),
        pytest.param(
            {"verb": "Skipped", "noun": "tool", "name": "gh", "suffix": "pinned"},
            ["Skipped", "pinned"],
            id="suffix",
        ),
    ],
)
def test_message(rich_console, kwargs, expected_strings):
    message(rich_console, **kwargs)
    output = rich_console.file.getvalue()
    for s in expected_strings:
        assert s in output


def test_print_error_simple(rich_console):
    print_error(rich_console, Exception("something went wrong"))
    output = rich_console.file.getvalue()
    assert "Error:" in output
    assert "something went wrong" in output


def test_print_error_with_hints(rich_console):

    class FakeError(Exception):
        error_message = "tool not found"
        hints = ["try: conda global list"]

    print_error(rich_console, FakeError())
    output = rich_console.file.getvalue()
    assert "Error:" in output
    assert "tool not found" in output
    assert "Hint:" in output
    assert "conda global list" in output


def test_print_error_escapes_markup(rich_console):

    class FakeError(Exception):
        error_message = "bad [bold]markup[/bold] in error"
        hints: list[str] = []

    print_error(rich_console, FakeError())
    output = rich_console.file.getvalue()
    assert "[bold]" in output or "markup" in output
