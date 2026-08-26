"""Full-screen festive overlays: fireworks, falling snow, hearts, emoji, etc.

The overlay is a transparent, click-through, always-on-top window that plays a
short particle animation and then closes itself. Two particle styles are used:

  * "spark"  - small colored dots with gravity (used for fireworks)
  * "emoji"  - a drifting, spinning emoji glyph (snow, hearts, lanterns, ...)
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QWidget

_FIREWORK_COLORS = [
    QColor(255, 99, 132), QColor(255, 205, 86), QColor(75, 192, 192),
    QColor(153, 102, 255), QColor(255, 159, 64), QColor(120, 220, 120),
    QColor(255, 255, 255),
]


@dataclass
class _Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float          # remaining life in seconds
    max_life: float
    kind: str            # "spark" | "emoji" | "rocket"
    color: QColor = field(default_factory=lambda: QColor(255, 255, 255))
    emoji: str = ""
    size: float = 16.0
    angle: float = 0.0
    spin: float = 0.0
    target_y: float = 0.0  # for rockets: explode when reached


class CelebrationOverlay(QWidget):
    _GRAVITY = 320.0  # px/s^2

    def __init__(self, screen_geometry: QRect, theme: str,
                 emojis: list[str], duration_ms: int = 7000) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setGeometry(screen_geometry)

        self._theme = theme
        self._emojis = emojis or ["✨"]
        self._particles: list[_Particle] = []
        self._elapsed = 0.0
        self._duration = duration_ms / 1000.0
        self._spawn_accum = 0.0

        self._dt = 1 / 60.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        self.show()
        self._timer.start(int(self._dt * 1000))

    # -- simulation --------------------------------------------------------

    def _tick(self) -> None:
        self._elapsed += self._dt
        self._spawn(self._dt)
        self._advance(self._dt)
        # Stop spawning near the end, then close once particles clear.
        if self._elapsed >= self._duration and not self._particles:
            self._timer.stop()
            self.close()
            return
        self.update()

    def _spawn(self, dt: float) -> None:
        if self._elapsed >= self._duration:
            return
        self._spawn_accum += dt
        if self._theme == "fireworks":
            # Launch a rocket roughly a few times per second.
            if self._spawn_accum >= random.uniform(0.35, 0.7):
                self._spawn_accum = 0.0
                self._launch_rocket()
        else:
            # Steady stream of falling emoji.
            if self._spawn_accum >= 0.18:
                self._spawn_accum = 0.0
                for _ in range(random.randint(1, 2)):
                    self._spawn_emoji()

    def _launch_rocket(self) -> None:
        w = self.width()
        x = random.uniform(w * 0.15, w * 0.85)
        target = random.uniform(self.height() * 0.15, self.height() * 0.45)
        self._particles.append(_Particle(
            x=x, y=self.height(), vx=random.uniform(-20, 20), vy=-random.uniform(430, 520),
            life=3.0, max_life=3.0, kind="rocket",
            color=random.choice(_FIREWORK_COLORS), size=4.0, target_y=target,
        ))

    def _explode(self, p: _Particle) -> None:
        count = random.randint(28, 44)
        base = random.choice(_FIREWORK_COLORS)
        speed = random.uniform(120, 190)
        for i in range(count):
            ang = (2 * math.pi) * (i / count) + random.uniform(-0.1, 0.1)
            spd = speed * random.uniform(0.5, 1.0)
            self._particles.append(_Particle(
                x=p.x, y=p.y,
                vx=math.cos(ang) * spd, vy=math.sin(ang) * spd,
                life=random.uniform(0.9, 1.5), max_life=1.5, kind="spark",
                color=base if random.random() < 0.7 else random.choice(_FIREWORK_COLORS),
                size=random.uniform(2.5, 4.5),
            ))

    def _spawn_emoji(self) -> None:
        x = random.uniform(0, self.width())
        self._particles.append(_Particle(
            x=x, y=-30, vx=random.uniform(-25, 25), vy=random.uniform(60, 140),
            life=12.0, max_life=12.0, kind="emoji",
            emoji=random.choice(self._emojis),
            size=random.uniform(22, 40),
            angle=random.uniform(0, 360), spin=random.uniform(-60, 60),
        ))

    def _advance(self, dt: float) -> None:
        alive: list[_Particle] = []
        for p in self._particles:
            if p.kind == "rocket":
                p.vy += self._GRAVITY * dt * 0.15
                p.x += p.vx * dt
                p.y += p.vy * dt
                if p.y <= p.target_y or p.vy >= 0:
                    self._explode(p)
                    continue
                alive.append(p)
            elif p.kind == "spark":
                p.vy += self._GRAVITY * dt
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.life -= dt
                if p.life > 0:
                    alive.append(p)
            else:  # emoji
                # gentle horizontal sway
                p.vx += math.sin(self._elapsed * 2 + p.x) * 6 * dt
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.angle += p.spin * dt
                if p.y < self.height() + 40:
                    alive.append(p)
        self._particles = alive

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        emoji_font = QFont()

        for p in self._particles:
            if p.kind == "emoji":
                emoji_font.setPointSizeF(p.size)
                painter.setFont(emoji_font)
                painter.save()
                painter.translate(p.x, p.y)
                painter.rotate(p.angle)
                painter.setPen(QColor(0, 0, 0, 255))
                painter.drawText(int(-p.size), int(p.size / 2), p.emoji)
                painter.restore()
            else:  # spark / rocket
                color = QColor(p.color)
                if p.kind == "spark":
                    color.setAlphaF(max(0.0, min(1.0, p.life / p.max_life)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(color)
                r = p.size
                painter.drawEllipse(int(p.x - r), int(p.y - r), int(r * 2), int(r * 2))
