from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mtnc.instruments import INSTRUMENTS
from mtnc.settings import AppSettings


class SettingsPanel(QWidget):
    settings_changed = Signal(object)

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self.setObjectName("settingsPanel")

        layout = QVBoxLayout(self)
        title = QLabel("Settings")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        inst_box = QGroupBox("Instrument")
        inst_form = QFormLayout(inst_box)
        self._instrument = QComboBox()
        for inst in INSTRUMENTS.values():
            self._instrument.addItem(inst.name, inst.id)
        idx = self._instrument.findData(settings.instrument_id)
        if idx >= 0:
            self._instrument.setCurrentIndex(idx)
        self._instrument.currentIndexChanged.connect(self._emit)
        inst_form.addRow("Voice:", self._instrument)
        layout.addWidget(inst_box)

        proc_box = QGroupBox("Processing")
        proc_form = QFormLayout(proc_box)
        self._whisper = QComboBox()
        for model in ("tiny", "base", "small", "medium"):
            self._whisper.addItem(model, model)
        widx = self._whisper.findData(settings.whisper_model)
        if widx >= 0:
            self._whisper.setCurrentIndex(widx)
        self._whisper.currentIndexChanged.connect(self._emit)
        proc_form.addRow("Whisper:", self._whisper)
        self._auto_process = QCheckBox("Auto-process on drop")
        self._auto_process.setChecked(settings.auto_process)
        self._auto_process.toggled.connect(self._emit)
        proc_form.addRow(self._auto_process)
        layout.addWidget(proc_box)

        kb_box = QGroupBox("Keyboard")
        kb_form = QFormLayout(kb_box)
        self._kb_enabled = QCheckBox("Enable QWERTY piano")
        self._kb_enabled.setChecked(settings.keyboard_enabled)
        self._kb_enabled.toggled.connect(self._emit)
        kb_form.addRow(self._kb_enabled)
        self._octave = QSpinBox()
        self._octave.setRange(-2, 2)
        self._octave.setValue(settings.keyboard_octave - 4)
        self._octave.valueChanged.connect(self._emit)
        kb_form.addRow("Octave shift:", self._octave)
        hint = QLabel("Keys: Z-M row + Q-P row")
        hint.setObjectName("meta")
        hint.setWordWrap(True)
        kb_form.addRow(hint)
        layout.addWidget(kb_box)

        sf_btn = QPushButton("SoundFont…")
        sf_btn.clicked.connect(self._pick_soundfont)
        layout.addWidget(sf_btn)
        self._sf_label = QLabel(settings.soundfont_path or "Default / none")
        self._sf_label.setObjectName("meta")
        self._sf_label.setWordWrap(True)
        layout.addWidget(self._sf_label)
        layout.addStretch()

    def _pick_soundfont(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(self, "Select SoundFont", "", "*.sf2")
        if path:
            self._settings.soundfont_path = path
            self._sf_label.setText(path)
            self._emit()

    def _emit(self) -> None:
        self._settings.instrument_id = self._instrument.currentData()
        self._settings.whisper_model = self._whisper.currentData()
        self._settings.auto_process = self._auto_process.isChecked()
        self._settings.keyboard_enabled = self._kb_enabled.isChecked()
        self._settings.keyboard_octave = 4 + self._octave.value()
        self._settings.save()
        self.settings_changed.emit(self._settings)

    @property
    def settings(self) -> AppSettings:
        return self._settings
