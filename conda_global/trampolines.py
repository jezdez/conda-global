"""Deploy and remove trampoline binaries and JSON configs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from conda.base.constants import on_win

from .paths import global_bin_dir as _default_bin_dir


class TrampolineManager:
    """Manages trampoline binaries and their JSON configs.

    Usage::

        trampolines = TrampolineManager()                # ~/.conda/bin/
        trampolines = TrampolineManager(tmp / "bin")      # test path

        trampolines.deploy("gh", exe_path, "/path/to/bin")
        trampolines.remove("gh")
    """

    def __init__(self, bin_dir: Path | None = None) -> None:
        self.bin_dir = bin_dir or _default_bin_dir()

    @property
    def _config_dir(self) -> Path:
        return self.bin_dir / ".trampoline"

    @property
    def _master_path(self) -> Path:
        return self._config_dir / "trampoline_bin"

    @property
    def _extension(self) -> str:
        return ".exe" if on_win else ""

    def ensure_master(self) -> Path:
        """Ensure the master trampoline binary exists, deploying it if needed."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

        if not self._master_path.is_file():
            source = _find_embedded_trampoline()
            shutil.copy2(source, self._master_path)
            if not on_win:
                self._master_path.chmod(0o755)

        return self._master_path

    def deploy(
        self,
        exposed_name: str,
        exe_path: Path,
        path_diff: str,
        env: dict[str, str] | None = None,
    ) -> Path:
        """Deploy a trampoline for an exposed binary.

        Creates a hardlink from ``<bin_dir>/<exposed_name>`` to the master
        trampoline, and writes the JSON config.

        Falls back to copying if hardlinking fails.
        """
        master = self.ensure_master()
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        trampoline_path = self.bin_dir / f"{exposed_name}{self._extension}"

        if not trampoline_path.exists():
            try:
                trampoline_path.hardlink_to(master)
            except OSError:
                shutil.copy2(master, trampoline_path)

        if not on_win:
            trampoline_path.chmod(0o755)

        config = {
            "exe": str(exe_path),
            "path_diff": path_diff,
            "env": env or {},
        }
        config_path = self._config_dir / f"{exposed_name}.json"
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        return trampoline_path

    def remove(self, exposed_name: str) -> None:
        """Remove a trampoline binary and its config."""
        trampoline_path = self.bin_dir / f"{exposed_name}{self._extension}"
        config_path = self._config_dir / f"{exposed_name}.json"

        if trampoline_path.exists():
            trampoline_path.unlink()
        if config_path.exists():
            config_path.unlink()


def _find_embedded_trampoline() -> Path:
    """Locate the trampoline binary shipped inside the wheel."""
    package_dir = Path(__file__).parent
    if on_win:
        candidates = [
            package_dir / "trampoline.exe",
            package_dir / ".." / "Scripts" / "trampoline.exe",
        ]
    else:
        candidates = [
            package_dir / "trampoline",
            package_dir / ".." / "bin" / "trampoline",
        ]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file():
            return resolved
    msg = "trampoline binary not found in package"
    raise FileNotFoundError(msg)
