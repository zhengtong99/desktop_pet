"""Frame-by-frame poke animations for the pet.

Each animation is a generator that yields a *transform* dict every frame. The
pet window advances the active generator on a timer and applies the transform
when painting. Supported transform keys (all optional):

    off_x / off_y : pixel offset from the resting position
    scale_x / scale_y : horizontal / vertical scaling (1.0 = normal)

When a generator is exhausted the pet snaps back to rest.
"""
from __future__ import annotations

import math
from collections.abc import Iterator

Transform = dict[str, float]

_FPS = 60.0


def jump(duration: float = 0.55, height: float = 45.0) -> Iterator[Transform]:
    """A light hop up and back down."""
    frames = max(1, int(duration * _FPS))
    for i in range(frames):
        t = i / frames
        off = -math.sin(t * math.pi) * height
        # A tiny stretch on the way up feels bouncier.
        stretch = 1.0 + 0.06 * math.sin(t * math.pi)
        yield {"off_y": off, "scale_x": 2.0 - stretch, "scale_y": stretch}


def squash(duration: float = 0.45, amount: float = 0.22) -> Iterator[Transform]:
    """Squash down then rebound past normal before settling."""
    frames = max(1, int(duration * _FPS))
    for i in range(frames):
        t = i / frames
        # Damped bounce: strong squash first, then a smaller overshoot.
        wave = math.sin(t * math.pi * 1.5) * (1.0 - t)
        yield {
            "scale_x": 1.0 + amount * wave,
            "scale_y": 1.0 - amount * wave,
            "off_y": amount * wave * 8.0,
        }


def shake(duration: float = 0.5, amplitude: float = 14.0) -> Iterator[Transform]:
    """Quick left-right wobble that fades out."""
    frames = max(1, int(duration * _FPS))
    for i in range(frames):
        t = i / frames
        off = math.sin(t * math.pi * 8.0) * amplitude * (1.0 - t)
        yield {"off_x": off}


def spin_wobble(duration: float = 0.5, amount: float = 0.18) -> Iterator[Transform]:
    """A cute breathing / wobble squeeze."""
    frames = max(1, int(duration * _FPS))
    for i in range(frames):
        t = i / frames
        wave = math.sin(t * math.pi * 2.0) * (1.0 - t)
        yield {"scale_x": 1.0 - amount * wave, "scale_y": 1.0 + amount * wave}


# Cycled in order each time the pet is poked.
SEQUENCE = [jump, squash, shake, spin_wobble]
