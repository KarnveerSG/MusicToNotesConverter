from __future__ import annotations

from pathlib import Path

import numpy as np


def render_midi_to_wav(midi_path: Path, output_path: Path, soundfont_path: Path | None = None) -> None:
    import pretty_midi

    midi = pretty_midi.PrettyMIDI(str(midi_path))
    sf_path = _resolve_soundfont(soundfont_path)
    audio = midi.fluidsynth(fs=44100, sf2_path=str(sf_path) if sf_path else None)
    if audio.size == 0:
        raise RuntimeError("MIDI render produced empty audio")
    _write_wav(output_path, audio, 44100)


def _resolve_soundfont(explicit: Path | None) -> Path | None:
    if explicit and explicit.is_file():
        return explicit
    candidates = [
        Path.home() / "soundfonts" / "GeneralUser GS.sf2",
        Path("C:/soundfonts/GeneralUser GS.sf2"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    import soundfile as sf

    peak = np.max(np.abs(audio)) or 1.0
    normalized = (audio / peak * 0.95).astype(np.float32)
    sf.write(str(path), normalized, sample_rate)
