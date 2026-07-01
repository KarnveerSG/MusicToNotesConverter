from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from mtnc.branding import app_icon
from mtnc.paths import app_data_dir
from mtnc.ui.main_window import MainWindow
from mtnc.ui.theme import stylesheet


def main() -> int:
    app_data_dir()
    app = QApplication(sys.argv)
    app.setApplicationName("MusicToNotes")
    app.setOrganizationName("MusicToNotes")
    app.setWindowIcon(app_icon())
    app.setStyle("Fusion")
    app.setStyleSheet(stylesheet())
    window = MainWindow()
    window.setAcceptDrops(True)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
