from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic_settings import BaseSettings


def _find_config_file() -> Optional[Path]:
    candidates = [
        Path(os.environ.get("ARCLOCK_CONFIG", "")),
        Path("config/arclock.yaml"),
        Path(__file__).resolve().parents[2] / "config" / "arclock.yaml",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _resolve_config_path() -> Path:
    """Return the path to write config to. Uses existing file location or a sensible default."""
    existing = _find_config_file()
    if existing:
        return existing
    env = os.environ.get("ARCLOCK_CONFIG", "")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "config" / "arclock.yaml"


class Settings(BaseSettings):
    de_callsign: str = ""
    de_grid: str = ""
    de_latitude: float = 0.0
    de_longitude: float = 0.0
    de_timezone: str = "UTC"
    map_style: str = "dark-matter"

    # Data refresh intervals in seconds
    sfi_interval: int = 900
    kp_interval: int = 300
    xray_interval: int = 60
    ssn_interval: int = 3600
    greyline_interval: int = 60

    model_config = {"env_prefix": "ARCLOCK_"}


def load_settings() -> Settings:
    cfg_path = _find_config_file()
    overrides: dict = {}
    if cfg_path:
        with open(cfg_path) as f:
            overrides = yaml.safe_load(f) or {}
    return Settings(**overrides)


settings = load_settings()
config_path = _resolve_config_path()
