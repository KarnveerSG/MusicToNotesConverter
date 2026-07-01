from __future__ import annotations

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def midi_to_name(pitch: int) -> str:
    octave = pitch // 12 - 1
    return f"{NOTE_NAMES[pitch % 12]}{octave}"


def midi_to_staff_y(pitch: int, middle_line_midi: int = 71) -> float:
    """Steps from middle staff line (B4 treble). Positive = higher on staff."""
    return pitch - middle_line_midi


# QWERTY piano mapping (two octaves, octave 4 base)
KEYBOARD_MAP: dict[str, int] = {
    "Z": 48,
    "S": 49,
    "X": 50,
    "D": 51,
    "C": 52,
    "V": 53,
    "G": 54,
    "B": 55,
    "H": 56,
    "N": 57,
    "J": 58,
    "M": 59,
    ",": 60,
    "L": 61,
    ".": 62,
    ";": 63,
    "/": 64,
    "Q": 72,
    "2": 73,
    "W": 74,
    "3": 75,
    "E": 76,
    "R": 77,
    "5": 78,
    "T": 79,
    "6": 80,
    "Y": 81,
    "7": 82,
    "U": 83,
    "I": 84,
    "9": 85,
    "O": 86,
    "0": 87,
    "P": 88,
}


def keyboard_pitch_for_key(key: str, octave_offset: int = 0) -> int | None:
    base = KEYBOARD_MAP.get(key.upper())
    if base is None:
        return None
    return base + octave_offset * 12
