from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from mtnc.audio.loader import downsample_for_display
from mtnc.ui.theme import COLORS


class WaveformView(QWidget):
    position_changed = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._duration = 0.0
        self._playhead = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(COLORS["playhead"], width=2))
        self._plot = pg.PlotWidget(background=COLORS["surface"])
        self._plot.showGrid(x=True, y=False, alpha=0.2)
        self._plot.setLabel("bottom", "Time", units="s")
        self._plot.setMenuEnabled(False)
        self._curve = self._plot.plot(pen=pg.mkPen(COLORS["waveform"], width=1))
        self._fill = pg.FillBetweenItem(self._curve, pg.PlotDataItem([0], [0]), brush=pg.mkBrush(COLORS["waveform_fill"] + "88"))
        self._plot.addItem(self._fill)
        self._plot.addItem(self._playhead)
        self._plot.scene().sigMouseClicked.connect(self._on_click)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)

    def set_audio(self, samples: np.ndarray, sample_rate: int) -> None:
        self._duration = len(samples) / sample_rate
        times, envelope = downsample_for_display(samples)
        time_seconds = times * self._duration
        self._curve.setData(time_seconds, envelope)
        self._fill.setCurves(self._curve, pg.PlotDataItem(time_seconds, np.zeros_like(envelope)))
        self._plot.setXRange(0, max(self._duration, 0.01), padding=0)
        self._playhead.setValue(0)

    def set_position(self, seconds: float) -> None:
        self._playhead.setValue(max(0.0, min(seconds, self._duration)))

    def _on_click(self, event) -> None:
        if self._duration <= 0:
            return
        pos = self._plot.plotItem.vb.mapSceneToView(event.scenePos())
        seconds = max(0.0, min(float(pos.x()), self._duration))
        self.set_position(seconds)
        self.position_changed.emit(seconds)
