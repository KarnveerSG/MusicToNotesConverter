from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from mtnc.models import NoteEvent
from mtnc.music_theory import midi_to_name, midi_to_staff_y
from mtnc.ui.theme import COLORS


class StaffView(QWidget):
    """Scrollable treble-clef staff notation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._notes: list[NoteEvent] = []
        self._position = 0.0
        self._max_time = 1.0
        self.setMinimumHeight(200)

    def set_notes(self, notes: list[NoteEvent]) -> None:
        self._notes = list(notes)
        self._max_time = max((n.end for n in notes), default=1.0)
        self.update()

    def set_position(self, seconds: float) -> None:
        self._position = seconds
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(COLORS["surface"]))

        w, h = self.width(), self.height()
        margin_l, margin_r = 56, 16
        staff_top = h // 2 - 20
        line_gap = 10
        px_per_sec = max(60.0, (w - margin_l - margin_r) / max(self._max_time, 1.0))

        pen = QPen(QColor(COLORS["text_muted"]))
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(5):
            y = staff_top + i * line_gap
            painter.drawLine(margin_l, y, w - margin_r, y)

        painter.setPen(QColor(COLORS["text"]))
        painter.setFont(QFont("Segoe UI Symbol", 28))
        painter.drawText(8, staff_top + 4 * line_gap + 8, "𝄞")

        note_pen = QPen(QColor(COLORS["note_border"]))
        note_brush = QColor(COLORS["note"])
        playhead_x = margin_l + self._position * px_per_sec

        for note in self._notes:
            x = margin_l + note.start * px_per_sec
            y = staff_top + (4 - midi_to_staff_y(note.pitch) / 2) * (line_gap / 2)
            painter.setBrush(note_brush)
            painter.setPen(note_pen)
            painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)
            if midi_to_staff_y(note.pitch) > 4 or midi_to_staff_y(note.pitch) < -4:
                stem_h = 28 if midi_to_staff_y(note.pitch) >= 0 else -28
                painter.drawLine(int(x) + 5, int(y), int(x) + 5, int(y) - stem_h)

        painter.setPen(QPen(QColor(COLORS["playhead"]), 2))
        painter.drawLine(int(playhead_x), staff_top - 20, int(playhead_x), staff_top + 4 * line_gap + 20)

        if self._notes:
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.setFont(QFont("Segoe UI", 8))
            last = self._notes[min(len(self._notes) - 1, 20)]
            painter.drawText(
                margin_l,
                h - 8,
                f"{len(self._notes)} notes · {midi_to_name(last.pitch)} …",
            )
