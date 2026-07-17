"""Load config.yaml and .env; expose project-wide settings and paths."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

with open(PROJECT_ROOT / "config.yaml", encoding="utf-8") as f:
    CFG: dict = yaml.safe_load(f)

LANGUAGES: dict[str, str] = CFG["languages"]
DOMAINS: list[str] = CFG["domains"]
CATEGORIES: list[str] = CFG["hallucination_categories"]


def path(key: str) -> Path:
    """Resolve a path from config.yaml `paths`, creating the directory."""
    p = PROJECT_ROOT / CFG["paths"][key]
    if not p.suffix:  # directories only
        p.mkdir(parents=True, exist_ok=True)
    return p


def api_key(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"{name} not set — add it to .env (see .env.example)")
    return val
