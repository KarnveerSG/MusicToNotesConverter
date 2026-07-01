from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from mtnc.audio.loader import load_audio, write_normalized_wav
from mtnc.models import ProcessingResult, SubtitleCue


class PipelineWorker(QThread):
    stage_started = Signal(str)
    stage_finished = Signal(str)
    progress = Signal(str, int)
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        audio_path: Path,
        whisper_model: str = "base",
        min_note: int = 36,
        max_note: int = 96,
        midi_program: int = 0,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.audio_path = audio_path
        self.whisper_model = whisper_model
        self.min_note = min_note
        self.max_note = max_note
        self.midi_program = midi_program
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        try:
            result = ProcessingResult(source_path=self.audio_path)
            self.stage_started.emit("Loading audio")
            self.progress.emit("Loading audio", 5)
            audio = load_audio(self.audio_path)
            result.normalized_wav = write_normalized_wav(audio)
            if self._cancelled:
                return
            self.stage_finished.emit("Loading audio")

            self.stage_started.emit("Transcribing speech")
            self.progress.emit("Transcribing speech", 20)
            cues, language = _transcribe(result.normalized_wav, self.whisper_model, self._cancel_check)
            result.cues = cues
            result.language = language
            if self._cancelled:
                return
            self.stage_finished.emit("Transcribing speech")

            self.stage_started.emit("Detecting pitch")
            self.progress.emit("Detecting pitch", 60)
            notes, midi_path = _detect_pitch(
                result.normalized_wav,
                self.min_note,
                self.max_note,
                self.midi_program,
            )
            result.notes = notes
            result.midi_path = midi_path
            if self._cancelled:
                return
            self.stage_finished.emit("Detecting pitch")

            self.progress.emit("Done", 100)
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _cancel_check(self) -> bool:
        return self._cancelled


def _transcribe(
    wav_path: Path,
    model_size: str,
    cancel_check,
) -> tuple[list[SubtitleCue], str | None]:
    from faster_whisper import WhisperModel

    from mtnc.paths import models_dir

    model = WhisperModel(model_size, device="cpu", compute_type="int8", download_root=str(models_dir()))
    segments, info = model.transcribe(
        str(wav_path),
        word_timestamps=True,
        vad_filter=True,
    )
    cues: list[SubtitleCue] = []
    index = 1
    language = info.language
    for segment in segments:
        if cancel_check():
            break
        text = segment.text.strip()
        if not text:
            continue
        cues.append(
            SubtitleCue(
                index=index,
                start=float(segment.start),
                end=float(segment.end),
                text=text,
            )
        )
        index += 1
    return cues, language


def _detect_pitch(
    wav_path: Path,
    min_note: int,
    max_note: int,
    midi_program: int,
) -> tuple[list[NoteEvent], Path]:
    from mtnc.models import NoteEvent
    from mtnc.pipeline.pitch_detection import detect_notes

    return detect_notes(wav_path, min_note, max_note, midi_program)
