from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict

def _settings_path() -> str:
    base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "JARVIZ")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "settings.json")

@dataclass
class AppSettings:
    accent: str = "#3aa3ff"
    start_maximized: bool = False
    tesseract_path: str = ""

def load_settings() -> AppSettings:
    path = _settings_path()
    if not os.path.exists(path):
        return AppSettings()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        default = AppSettings()
        return AppSettings(
            accent=data.get("accent", default.accent),
            start_maximized=bool(data.get("start_maximized", default.start_maximized)),
        )
    except Exception:
        return AppSettings()

def save_settings(s: AppSettings) -> None:
    path = _settings_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(s), f, indent=2)
