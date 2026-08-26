"""Load the bundled cute cartoon font and expose its family name.

The font (ZCOOL KuaiLe / \u7ad9\u9177\u5feb\u4e50\u4f53) covers both Chinese and English, so the pet
looks the same playful way on every machine, even without it installed.
"""
from __future__ import annotations

from PySide6.QtGui import QFontDatabase

from . import assets

_family: str | None = None


def cute_font_family() -> str:
    """Register the bundled font(s) once and return the cute family name.

    Falls back to an empty string (Qt default) if the font can't be loaded.
    """
    global _family
    if _family is not None:
        return _family

    loaded: list[str] = []
    for path in assets.list_fonts():
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id != -1:
            loaded.extend(QFontDatabase.applicationFontFamilies(font_id))

    # Prefer the ZCOOL KuaiLe family if present.
    for fam in loaded:
        if "ZCOOL" in fam or "\u5feb\u4e50" in fam:
            _family = fam
            return _family

    _family = loaded[0] if loaded else ""
    return _family
