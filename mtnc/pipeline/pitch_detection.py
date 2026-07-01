from __future__ import annotations

import tempfile
from pathlib import Path

import librosa
import numpy as np

from mtnc.export.exporters import notes_to_midi_file
from mtnc.models import NoteEvent


def detect_notes(
    wav_path: Path,
    min_note: int = 36,
    max_note: int = 96,
    midi_program: int = 0,
) -> tuple[list[NoteEvent], Path]:
    samples, sr = librosa.load(str(wav_path), sr=22050, mono=True)
    fmin = librosa.note_to_hz(librosa.midi_to_note(min_note))
    fmax = librosa.note_to_hz(librosa.midi_to_note(max_note))

    f0, voiced_flag, _ = librosa.pyin(
        samples,
        fmin=fmin,
        fmax=fmax,
        sr=sr,
        frame_length=2048,
    )
    times = librosa.times_like(f0, sr=sr)
    notes = _f0_to_notes(f0, voiced_flag, times)

    out = Path(tempfile.gettempdir()) / f"mtnc_{wav_path.stem}.mid"
    notes_to_midi_file(notes, out, program=midi_program)
    return notes, out


def _f0_to_notes(
    f0: np.ndarray,
    voiced_flag: np.ndarray,
    times: np.ndarray,
    min_duration: float = 0.08,
) -> list[NoteEvent]:
    notes: list[NoteEvent] = []
    current_pitch: int | None = None
    start_time = 0.0

    def flush(end_time: float) -> None:
        nonlocal current_pitch, start_time
        if current_pitch is None:
            return
        if end_time - start_time >= min_duration:
            notes.append(
                NoteEvent(
                    start=start_time,
                    end=end_time,
                    pitch=current_pitch,
                    velocity=80,
                )
            )
        current_pitch = None

    for idx, (time, freq, voiced) in enumerate(zip(times, f0, voiced_flag)):
        end_time = float(times[idx + 1]) if idx + 1 < len(times) else float(time)
        if not voiced or freq is None or np.isnan(freq):
            flush(float(time))
            continue
        pitch = int(round(librosa.hz_to_midi(float(freq))))
        if current_pitch is None:
            current_pitch = pitch
            start_time = float(time)
        elif pitch != current_pitch:
            flush(float(time))
            current_pitch = pitch
            start_time = float(time)

    if current_pitch is not None and len(times):
        flush(float(times[-1]))
    return notes
