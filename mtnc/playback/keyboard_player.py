from __future__ import annotations

import tempfile
import threading
from pathlib import Path

import numpy as np

from mtnc.instruments import get_instrument
from mtnc.playback.midi_player import _resolve_soundfont


class KeyboardSynth:
    """Lightweight note playback for QWERTY / on-screen keyboard."""

    def __init__(self, instrument_id: str = "piano", soundfont_path: Path | None = None) -> None:
        self._instrument_id = instrument_id
        self._soundfont = soundfont_path
        self._held: set[int] = set()
        self._lock = threading.Lock()
        self._fs = None

    def set_instrument(self, instrument_id: str) -> None:
        self._instrument_id = instrument_id

    def set_soundfont(self, path: Path | None) -> None:
        self._soundfont = path

    def note_on(self, pitch: int, velocity: int = 80) -> None:
        with self._lock:
            if pitch in self._held:
                return
            self._held.add(pitch)
        threading.Thread(target=self._play_note, args=(pitch, velocity), daemon=True).start()

    def note_off(self, pitch: int) -> None:
        with self._lock:
            self._held.discard(pitch)

    def all_off(self) -> None:
        with self._lock:
            self._held.clear()

    def _play_note(self, pitch: int, velocity: int) -> None:
        try:
            import pretty_midi

            from mtnc.export.exporters import notes_to_midi_file
            from mtnc.models import NoteEvent
            from mtnc.playback.midi_player import render_midi_to_wav

            inst = get_instrument(self._instrument_id)
            note = NoteEvent(start=0.0, end=0.35, pitch=pitch, velocity=velocity)
            tmp_mid = Path(tempfile.gettempdir()) / f"mtnc_kb_{pitch}.mid"
            notes_to_midi_file([note], tmp_mid, program=inst.midi_program)
            tmp_wav = Path(tempfile.gettempdir()) / f"mtnc_kb_{pitch}.wav"
            sf = _resolve_soundfont(self._soundfont)
            render_midi_to_wav(tmp_mid, tmp_wav, sf)
            self._play_wav(tmp_wav)
        except Exception:
            self._beep(pitch)

    def _play_wav(self, path: Path) -> None:
        try:
            import soundfile as sf
            from PySide6.QtCore import QUrl
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

            data, sr = sf.read(str(path))
            if not hasattr(self, "_player"):
                self._player = QMediaPlayer()
                self._audio_out = QAudioOutput()
                self._player.setAudioOutput(self._audio_out)
            self._player.setSource(QUrl.fromLocalFile(str(path)))
            self._player.play()
        except Exception:
            pass

    def _beep(self, pitch: int) -> None:
        try:
            import soundfile as sf

            sr = 22050
            t = np.linspace(0, 0.25, int(sr * 0.25), endpoint=False)
            freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
            wave = 0.3 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)
            tmp = Path(tempfile.gettempdir()) / f"mtnc_beep_{pitch}.wav"
            sf.write(str(tmp), wave.astype(np.float32), sr)
            self._play_wav(tmp)
        except Exception:
            pass
