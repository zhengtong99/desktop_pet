"""Fetch local weather by IP and format a playful bilingual report.

Uses only free, key-less web services:
  * ip-api.com          -> approximate location from the user's IP address
  * open-meteo.com      -> current weather + daily high/low

All network work happens on a background thread (:class:`WeatherWorker`) so the
pet never freezes. If anything fails (offline, blocked, etc.) the pet simply
stays quiet about the weather.
"""
from __future__ import annotations

import random

import requests
from PySide6.QtCore import QObject, QThread, Signal

# Countries that conventionally use Fahrenheit.
_FAHRENHEIT = {"US", "BS", "BZ", "KY", "PW", "FM", "MH"}

_TIMEOUT = 8  # seconds per request

# WMO weather code -> (Chinese description, English description, emoji).
_WEATHER_CODES: dict[int, tuple[str, str, str]] = {
    0: ("大晴天", "clear sky", "☀️"),
    1: ("晴", "mostly clear", "🌤️"),
    2: ("多云", "partly cloudy", "⛅"),
    3: ("阴天", "overcast", "☁️"),
    45: ("有雾", "foggy", "🌫️"),
    48: ("雾凇", "rime fog", "🌫️"),
    51: ("毛毛雨", "light drizzle", "🌦️"),
    53: ("小雨", "drizzle", "🌦️"),
    55: ("密集毛毛雨", "dense drizzle", "🌧️"),
    56: ("冻毛毛雨", "freezing drizzle", "🌧️"),
    57: ("冻毛毛雨", "freezing drizzle", "🌧️"),
    61: ("小雨", "light rain", "🌦️"),
    63: ("中雨", "rain", "🌧️"),
    65: ("大雨", "heavy rain", "🌧️"),
    66: ("冻雨", "freezing rain", "🌧️"),
    67: ("冻雨", "freezing rain", "🌧️"),
    71: ("小雪", "light snow", "🌨️"),
    73: ("中雪", "snow", "❄️"),
    75: ("大雪", "heavy snow", "❄️"),
    77: ("雪粒", "snow grains", "❄️"),
    80: ("阵雨", "rain showers", "🌦️"),
    81: ("阵雨", "rain showers", "🌧️"),
    82: ("强阵雨", "violent showers", "⛈️"),
    85: ("阵雪", "snow showers", "🌨️"),
    86: ("强阵雪", "heavy snow showers", "❄️"),
    95: ("雷阵雨", "thunderstorm", "⛈️"),
    96: ("雷暴伴冰雹", "thunderstorm w/ hail", "⛈️"),
    99: ("强雷暴冰雹", "severe hailstorm", "⛈️"),
}


def _describe_code(code: int) -> tuple[str, str, str]:
    return _WEATHER_CODES.get(code, ("神秘天气", "mysterious weather", "🌈"))


def _get_location() -> dict:
    resp = requests.get(
        "http://ip-api.com/json/"
        "?fields=status,country,countryCode,city,lat,lon",
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        raise RuntimeError("location lookup failed")
    return data


def _get_weather(lat: float, lon: float, fahrenheit: bool) -> dict:
    unit = "fahrenheit" if fahrenheit else "celsius"
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min",
            "temperature_unit": unit,
            "timezone": "auto",
            "forecast_days": 1,
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _fun_comment(code: int, high: float, unit: str) -> str:
    """A playful bilingual tip based on conditions."""
    if code in (0, 1):
        base = ["记得防晒哦～ Don't forget sunscreen!",
                "适合出去走走！ Great day for a walk!"]
    elif code in (2, 3, 45, 48):
        base = ["云朵软软的 The clouds look cozy~",
                "光线柔和，拍照正好 Soft light, perfect for photos!"]
    elif code in (95, 96, 99):
        base = ["打雷啦，待在室内更安全 Stay cozy indoors! ⛈️"]
    elif 71 <= code <= 86:
        base = ["下雪啦，注意保暖！ Bundle up, it's snowy! ❄️",
                "小心路滑哦 Careful, it's slippery!"]
    elif 51 <= code <= 82:
        base = ["记得带伞哦☔ Grab an umbrella!",
                "雨天记得穿防滑鞋 Watch your step in the rain!"]
    else:
        base = ["照顾好自己哦 Take care out there!"]

    if high >= (100 if unit == "°F" else 35):
        base.append(f"今日最高 {high:.0f}{unit}，注意避暑防晒！ Stay cool!")
    elif high <= (32 if unit == "°F" else 0):
        base.append(f"今日最高才 {high:.0f}{unit}，多穿点！ Bundle up warm!")
    return random.choice(base)


def build_report() -> str:
    """Fetch data and return a ready-to-show bilingual weather report.

    The report contains Chinese and English condition descriptions, bilingual
    temperature labels, and a bilingual weather tip.
    """
    loc = _get_location()
    fahrenheit = loc.get("countryCode") in _FAHRENHEIT
    unit = "°F" if fahrenheit else "°C"

    data = _get_weather(loc["lat"], loc["lon"], fahrenheit)
    current = data.get("current", {})
    daily = data.get("daily", {})

    code = int(current.get("weather_code", 0))
    temp = float(current.get("temperature_2m", 0.0))
    highs = daily.get("temperature_2m_max") or [temp]
    lows = daily.get("temperature_2m_min") or [temp]
    high, low = float(highs[0]), float(lows[0])

    zh, en, emoji = _describe_code(code)
    city = loc.get("city") or "你所在的地方"
    comment = _fun_comment(code, high, unit)

    return (
        f"{emoji} {city}今天是{zh}哦！ It's {en} in {city}!\n"
        f"现在Now {temp:.0f}{unit}，最高High {high:.0f}{unit} / "
        f"最低Low {low:.0f}{unit}。\n"
        f"{comment}"
    )


class WeatherWorker(QObject):
    """Build a weather report in a background thread and emit its result."""

    ready = Signal(str)
    failed = Signal(str)

    def run(self) -> None:
        try:
            report = build_report()
        except Exception as exc:  # noqa: BLE001 - network is best-effort
            self.failed.emit(str(exc))
            return
        self.ready.emit(report)


def fetch_weather_async(parent: QObject, on_ready, on_failed=None) -> QThread:
    """Start a weather fetch on a worker thread.

    Returns the running :class:`QThread`; keep a reference so it isn't garbage
    collected before it finishes.
    """
    thread = QThread(parent)
    worker = WeatherWorker()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.ready.connect(on_ready)
    if on_failed is not None:
        worker.failed.connect(on_failed)
    # Clean up once done.
    worker.ready.connect(thread.quit)
    worker.failed.connect(thread.quit)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    # Keep the worker alive for the thread's lifetime.
    thread._worker = worker  # type: ignore[attr-defined]
    thread.start()
    return thread
