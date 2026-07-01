from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from mtnc.ui.main_window import MainWindow
from mtnc.ui.theme import stylesheet


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MusicToNotesConverter")
    app.setStyle("Fusion")
    app.setStyleSheet(stylesheet())
    window = MainWindow()
    window.setAcceptDrops(True)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
