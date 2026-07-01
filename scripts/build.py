"""Build Windows desktop executable with PyInstaller."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        "MusicToNotes",
        "--paths",
        str(ROOT),
        "--collect-all",
        "PySide6",
        "--collect-all",
        "pyqtgraph",
        "--hidden-import",
        "faster_whisper",
        "--hidden-import",
        "pretty_midi",
        "--hidden-import",
        "librosa",
        str(ROOT / "mtnc" / "app.py"),
    ]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
