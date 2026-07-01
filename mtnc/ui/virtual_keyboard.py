from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from mtnc.ui.theme import COLORS

WHITE_PCS = {0, 2, 4, 5, 7, 9, 11}
BLACK_PCS = {1, 3, 6, 8, 10}


class VirtualKeyboard(QWidget):
    key_pressed = Signal(int)
    key_released = Signal(int)

    def __init__(self, start_midi: int = 48, num_keys: int = 25, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._start = start_midi
        self._num = num_keys
        self._active: set[int] = set()
        self._playback: set[int] = set()
        self.setMinimumHeight(100)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_active_notes(self, pitches: set[int]) -> None:
        self._playback = set(pitches)
        self.update()

    def press_key(self, pitch: int) -> None:
        self._active.add(pitch)
        self.key_pressed.emit(pitch)
        self.update()

    def release_key(self, pitch: int) -> None:
        self._active.discard(pitch)
        self.key_released.emit(pitch)
        self.update()

    def clear_active(self) -> None:
        self._active.clear()
        self.update()

    def _white_keys(self) -> list[int]:
        keys = []
        for i in range(self._num):
            pitch = self._start + i
            if pitch % 12 in WHITE_PCS:
                keys.append(pitch)
        return keys

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        whites = self._white_keys()
        if not whites:
            return
        white_w = w / len(whites)
        black_w = white_w * 0.55
        black_h = h * 0.58

        for idx, pitch in enumerate(whites):
            x = idx * white_w
            color = self._key_color(pitch, is_black=False)
            painter.fillRect(int(x), 0, int(white_w) + 1, h, color)
            painter.setPen(QPen(QColor(COLORS["border"])))
            painter.drawRect(int(x), 0, int(white_w), h)

        for i in range(self._num):
            pitch = self._start + i
            if pitch % 12 not in BLACK_PCS:
                continue
            white_idx = sum(1 for p in self._white_keys() if p < pitch)
            x = white_idx * white_w - black_w / 2
            color = self._key_color(pitch, is_black=True)
            painter.fillRect(int(x), 0, int(black_w), int(black_h), color)
            painter.setPen(QPen(QColor("#111")))
            painter.drawRect(int(x), 0, int(black_w), int(black_h))

    def _key_color(self, pitch: int, is_black: bool) -> QColor:
        if pitch in self._active:
            return QColor(COLORS["accent_hover"])
        if pitch in self._playback:
            return QColor(COLORS["success"])
        return QColor("#1a1a28" if is_black else "#e8e8f0")

    def mousePressEvent(self, event) -> None:
        pitch = self._pitch_at(event.position().x(), event.position().y())
        if pitch is not None:
            self.press_key(pitch)

    def mouseReleaseEvent(self, event) -> None:
        pitch = self._pitch_at(event.position().x(), event.position().y())
        if pitch is not None:
            self.release_key(pitch)

    def _pitch_at(self, x: float, y: float) -> int | None:
        w, h = self.width(), self.height()
        whites = self._white_keys()
        white_w = w / len(whites)
        black_w = white_w * 0.55
        black_h = h * 0.58

        if y <= black_h:
            for i in range(self._num):
                pitch = self._start + i
                if pitch % 12 not in BLACK_PCS:
                    continue
                white_idx = sum(1 for p in whites if p < pitch)
                bx = white_idx * white_w - black_w / 2
                if bx <= x <= bx + black_w:
                    return pitch

        idx = int(x / white_w)
        if 0 <= idx < len(whites):
            return whites[idx]
        return None
