"""Locate the transparent pet images, whether running from source or bundled.

When packaged with PyInstaller the assets live next to the executable in a
temporary folder exposed as ``sys._MEIPASS``. When running from source they live
in ``<project>/assets/pets``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_IMAGE_SUFFIXES = {".png"}


def _base_dir() -> Path:
    bundled = getattr(sys, "_MEIPASS", None)
    if bundled:
        return Path(bundled)
    # pet/assets.py -> project root is one level up from the package.
    return Path(__file__).resolve().parent.parent


def pets_dir() -> Path:
    return _base_dir() / "assets" / "pets"


def fonts_dir() -> Path:
    return _base_dir() / "assets" / "fonts"


def list_fonts() -> list[Path]:
    """Return every bundled font file."""
    folder = fonts_dir()
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in {".ttf", ".otf"}
    )


def list_pets() -> list[Path]:
    """Return every transparent pet PNG, sorted by name."""
    folder = pets_dir()
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES
    )
