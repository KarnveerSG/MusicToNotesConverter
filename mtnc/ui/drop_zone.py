from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from mtnc.ui.theme import COLORS


class DropZoneOverlay(QWidget):
    """Full-area overlay shown before audio is loaded."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("🎵")
        icon.setStyleSheet("font-size: 48pt;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("Drop audio here")
        title.setObjectName("dropTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("MP3 · WAV · FLAC · OGG · M4A · AAC")
        hint.setObjectName("meta")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel("or use File → Open Audio (Ctrl+O)")
        sub.setObjectName("meta")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(sub)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(COLORS["accent"])
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)
        margin = 24
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        painter.drawRoundedRect(rect, 12, 12)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        parent = self.parent()
        if parent and hasattr(parent, "_handle_drop"):
            parent._handle_drop(event)  # type: ignore[attr-defined]
