from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QKeyEvent, QKeySequence
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from mtnc.audio.loader import load_audio
from mtnc.export.exporters import cues_to_srt, notes_to_midi_file, write_midi_copy
from mtnc.instruments import get_instrument
from mtnc.models import ProcessingResult
from mtnc.music_theory import keyboard_pitch_for_key
from mtnc.pipeline.worker import PipelineWorker
from mtnc.playback.keyboard_player import KeyboardSynth
from mtnc.playback.midi_player import render_midi_to_wav
from mtnc.settings import AppSettings
from mtnc.ui.drop_zone import DropZoneOverlay
from mtnc.ui.piano_roll_view import PianoRollView
from mtnc.ui.settings_panel import SettingsPanel
from mtnc.ui.staff_view import StaffView
from mtnc.ui.subtitle_view import SubtitleView
from mtnc.ui.virtual_keyboard import VirtualKeyboard
from mtnc.ui.waveform_view import WaveformView

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music To Notes")
        self.resize(1360, 900)

        self._settings = AppSettings.load()
        self._audio_path: Path | None = None
        self._result: ProcessingResult | None = None
        self._worker: PipelineWorker | None = None
        self._soundfont: Path | None = (
            Path(self._settings.soundfont_path) if self._settings.soundfont_path else None
        )
        self._pressed_keys: set[str] = set()

        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._player.positionChanged.connect(self._on_player_position)

        self._kb_synth = KeyboardSynth(self._settings.instrument_id, self._soundfont)

        self._waveform = WaveformView()
        self._drop_zone = DropZoneOverlay(self._waveform)
        self._subtitles = SubtitleView()
        self._piano_roll = PianoRollView()
        self._staff = StaffView()
        self._virtual_kb = VirtualKeyboard()
        self._settings_panel = SettingsPanel(self._settings)
        self._settings_panel.settings_changed.connect(self._on_settings_changed)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setVisible(False)
        self._stage_label = QLabel("Drop an audio file or open one to begin.")
        self._stage_label.setObjectName("meta")
        self._time_label = QLabel("00:00 / 00:00")
        self._time_label.setObjectName("meta")

        self._virtual_kb.key_pressed.connect(self._on_virtual_key_pressed)
        self._virtual_kb.key_released.connect(self._on_virtual_key_released)

        self._build_menu()
        self._build_toolbar()
        self._build_layout()
        self._build_transport()
        self._set_actions_enabled(False)
        self._sync_drop_zone()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        self._open_action = QAction("&Open Audio...", self)
        self._open_action.setShortcut(QKeySequence.Open)
        self._open_action.triggered.connect(self._open_file)
        file_menu.addAction(self._open_action)

        self._process_action = QAction("&Process", self)
        self._process_action.setShortcut("Ctrl+R")
        self._process_action.triggered.connect(self._start_processing)
        file_menu.addAction(self._process_action)

        file_menu.addSeparator()
        quit_action = QAction("E&xit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        export_menu = self.menuBar().addMenu("&Export")
        self._export_srt = QAction("Subtitles (.srt)", self)
        self._export_srt.triggered.connect(lambda: self._export_subtitles("srt"))
        export_menu.addAction(self._export_srt)
        self._export_vtt = QAction("Subtitles (.vtt)", self)
        self._export_vtt.triggered.connect(lambda: self._export_subtitles("vtt"))
        export_menu.addAction(self._export_vtt)
        self._export_midi = QAction("MIDI (.mid)", self)
        self._export_midi.triggered.connect(self._export_midi_file)
        export_menu.addAction(self._export_midi)
        self._export_wav = QAction("Rendered audio (.wav)", self)
        self._export_wav.triggered.connect(self._export_wav_file)
        export_menu.addAction(self._export_wav)

        inst_menu = self.menuBar().addMenu("&Instrument")
        self._inst_actions: dict[str, QAction] = {}
        for inst_id in ("piano", "guitar", "violin"):
            inst = get_instrument(inst_id)
            action = QAction(inst.name, self)
            action.setCheckable(True)
            action.setChecked(inst_id == self._settings.instrument_id)
            action.triggered.connect(lambda checked, i=inst_id: self._select_instrument(i))
            inst_menu.addAction(action)
            self._inst_actions[inst_id] = action

        settings_menu = self.menuBar().addMenu("&Settings")
        sf_action = QAction("SoundFont path...", self)
        sf_action.triggered.connect(self._pick_soundfont)
        settings_menu.addAction(sf_action)

        help_menu = self.menuBar().addMenu("&Help")
        kb_action = QAction("Keyboard shortcuts", self)
        kb_action.triggered.connect(self._show_keyboard_help)
        help_menu.addAction(kb_action)

    def _build_toolbar(self) -> None:
        bar = QToolBar("Main")
        bar.setMovable(False)
        bar.addAction(self._open_action)
        bar.addAction(self._process_action)
        bar.addSeparator()
        self._inst_label = QLabel(f"  {get_instrument(self._settings.instrument_id).name}  ")
        self._inst_label.setObjectName("toolbarMeta")
        bar.addWidget(self._inst_label)
        self.addToolBar(bar)

    def _build_layout(self) -> None:
        wf_container = QWidget()
        wf_layout = QVBoxLayout(wf_container)
        wf_layout.setContentsMargins(0, 0, 0, 0)
        wf_layout.addWidget(self._waveform)
        self._wf_container = wf_container
        self._drop_zone = DropZoneOverlay(wf_container)

        center = QWidget()
        layout = QVBoxLayout(center)
        layout.setSpacing(8)
        layout.addWidget(wf_container, stretch=2)
        layout.addWidget(self._progress)
        layout.addWidget(self._stage_label)

        tabs = QTabWidget()
        tabs.addTab(self._staff, "Sheet Music")
        tabs.addTab(self._piano_roll, "Piano Roll")
        tabs.addTab(self._subtitles, "Transcript")
        layout.addWidget(tabs, stretch=3)

        kb_label = QLabel("Virtual Instrument — click keys or use QWERTY")
        kb_label.setObjectName("meta")
        layout.addWidget(kb_label)
        layout.addWidget(self._virtual_kb)

        splitter = QSplitter()
        splitter.addWidget(center)
        splitter.addWidget(self._settings_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([1000, 280])
        self.setCentralWidget(splitter)

        status = QStatusBar()
        status.addPermanentWidget(self._time_label)
        self.setStatusBar(status)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_drop_zone()

    def _sync_drop_zone(self) -> None:
        show = self._audio_path is None
        self._drop_zone.setVisible(show)
        if show:
            self._drop_zone.setGeometry(self._wf_container.rect())
            self._drop_zone.raise_()

    def _build_transport(self) -> None:
        dock = QWidget()
        row = QHBoxLayout(dock)
        row.setContentsMargins(0, 0, 0, 0)
        self._play_btn = QPushButton("▶ Play")
        self._pause_btn = QPushButton("⏸ Pause")
        self._stop_btn = QPushButton("⏹ Stop")
        self._play_midi_btn = QPushButton("🎹 Play Notes")
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setVisible(False)
        self._play_btn.clicked.connect(self._player.play)
        self._pause_btn.clicked.connect(self._player.pause)
        self._stop_btn.clicked.connect(self._stop_playback)
        self._play_midi_btn.clicked.connect(self._play_midi)
        self._cancel_btn.clicked.connect(self._cancel_processing)
        self._seek = QSlider()
        self._seek.setOrientation(Qt.Orientation.Horizontal)
        self._seek.sliderMoved.connect(self._seek_to)
        for btn in (self._play_btn, self._pause_btn, self._stop_btn, self._play_midi_btn, self._cancel_btn):
            row.addWidget(btn)
        row.addWidget(self._seek, stretch=1)
        self.statusBar().addWidget(dock, 1)

        self._waveform.position_changed.connect(self._seek_to)
        self._subtitles.cue_selected.connect(self._seek_to)

        play_shortcut = QAction(self)
        play_shortcut.setShortcut(Qt.Key.Key_Space)
        play_shortcut.triggered.connect(self._toggle_playback)
        self.addAction(play_shortcut)

    def _toggle_playback(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _handle_drop(self, event) -> None:
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in AUDIO_EXTS:
                self._load_file(path)
                event.acceptProposedAction()
                return

    def _set_actions_enabled(self, processed: bool) -> None:
        self._process_action.setEnabled(self._audio_path is not None and self._worker is None)
        self._play_midi_btn.setEnabled(processed)
        for action in (self._export_srt, self._export_vtt, self._export_midi, self._export_wav):
            action.setEnabled(processed)

    def _select_instrument(self, instrument_id: str) -> None:
        self._settings.instrument_id = instrument_id
        self._settings.save()
        for iid, action in self._inst_actions.items():
            action.setChecked(iid == instrument_id)
        self._on_settings_changed(self._settings)

    def _on_settings_changed(self, settings: AppSettings) -> None:
        self._settings = settings
        inst = get_instrument(settings.instrument_id)
        self._inst_label.setText(f"  {inst.name}  ")
        self._kb_synth.set_instrument(settings.instrument_id)
        if settings.soundfont_path:
            self._soundfont = Path(settings.soundfont_path)
            self._kb_synth.set_soundfont(self._soundfont)
        if self._result and self._result.notes:
            self._regenerate_midi()

    def _regenerate_midi(self) -> None:
        if not self._result or not self._result.notes:
            return
        import tempfile

        inst = get_instrument(self._settings.instrument_id)
        out = Path(tempfile.gettempdir()) / f"mtnc_{self._audio_path.stem}.mid"
        notes_to_midi_file(self._result.notes, out, program=inst.midi_program)
        self._result.midi_path = out

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open audio",
            "",
            "Audio (*.mp3 *.wav *.flac *.ogg *.m4a *.aac);;All (*.*)",
        )
        if path:
            self._load_file(Path(path))

    def _load_file(self, path: Path) -> None:
        try:
            audio = load_audio(path)
        except Exception as exc:
            QMessageBox.critical(self, "Load failed", str(exc))
            return
        self._audio_path = path
        self._result = None
        self._clear_views()
        self._waveform.set_audio(audio.samples, audio.sample_rate)
        self._player.setSource(QUrl.fromLocalFile(str(path)))
        self._seek.setRange(0, int(audio.duration * 1000))
        self._time_label.setText(f"00:00 / {_fmt(audio.duration)}")
        self._stage_label.setText(f"Loaded: {path.name}")
        self._set_actions_enabled(False)
        self._sync_drop_zone()
        self.statusBar().showMessage(f"{path.name} | {audio.duration:.1f}s | {audio.sample_rate} Hz", 5000)
        if self._settings.auto_process:
            self._start_processing()

    def _clear_views(self) -> None:
        self._subtitles.set_cues([])
        self._piano_roll.set_notes([])
        self._staff.set_notes([])
        self._virtual_kb.set_active_notes(set())

    def _start_processing(self) -> None:
        if not self._audio_path or self._worker:
            return
        inst = get_instrument(self._settings.instrument_id)
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._stage_label.setText("Processing...")
        self._process_action.setEnabled(False)
        self._cancel_btn.setVisible(True)
        self._worker = PipelineWorker(
            self._audio_path,
            whisper_model=self._settings.whisper_model,
            min_note=inst.min_midi,
            max_note=inst.max_midi,
            midi_program=inst.midi_program,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.stage_started.connect(lambda s: self._stage_label.setText(f"Running: {s}"))
        self._worker.finished_ok.connect(self._on_processed)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

    def _on_progress(self, _label: str, value: int) -> None:
        self._progress.setValue(value)

    def _on_processed(self, result: ProcessingResult) -> None:
        self._result = result
        self._subtitles.set_cues(result.cues)
        self._piano_roll.set_notes(result.notes)
        self._staff.set_notes(result.notes)
        lang = result.language or "unknown"
        inst = get_instrument(self._settings.instrument_id)
        self._stage_label.setText(
            f"Done — {len(result.notes)} notes ({inst.name}), {len(result.cues)} cues (lang: {lang})"
        )
        self._set_actions_enabled(True)
        self.statusBar().showMessage("Processing complete", 5000)

    def _on_failed(self, message: str) -> None:
        self._progress.setVisible(False)
        self._stage_label.setText("Processing failed.")
        QMessageBox.critical(self, "Processing failed", message)

    def _on_worker_done(self) -> None:
        self._worker = None
        self._progress.setVisible(False)
        self._cancel_btn.setVisible(False)
        self._set_actions_enabled(self._result is not None)

    def _cancel_processing(self) -> None:
        if self._worker:
            self._worker.cancel()
            self._stage_label.setText("Cancelling...")

    def _play_midi(self) -> None:
        if not self._result or not self._result.midi_path:
            return
        import tempfile

        temp_wav = Path(tempfile.gettempdir()) / "mtnc_preview.wav"
        try:
            render_midi_to_wav(self._result.midi_path, temp_wav, self._soundfont)
        except Exception as exc:
            QMessageBox.warning(
                self,
                "MIDI playback failed",
                f"{exc}\n\nSet a SoundFont in Settings for instrument playback.",
            )
            return
        self._player.setSource(QUrl.fromLocalFile(str(temp_wav)))
        self._player.play()
        self.statusBar().showMessage("Playing converted notes", 3000)

    def _on_player_position(self, ms: int) -> None:
        seconds = ms / 1000.0
        self._sync_position(seconds)
        duration_ms = self._player.duration()
        if duration_ms > 0:
            self._seek.blockSignals(True)
            self._seek.setValue(ms)
            self._seek.blockSignals(False)
            self._time_label.setText(f"{_fmt(seconds)} / {_fmt(duration_ms / 1000.0)}")

    def _sync_position(self, seconds: float) -> None:
        self._waveform.set_position(seconds)
        self._subtitles.highlight_at(seconds)
        self._piano_roll.set_position(seconds)
        self._staff.set_position(seconds)
        if self._result and self._result.notes:
            active = {
                n.pitch
                for n in self._result.notes
                if n.start <= seconds < n.end
            }
            self._virtual_kb.set_active_notes(active)

    def _seek_to(self, seconds: float) -> None:
        ms = int(seconds * 1000)
        self._player.setPosition(ms)
        self._sync_position(seconds)

    def _stop_playback(self) -> None:
        self._player.stop()
        self._sync_position(0)

    def _on_virtual_key_pressed(self, pitch: int) -> None:
        self._kb_synth.note_on(pitch)

    def _on_virtual_key_released(self, pitch: int) -> None:
        self._kb_synth.note_off(pitch)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not self._settings.keyboard_enabled:
            super().keyPressEvent(event)
            return
        text = event.text()
        if not text or text in self._pressed_keys:
            super().keyPressEvent(event)
            return
        octave_off = self._settings.keyboard_octave - 4
        pitch = keyboard_pitch_for_key(text, octave_off)
        if pitch is not None:
            self._pressed_keys.add(text)
            self._virtual_kb.press_key(pitch)
            self._kb_synth.note_on(pitch)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        text = event.text()
        if text in self._pressed_keys:
            self._pressed_keys.discard(text)
            octave_off = self._settings.keyboard_octave - 4
            pitch = keyboard_pitch_for_key(text, octave_off)
            if pitch is not None:
                self._virtual_kb.release_key(pitch)
                self._kb_synth.note_off(pitch)
            event.accept()
            return
        super().keyReleaseEvent(event)

    def _export_subtitles(self, fmt: str) -> None:
        if not self._result or not self._result.cues:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export subtitles", "", f"*.{fmt}")
        if not path:
            return
        from mtnc.export.exporters import cues_to_vtt

        content = cues_to_srt(self._result.cues) if fmt == "srt" else cues_to_vtt(self._result.cues)
        Path(path).write_text(content, encoding="utf-8")
        self.statusBar().showMessage(f"Exported {path}", 5000)

    def _export_midi_file(self) -> None:
        if not self._result or not self._result.midi_path:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export MIDI", "", "*.mid")
        if path:
            write_midi_copy(self._result.midi_path, Path(path))
            self.statusBar().showMessage(f"Exported {path}", 5000)

    def _export_wav_file(self) -> None:
        if not self._result or not self._result.midi_path:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export WAV", "", "*.wav")
        if not path:
            return
        try:
            render_midi_to_wav(self._result.midi_path, Path(path), self._soundfont)
        except Exception as exc:
            QMessageBox.warning(self, "Export failed", f"{exc}\n\nSet a SoundFont in Settings.")
            return
        self.statusBar().showMessage(f"Exported {path}", 5000)

    def _pick_soundfont(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select SoundFont", "", "*.sf2")
        if path:
            self._soundfont = Path(path)
            self._settings.soundfont_path = path
            self._settings.save()
            self._kb_synth.set_soundfont(self._soundfont)
            self.statusBar().showMessage(f"SoundFont: {path}", 5000)

    def _show_keyboard_help(self) -> None:
        QMessageBox.information(
            self,
            "Keyboard shortcuts",
            "Transport: Space = play/pause\n"
            "File: Ctrl+O open, Ctrl+R process\n"
            "QWERTY piano: Z-M (lower), Q-P (upper)\n"
            "Octave shift in Settings panel\n"
            "Drag & drop audio anywhere on window",
        )

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        self._handle_drop(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._sync_drop_zone()


def _fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"
