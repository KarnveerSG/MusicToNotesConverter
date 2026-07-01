from __future__ import annotations

from pathlib import Path

from mtnc.models import NoteEvent, SubtitleCue


def cues_to_srt(cues: list[SubtitleCue]) -> str:
    lines: list[str] = []
    for cue in cues:
        lines.append(str(cue.index))
        lines.append(f"{_ts(cue.start)} --> {_ts(cue.end)}")
        lines.append(cue.text)
        lines.append("")
    return "\n".join(lines)


def cues_to_vtt(cues: list[SubtitleCue]) -> str:
    lines = ["WEBVTT", ""]
    for cue in cues:
        lines.append(f"{_ts(cue.start, vtt=True)} --> {_ts(cue.end, vtt=True)}")
        lines.append(cue.text)
        lines.append("")
    return "\n".join(lines)


def cues_to_plain(cues: list[SubtitleCue]) -> str:
    return "\n".join(c.text for c in cues)


def _ts(seconds: float, vtt: bool = False) -> str:
    ms = int(round((seconds % 1) * 1000))
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if vtt:
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_midi_copy(source: Path, destination: Path) -> None:
    destination.write_bytes(source.read_bytes())


def notes_to_midi_file(
    notes: list[NoteEvent],
    destination: Path,
    tempo: int = 120,
    program: int = 0,
) -> None:
    import pretty_midi

    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    piano = pretty_midi.Instrument(program=program)
    for note in notes:
        piano.notes.append(
            pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start,
                end=max(note.end, note.start + 0.05),
            )
        )
    midi.instruments.append(piano)
    midi.write(str(destination))
