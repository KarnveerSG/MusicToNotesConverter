from __future__ import annotations

import os
import shutil
from pathlib import Path

APP_NAME = "MusicToNotes"


def app_data_dir() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def cache_dir() -> Path:
    path = app_data_dir() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def temp_dir() -> Path:
    path = app_data_dir() / "temp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def models_dir() -> Path:
    path = app_data_dir() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings_path() -> Path:
    return app_data_dir() / "settings.json"


def temp_file(name: str) -> Path:
    return temp_dir() / name


def migrate_legacy_settings() -> None:
    legacy = Path.home() / ".mtnc" / "settings.json"
    target = settings_path()
    if legacy.is_file() and not target.is_file():
        shutil.copy2(legacy, target)
