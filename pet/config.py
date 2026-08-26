"""User settings that persist between runs.

Settings are stored as JSON in a per-user folder so they survive updates and
never require the user to edit anything by hand.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _config_dir() -> Path:
    """Return a writable per-user config folder, created if needed."""
    if os.name == "nt":  # Windows
        base = os.environ.get("APPDATA") or str(Path.home())
        path = Path(base) / "DesktopPet"
    else:  # macOS / Linux
        path = Path.home() / ".config" / "desktop_pet"
    path.mkdir(parents=True, exist_ok=True)
    return path


CONFIG_PATH = _config_dir() / "settings.json"

DEFAULTS: dict[str, Any] = {
    "scale": 0.12,           # pet size as a fraction of the source image
    "always_on_top": True,
    "pos_x": None,           # last window position (None -> auto place)
    "pos_y": None,
    "pet_name": "",          # currently shown cut-out (by file name)
    "daily_date": "",        # date the daily pet was chosen (YYYY-MM-DD)
    "weather_on_start": True,
    "greeting_on_start": True,
}


class Config:
    """Small JSON-backed settings store with attribute-style access."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
                stored = json.load(handle)
            if isinstance(stored, dict):
                self._data.update({k: stored[k] for k in stored if k in DEFAULTS})
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            # Missing or corrupt config: fall back to defaults silently.
            pass

    def save(self) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
                json.dump(self._data, handle, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()
