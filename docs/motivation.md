# Motivation

## The problem

Command-line tools often need their own dependencies. Installing them
into a shared environment (like `base`) leads to conflicts: upgrading
one tool can break another.

The solution is isolation — each tool in its own environment. But then
you need activation, PATH management, and a way to remember what you
installed. That overhead is why tools like pipx exist.

## Prior art

### pipx

[pipx](https://pipx.pypa.io/) pioneered the "isolated tool
environments" pattern for Python. It creates a virtualenv per tool
and places wrapper scripts on PATH. It works well, but:

- Only installs from PyPI — you can't install non-Python tools like
  `gh`, `bat`, or `fd`
- Uses Python wrapper scripts that add interpreter startup time
- No manifest file for syncing across machines

### pixi global

[pixi global](https://pixi.sh/latest/reference/cli/#global) brings
the same pattern to the pixi ecosystem. It installs tools from conda
channels into isolated environments. However:

- Requires pixi as the package manager — you can't use conda's
  solver, channels configuration, or existing infrastructure
- Uses its own environment format and manifest location
- Does not integrate with the conda CLI

## How conda-global fits in

conda-global brings isolated tool management into conda itself:

| | pipx | pixi global | conda-global |
|---|---|---|---|
| Package source | PyPI | conda channels | conda channels |
| Isolation | virtualenvs | pixi envs | conda envs |
| Launcher | Python scripts | shell scripts | Rust trampolines |
| Startup overhead | ~50ms | ~10ms | <1ms |
| Manifest | none | `~/.pixi/manifests/pixi-global.toml` | `global.toml` |
| CLI integration | standalone | pixi CLI | `conda global` + `cg` alias |
| Non-Python tools | no | yes | yes |
| Cross-machine sync | no | yes | yes |

## Design choices

Rust trampolines over wrapper scripts
: Wrapper scripts add measurable startup latency (Python: ~50ms,
  shell: ~10ms). A compiled trampoline that calls `execvp` adds
  negligible overhead and replaces the process entirely on Unix.

Hardlinks over copies
: All trampolines are hardlinks to a single master binary. This
  keeps disk usage flat regardless of how many tools are exposed.

Manifest-first approach
: The `global.toml` manifest is the source of truth. You can edit it
  by hand, check it into version control, and run
  `conda global sync` on any machine to reproduce your setup.

conda's solver
: conda-global uses conda's own solver and channel infrastructure.
  Your `.condarc` settings, channel priorities, and authentication
  tokens all work as expected.

## Acknowledgements

conda-global draws inspiration from
[pipx](https://pipx.pypa.io/),
[pixi global](https://pixi.sh/), and
[conda-express](https://github.com/jezdez/conda-express).
The trampoline design is informed by pixi's implementation with
adaptations for conda's environment layout.
