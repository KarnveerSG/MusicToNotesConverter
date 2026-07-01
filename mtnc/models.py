from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SubtitleCue:
    index: int
    start: float
    end: float
    text: str


@dataclass
class NoteEvent:
    start: float
    end: float
    pitch: int
    velocity: int = 80


@dataclass
class AudioMetadata:
    path: Path
    duration: float
    sample_rate: int
    channels: int
    samples: object  # np.ndarray


@dataclass
class ProcessingResult:
    source_path: Path
    normalized_wav: Path | None = None
    cues: list[SubtitleCue] = field(default_factory=list)
    notes: list[NoteEvent] = field(default_factory=list)
    midi_path: Path | None = None
    language: str | None = None
