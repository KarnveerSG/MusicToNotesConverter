from __future__ import annotations

from pathlib import Path

import numpy as np

from mtnc.export.exporters import cues_to_srt, cues_to_vtt, notes_to_midi_file
from mtnc.instruments import INSTRUMENTS, get_instrument
from mtnc.models import NoteEvent, SubtitleCue
from mtnc.music_theory import keyboard_pitch_for_key, midi_to_name
from mtnc.pipeline.pitch_detection import _f0_to_notes
from mtnc.settings import AppSettings


def test_instruments_defined():
    assert "piano" in INSTRUMENTS
    assert "guitar" in INSTRUMENTS
    assert "violin" in INSTRUMENTS
    piano = get_instrument("piano")
    assert piano.midi_program == 0
    assert get_instrument("unknown").id == "piano"


def test_midi_to_name():
    assert midi_to_name(60) == "C4"
    assert midi_to_name(69) == "A4"


def test_keyboard_mapping():
    assert keyboard_pitch_for_key("N") == 57
    assert keyboard_pitch_for_key("n", 1) == 69


def test_f0_to_notes_basic():
    times = np.array([0.0, 0.1, 0.2, 0.3])
    f0 = np.array([440.0, 440.0, 440.0, np.nan])
    voiced = np.array([True, True, True, False])
    notes = _f0_to_notes(f0, voiced, times, min_duration=0.05)
    assert len(notes) == 1
    assert notes[0].pitch == 69


def test_subtitle_export():
    cues = [SubtitleCue(1, 0.0, 1.5, "Hello")]
    srt = cues_to_srt(cues)
    assert "Hello" in srt
    assert "-->" in srt
    vtt = cues_to_vtt(cues)
    assert vtt.startswith("WEBVTT")


def test_notes_to_midi(tmp_path):
    notes = [NoteEvent(0.0, 0.5, 60, 80)]
    out = tmp_path / "test.mid"
    notes_to_midi_file(notes, out, program=24)
    assert out.is_file()
    assert out.stat().st_size > 0


def test_settings_roundtrip(tmp_path, monkeypatch):
    config_file = tmp_path / "settings.json"

    def mock_config_path(cls) -> Path:
        return config_file

    monkeypatch.setattr(AppSettings, "config_path", classmethod(mock_config_path))
    s = AppSettings(instrument_id="violin", auto_process=False)
    s.save()
    assert config_file.is_file()
    loaded = AppSettings.load()
    assert loaded.instrument_id == "violin"
    assert loaded.auto_process is False
