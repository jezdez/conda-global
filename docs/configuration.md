# Configuration

## Manifest

The manifest at `~/.cg/global.toml` is the source of truth for
all globally installed tools. It is written by conda-global commands
and can also be edited by hand.

### Format

Each tool environment is defined under `[envs.<name>]`:

```toml
[envs.gh]
channels = ["conda-forge"]
dependencies = { gh = "*" }
exposed = { gh = "gh" }

[envs.ruff]
channels = ["conda-forge"]
dependencies = { ruff = ">=0.4" }
exposed = { ruff = "ruff" }
pinned = true

[envs.py314]
channels = ["conda-forge"]
dependencies = { python = "*", pip = "*" }
exposed = { "python3.14" = "python3.14", pip = "pip3.14" }
```

### Fields

`channels`
: List of conda channels to search when solving the environment.
  Order matters — earlier channels have higher priority.

`dependencies`
: Map of package names to version specs. Use `"*"` for any version,
  or a conda match spec like `">=0.4"`, `">=1.0,<2"`.

`exposed`
: Map of exposed names to binary names. The key is the name that
  appears on PATH; the value is the binary inside the environment's
  `bin/` (or `Scripts/` on Windows).

`pinned`
: Optional boolean. If `true`, the tool is skipped during
  `conda global update` (unless targeted explicitly with `-e`).
  Defaults to `false`.

## Filesystem layout

```
~/.cg/
├── bin/                         ← exposed trampolines (on PATH)
│   ├── ruff                       hardlink → trampoline/_cg_trampoline
│   ├── gh                         hardlink → trampoline/_cg_trampoline
│   └── trampoline/
│       ├── _cg_trampoline         master binary (compiled Rust)
│       ├── ruff.json              config for ruff trampoline
│       └── gh.json                config for gh trampoline
├── envs/                        ← isolated tool environments
│   ├── ruff/
│   │   ├── bin/ruff               real binary
│   │   └── conda-meta/           conda metadata (marks valid env)
│   └── gh/
│       ├── bin/gh
│       └── conda-meta/
└── global.toml                  ← manifest
```

On Windows, `~/.cg` is `%USERPROFILE%\.cg` and `bin/` uses
platform-appropriate extensions (`.exe`).

### Paths

| Path | Purpose |
|------|---------|
| `~/.cg/bin/` | Trampoline directory, added to PATH |
| `~/.cg/bin/trampoline/` | Master binary and JSON configs |
| `~/.cg/envs/` | Tool environments (one prefix per tool) |
| `~/.cg/global.toml` | Manifest |

## Trampoline config files

Each exposed binary has a JSON config at
`~/.cg/bin/trampoline/<name>.json`:

```json
{
  "exe": "/home/user/.cg/envs/gh/bin/gh",
  "path_diff": "/home/user/.cg/envs/gh/bin",
  "env": {}
}
```

`exe`
: Absolute path to the real binary inside the tool environment.

`path_diff`
: Directory to prepend to `PATH` before launching.

`env`
: Additional environment variables to set. Empty by default.

These files are managed automatically. Editing them is only useful
for debugging.

## Environment variables

`CONDA_GLOBAL_HOME`
: Override the base directory for all conda-global paths (manifest,
  environments, trampolines). Defaults to `~/.cg`. Supports `~`
  expansion and relative paths.

`EDITOR` / `VISUAL`
: Used by `conda global edit` to open the manifest. `VISUAL` takes
  precedence.
