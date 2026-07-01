from __future__ import annotations

import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from mtnc.models import AudioMetadata


def load_audio(path: Path, target_sr: int = 22050) -> AudioMetadata:
    samples, sr = librosa.load(str(path), sr=target_sr, mono=True)
    samples = librosa.util.normalize(samples)
    duration = float(len(samples) / sr)
    return AudioMetadata(
        path=path,
        duration=duration,
        sample_rate=sr,
        channels=1,
        samples=samples,
    )


def write_normalized_wav(audio: AudioMetadata) -> Path:
    out = Path(tempfile.gettempdir()) / f"mtnc_{audio.path.stem}_norm.wav"
    sf.write(str(out), audio.samples, audio.sample_rate)
    return out


def downsample_for_display(samples: np.ndarray, max_points: int = 8000) -> tuple[np.ndarray, np.ndarray]:
    n = len(samples)
    if n <= max_points:
        times = np.linspace(0, 1, n)
        return times, samples
    step = max(1, n // max_points)
    chunk = samples[: n - (n % step)].reshape(-1, step)
    envelope = np.max(np.abs(chunk), axis=1)
    times = np.linspace(0, 1, len(envelope))
    return times, envelope
