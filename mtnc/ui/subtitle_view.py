from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from mtnc.models import SubtitleCue


class SubtitleView(QWidget):
    cue_selected = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_click)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list)

    def set_cues(self, cues: list[SubtitleCue]) -> None:
        self._list.clear()
        for cue in cues:
            item = QListWidgetItem(f"[{_fmt(cue.start)}] {cue.text}")
            item.setData(256, cue.start)
            self._list.addItem(item)

    def highlight_at(self, seconds: float) -> None:
        for row in range(self._list.count()):
            item = self._list.item(row)
            start = item.data(256) or 0.0
            next_start = self._list.item(row + 1).data(256) if row + 1 < self._list.count() else float("inf")
            item.setSelected(start <= seconds < next_start)

    def _on_click(self, item: QListWidgetItem) -> None:
        start = item.data(256)
        if start is not None:
            self.cue_selected.emit(float(start))


def _fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"
