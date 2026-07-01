from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

ACCENT = QColor("#7c9cff")
BG = QColor("#252536")
SURFACE = QColor("#1e1e2e")
NOTE = QColor("#c9e7ff")
WAVE = QColor("#9ab4ff")

PIANO_START = 21
PIANO_KEYS = 88


def paint_logo(painter: QPainter, rect: QRectF, *, large: bool = False) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    cx, cy = rect.center().x(), rect.center().y()
    r = min(rect.width(), rect.height()) * 0.42

    painter.setBrush(BG)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), r * 0.35, r * 0.35)

    # Audio waveform bars → note
    bar_w = r * 0.11
    base_x = cx - r * 0.55
    heights = (0.35, 0.65, 0.5, 0.85, 0.45, 0.7, 0.4)
    painter.setBrush(WAVE)
    for i, h in enumerate(heights):
        bh = r * h
        painter.drawRoundedRect(
            QRectF(base_x + i * (bar_w + 3), cy + r * 0.35 - bh, bar_w, bh),
            2,
            2,
        )

    # Staff lines + note head
    staff_x = cx + r * 0.05
    gap = r * 0.11
    pen = QPen(NOTE, 1.5 if large else 1.2)
    painter.setPen(pen)
    for i in range(5):
        y = cy - gap + i * gap * 0.5
        painter.drawLine(QPointF(staff_x, y), QPointF(staff_x + r * 0.75, y))

    painter.setBrush(NOTE)
    painter.setPen(QPen(ACCENT, 1.5))
    note_x = staff_x + r * 0.42
    note_y = cy - gap * 0.25
    painter.drawEllipse(QPointF(note_x, note_y), r * 0.09, r * 0.07)
    painter.drawLine(QPointF(note_x + r * 0.08, note_y), QPointF(note_x + r * 0.08, note_y - r * 0.35))


def make_pixmap(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    paint_logo(painter, QRectF(0, 0, size, size), large=size >= 96)
    painter.end()
    return pix


def app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(make_pixmap(size))
    return icon


def save_icon_png(path: Path, size: int = 256) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    make_pixmap(size).save(str(path))
