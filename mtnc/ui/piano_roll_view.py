from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import QGraphicsRectItem, QVBoxLayout, QWidget

from mtnc.models import NoteEvent
from mtnc.ui.theme import COLORS


class PianoRollView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plot = pg.PlotWidget(background=COLORS["surface"])
        self._plot.showGrid(x=True, y=True, alpha=0.15)
        self._plot.setLabel("bottom", "Time", units="s")
        self._plot.setLabel("left", "MIDI pitch")
        self._plot.setMenuEnabled(False)
        self._items: list[QGraphicsRectItem] = []
        self._playhead = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(COLORS["playhead"], width=2))
        self._plot.addItem(self._playhead)
        self._duration = 0.0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)

    def set_notes(self, notes: list[NoteEvent]) -> None:
        for item in self._items:
            self._plot.removeItem(item)
        self._items.clear()
        if not notes:
            return
        min_pitch = min(n.pitch for n in notes) - 2
        max_pitch = max(n.pitch for n in notes) + 2
        max_time = max(n.end for n in notes)
        for note in notes:
            rect = QGraphicsRectItem(
                note.start,
                note.pitch - 0.4,
                max(note.end - note.start, 0.03),
                0.8,
            )
            rect.setBrush(pg.mkBrush(COLORS["note"]))
            rect.setPen(pg.mkPen(COLORS["note_border"]))
            self._plot.addItem(rect)
            self._items.append(rect)
        self._duration = max(max_time, 0.1)
        self._plot.setXRange(0, self._duration, padding=0.02)
        self._plot.setYRange(min_pitch, max_pitch, padding=0.05)
        self._playhead.setValue(0)

    def set_position(self, seconds: float) -> None:
        self._playhead.setValue(max(0.0, min(seconds, self._duration)))
