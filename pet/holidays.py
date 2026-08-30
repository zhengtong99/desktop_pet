"""Detect festivals (Chinese + Western) and describe how to celebrate them.

Each festival maps to a *theme* understood by the celebration overlay, plus a
short bilingual greeting and a set of emoji used for the falling-object effect.
Chinese festivals are computed from the lunar calendar via ``lunardate``.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Holiday:
    key: str                       # stable id
    name: str                      # bilingual display name
    theme: str                     # celebration effect: fireworks/snow/...
    greeting: str                  # bilingual greeting shown in a bubble
    emojis: list[str] = field(default_factory=list)


# --- Lunar helpers ---------------------------------------------------------

def _lunar_to_solar(greg_year: int, month: int, day: int) -> _dt.date | None:
    """Solar date of a given lunar month/day for ``greg_year`` (or None)."""
    try:
        from lunardate import LunarDate

        return LunarDate(greg_year, month, day).toSolarDate()
    except Exception:
        return None


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> _dt.date:
    """The n-th ``weekday`` (Mon=0) of ``month`` in ``year``."""
    first = _dt.date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + _dt.timedelta(days=offset + 7 * (n - 1))


def _easter(year: int) -> _dt.date:
    """Gregorian Easter Sunday (anonymous computus algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month, day = divmod(h + m - 7 * n + 114, 31)
    return _dt.date(year, month, day + 1)


# --- Holiday configurations ------------------------------------------------

# Fixed-date holidays (month, day) -> Holiday
_FIXED_HOLIDAYS: dict[tuple[int, int], Holiday] = {
    (1, 1): Holiday("new_year", "元旦 / New Year's Day", "fireworks",
                    "新年快乐！🎆 Happy New Year!",
                    ["🎆", "🎇", "🥂", "✨"]),
    (2, 14): Holiday("valentine", "情人节 / Valentine's Day", "hearts",
                     "情人节快乐 💝 Happy Valentine's Day!",
                     ["❤️", "💕", "🌹", "💝"]),
    (10, 31): Holiday("halloween", "万圣节 / Halloween", "spooky",
                      "万圣节快乐！🎃 Trick or treat!",
                      ["🎃", "👻", "🦇", "🕸️"]),
    (12, 24): Holiday("christmas_eve", "平安夜 / Christmas Eve", "snow",
                      "平安夜快乐 🎄 Merry Christmas Eve!",
                      ["🎄", "❄️", "🎁", "⭐"]),
    (12, 25): Holiday("christmas", "圣诞节 / Christmas", "snow",
                      "圣诞快乐！🎄 Merry Christmas!",
                      ["🎄", "🎅", "❄️", "🎁", "⭐"]),
}

# Lunar holidays (lunar_month, lunar_day) -> Holiday
_LUNAR_HOLIDAYS: dict[tuple[int, int], Holiday] = {
    (1, 15): Holiday("lantern", "元宵节 / Lantern Festival", "lanterns",
                     "元宵节快乐，团团圆圆！🏮 Happy Lantern Festival!",
                     ["🏮", "🥮", "✨"]),
    (5, 5): Holiday("dragon_boat", "端午节 / Dragon Boat Festival", "confetti",
                    "端午安康！🐉 Happy Dragon Boat Festival!",
                    ["🥟", "🐉", "🎏"]),
    (7, 7): Holiday("qixi", "七夕 / Qixi Festival", "hearts",
                    "七夕快乐～ 愿有情人终成眷属 💕",
                    ["💕", "🌹", "✨"]),
    (8, 15): Holiday("mid_autumn", "中秋节 / Mid-Autumn Festival", "moon",
                     "中秋快乐，月圆人团圆！🌕 Happy Mid-Autumn!",
                     ["🌕", "🥮", "🐇", "✨"]),
}

# Spring Festival (Lunar New Year) special handling (extends beyond lunar day)
_SPRING_FESTIVAL = Holiday(
    "spring_festival",
    "春节 / Chinese New Year",
    "fireworks",
    "新年快乐，恭喜发财！🧨 Happy Lunar New Year!",
    ["🧧", "🧨", "🎆", "🏮", "✨"],
)

# Birthday (fixed dates)
_BIRTHDAY = Holiday(
    "birthday",
    "生日快乐 / Happy Birthday",
    "cake",
    "生日快乐！🎂 Happy Birthday to you!",
    ["🎂", "🎉", "🎈", "🍰", "✨"],
)

# Thanksgiving (4th Thursday of November)
_THANKSGIVING = Holiday(
    "thanksgiving",
    "感恩节 / Thanksgiving",
    "confetti",
    "感恩节快乐！🦃 Happy Thanksgiving!",
    ["🦃", "🍁", "🥧"],
)

# Easter (computed Gregorian date)
_EASTER = Holiday(
    "easter",
    "复活节 / Easter",
    "confetti",
    "复活节快乐！🐰 Happy Easter!",
    ["🐰", "🥚", "🌷"],
)


# --- Public API ------------------------------------------------------------

def active_holiday(today: _dt.date) -> Holiday | None:
    """Return the festival active on ``today``, or None.

    Birthday celebrations are fixed to 11/17 and 2/27.
    """
    y = today.year
    md = (today.month, today.day)

    # Priority 1: Fixed birthday dates (11/17, 2/27).
    if md in {(11, 17), (2, 27)}:
        return _BIRTHDAY

    # Priority 2: Spring Festival (extends 2-3 days from lunar 1/1).
    spring = _lunar_to_solar(y, 1, 1)
    if spring and (spring - _dt.timedelta(days=1)) <= today <= (
        spring + _dt.timedelta(days=2)
    ):
        return _SPRING_FESTIVAL

    # Priority 3: Lunar holidays (exact lunar date match).
    for (lm, ld), holiday in _LUNAR_HOLIDAYS.items():
        solar = _lunar_to_solar(y, lm, ld)
        if solar and solar == today:
            return holiday

    # Priority 4: Fixed-date Western holidays.
    if md in _FIXED_HOLIDAYS:
        return _FIXED_HOLIDAYS[md]

    # Priority 5: Computed Western dates (Thanksgiving, Easter).
    if today == _nth_weekday(y, 11, 3, 4):  # 4th Thursday of November
        return _THANKSGIVING
    if today == _easter(y):
        return _EASTER

    return None
