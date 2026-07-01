from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QScrollArea, QSizePolicy, QWidget

from mtnc.branding import PIANO_KEYS, PIANO_START
from mtnc.ui.theme import COLORS

WHITE_PCS = {0, 2, 4, 5, 7, 9, 11}
BLACK_PCS = {1, 3, 6, 8, 10}
WHITE_KEY_WIDTH = 20
KEY_HEIGHT = 130


class VirtualKeyboard(QWidget):
    key_pressed = Signal(int)
    key_released = Signal(int)

    def __init__(
        self,
        start_midi: int = PIANO_START,
        num_keys: int = PIANO_KEYS,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._start = start_midi
        self._num = num_keys
        self._active: set[int] = set()
        self._playback: set[int] = set()
        self.setFixedHeight(KEY_HEIGHT)
        self.setMinimumWidth(self._content_width())
        self.setMaximumWidth(self._content_width())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _content_width(self) -> int:
        return len(self._white_keys()) * WHITE_KEY_WIDTH

    def _white_keys(self) -> list[int]:
        keys = []
        for i in range(self._num):
            pitch = self._start + i
            if pitch % 12 in WHITE_PCS:
                keys.append(pitch)
        return keys

    def sizeHint(self) -> QSize:
        return QSize(self._content_width(), KEY_HEIGHT)

    def scroll_to_pitch(self, pitch: int) -> None:
        parent = self.parent()
        while parent and not isinstance(parent, QScrollArea):
            parent = parent.parent()
        if not isinstance(parent, QScrollArea):
            return
        whites = self._white_keys()
        try:
            idx = next(i for i, p in enumerate(whites) if p >= pitch)
        except StopIteration:
            idx = len(whites) - 1
        x = max(0, idx * WHITE_KEY_WIDTH - parent.viewport().width() // 3)
        parent.horizontalScrollBar().setValue(x)

    def set_active_notes(self, pitches: set[int]) -> None:
        self._playback = set(pitches)
        self.update()

    def press_key(self, pitch: int) -> None:
        if not (self._start <= pitch < self._start + self._num):
            return
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

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        h = self.height()
        whites = self._white_keys()
        white_w = WHITE_KEY_WIDTH
        black_w = white_w * 0.58
        black_h = h * 0.6

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
            white_idx = sum(1 for p in whites if p < pitch)
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
        h = self.height()
        whites = self._white_keys()
        white_w = WHITE_KEY_WIDTH
        black_w = white_w * 0.58
        black_h = h * 0.6

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


class PianoKeyboardPanel(QScrollArea):
    """Horizontally scrollable 88-key piano."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self._keyboard = VirtualKeyboard()
        self.setWidget(self._keyboard)
        self.setMinimumHeight(KEY_HEIGHT + 18)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    @property
    def keyboard(self) -> VirtualKeyboard:
        return self._keyboard

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.keyboard.scroll_to_pitch(60)
