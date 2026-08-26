"""Cute one-liners the pet says in its speech bubble.

Each entry has a Chinese and an English version; the pet shows one *or* the
other at random (not both at once).
"""
from __future__ import annotations

import random

# (Chinese, English) pairs.
CHITCHAT: list[tuple[str, str]] = [
    ("加油哦！", "You got this!"),
    ("么么哒 💕", "Love you!"),
    ("祝你开心！", "Have a great day!"),
    ("记得喝水哦～", "Stay hydrated!"),
    ("你今天超棒的！", "You're amazing!"),
    ("休息一下吧～", "Take a little break!"),
    ("抱抱你～", "Sending you a hug!"),
    ("别忘了微笑 😊", "Keep smiling!"),
    ("我一直陪着你", "I'm always here!"),
    ("深呼吸～", "Breathe, relax."),
    ("你值得所有的好", "You deserve the best!"),
    ("累了就靠一会儿吧", "Lean on me anytime."),
    ("今天也要元气满满！", "Stay energized!"),
    ("慢慢来，不着急", "One step at a time."),
    ("你笑起来最好看", "Your smile is the best!"),
    ("摸摸头，乖～", "There, there. 🥰"),
    ("工作再忙也要吃饭哦", "Don't skip meals!"),
    ("想你了", "Thinking of you 💭"),
    ("冲鸭！", "Let's gooo! 🚀"),
    ("眼睛累了看看远方", "Rest your eyes~"),
]

# (Chinese, English) pairs used when the pet is poked / clicked.
POKE: list[tuple[str, str]] = [
    ("哎呀～", "Hey! 😆"),
    ("痒痒的啦", "That tickles!"),
    ("再戳我就跳给你看", "Do it again! 😜"),
    ("在呢在呢", "I'm here!"),
    ("嘿嘿～", "Hehe!"),
    ("戳一下少一下哦", "Careful now~"),
]


_last: dict[int, str] = {}


def _pick(pairs: list[tuple[str, str]]) -> str:
    """Pick a random line (Chinese or English), avoiding the last one shown."""
    key = id(pairs)
    previous = _last.get(key)
    choice = random.choice(random.choice(pairs))
    for _ in range(4):
        if choice != previous:
            break
        choice = random.choice(random.choice(pairs))
    _last[key] = choice
    return choice


def random_chitchat() -> str:
    return _pick(CHITCHAT)


def random_poke() -> str:
    return _pick(POKE)
