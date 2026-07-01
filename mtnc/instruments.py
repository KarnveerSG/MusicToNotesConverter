from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    id: str
    name: str
    midi_program: int
    min_midi: int
    max_midi: int
    clef: str  # "treble" | "bass"


INSTRUMENTS: dict[str, Instrument] = {
    "piano": Instrument("piano", "Piano", 0, 21, 108, "treble"),
    "guitar": Instrument("guitar", "Guitar", 24, 40, 88, "treble"),
    "violin": Instrument("violin", "Violin", 40, 55, 103, "treble"),
}

DEFAULT_INSTRUMENT = "piano"


def get_instrument(instrument_id: str) -> Instrument:
    return INSTRUMENTS.get(instrument_id, INSTRUMENTS[DEFAULT_INSTRUMENT])
