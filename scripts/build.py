"""Build single-file Windows desktop executable with PyInstaller."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    icon_png = ROOT / "mtnc" / "assets" / "app_icon.png"
    icon_png.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT))
    from PySide6.QtWidgets import QApplication

    qt_app = QApplication([])
    from mtnc.branding import save_icon_png

    save_icon_png(icon_png)
    icon_ico = ROOT / "mtnc" / "assets" / "app_icon.ico"
    try:
        from PIL import Image

        Image.open(icon_png).save(
            icon_ico,
            format="ICO",
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        )
    except ImportError:
        icon_ico = icon_png

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "MusicToNotes",
        "--icon",
        str(icon_ico),
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
