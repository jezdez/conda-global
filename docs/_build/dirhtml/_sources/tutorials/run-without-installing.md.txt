# Run tools without installing

`conda global run` lets you execute a tool in a temporary environment
that is created on demand and cleaned up automatically. No permanent
installation, no manifest entry, no trampoline.

This is useful for one-off commands, trying out a tool before
committing, or running a specific version.

## Basic usage

```bash
$ conda global run ruff -- check .
  Running tool ruff...
```

Everything after `--` is passed to the tool as arguments.

## Try before you install

Not sure if a tool fits your workflow? Run it first:

```bash
$ conda global run bat -- README.md
```

If you like it, install it permanently:

```bash
$ conda global install bat
```

## Use a specific channel

Pull the tool from a non-default channel:

```bash
$ conda global run -c bioconda samtools -- --version
```

Multiple `-c` flags are supported:

```bash
$ conda global run -c nvidia -c conda-forge cuda-toolkit -- nvcc --version
```

## How it works

1. A temporary environment named `_cg_run_<package>` is created
2. The package is solved and installed
3. The matching binary is located and executed
4. The temporary environment is removed — even if the tool crashes

This is similar to `pipx run` or `npx`.

## When to use run vs install

Use `conda global run` when you:

- Need a tool for a single command
- Want to try something without committing
- Are scripting a CI job that needs a tool temporarily

Use `conda global install` when you:

- Use the tool regularly
- Want it available on PATH permanently
- Want it tracked in your manifest for `conda global sync`
