from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
STUDENTS_FILE = DATA_DIR / "students.json"
ADMINS_FILE = DATA_DIR / "admins.json"

__all__ = ["BASE_DIR", "DATA_DIR", "IMAGES_DIR", "STUDENTS_FILE", "ADMINS_FILE"]

