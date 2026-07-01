from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields

from mtnc.paths import migrate_legacy_settings, settings_path


@dataclass
class AppSettings:
    instrument_id: str = "piano"
    whisper_model: str = "base"
    auto_process: bool = True
    keyboard_enabled: bool = True
    keyboard_octave: int = 4
    soundfont_path: str | None = None
    accent_color: str = "#7c9cff"

    @classmethod
    def config_path(cls):
        migrate_legacy_settings()
        return settings_path()

    def save(self) -> None:
        self.config_path().write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> AppSettings:
        path = cls.config_path()
        if not path.is_file():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            known = {f.name for f in fields(cls)}
            return cls(**{k: v for k, v in data.items() if k in known})
        except (json.JSONDecodeError, TypeError):
            return cls()
