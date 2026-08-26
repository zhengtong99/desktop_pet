"""A little American-English phrasebook the pet uses to teach you English.

Each entry has the English text (``en``), a Chinese translation/explanation
(``zh``), and a ``kind`` tag (word / phrase / expression). One is shown at random
in a speech bubble with a speaker button that pronounces the English aloud.

Kept offline on purpose: a curated list gives natural, everyday American English
with good translations, works without internet, and needs no API key.
"""
from __future__ import annotations

import random

# kind: "word" | "phrase" | "expression"
ENTRIES: list[dict[str, str]] = [
    # --- everyday expressions ---
    {"en": "Break a leg!", "zh": "祝你好运！（用于表演/考试前）", "kind": "expression"},
    {"en": "No worries.", "zh": "没事儿 / 别担心", "kind": "expression"},
    {"en": "It's a piece of cake.", "zh": "小菜一碟，太简单了", "kind": "expression"},
    {"en": "Hang in there!", "zh": "坚持住，挺住！", "kind": "expression"},
    {"en": "You nailed it!", "zh": "你太棒了，完美搞定！", "kind": "expression"},
    {"en": "Let's grab a bite.", "zh": "咱们随便吃点吧", "kind": "expression"},
    {"en": "I'm on it.", "zh": "我这就去办", "kind": "expression"},
    {"en": "My bad.", "zh": "我的错，抱歉", "kind": "expression"},
    {"en": "Sounds good to me.", "zh": "我觉得挺好 / 可以", "kind": "expression"},
    {"en": "Take it easy.", "zh": "放轻松 / 慢慢来", "kind": "expression"},
    {"en": "What's up?", "zh": "最近怎么样？/ 咋啦？", "kind": "expression"},
    {"en": "Long time no see!", "zh": "好久不见！", "kind": "expression"},
    {"en": "Let's call it a day.", "zh": "今天就到这儿吧", "kind": "expression"},
    {"en": "It's up to you.", "zh": "由你决定", "kind": "expression"},
    {"en": "I got your back.", "zh": "有我在，我挺你", "kind": "expression"},
    {"en": "Give me a heads-up.", "zh": "提前跟我说一声", "kind": "expression"},
    {"en": "Let's play it by ear.", "zh": "到时候再看情况吧", "kind": "expression"},
    {"en": "That works for me.", "zh": "对我来说没问题", "kind": "expression"},
    {"en": "Keep me posted.", "zh": "随时告诉我进展", "kind": "expression"},
    {"en": "It's not a big deal.", "zh": "没什么大不了的", "kind": "expression"},
    {"en": "Speak of the devil!", "zh": "说曹操曹操到！", "kind": "expression"},
    {"en": "I'm all ears.", "zh": "我洗耳恭听", "kind": "expression"},
    {"en": "Let's touch base later.", "zh": "咱们晚点再对一下", "kind": "expression"},
    {"en": "Better late than never.", "zh": "迟到总比不到好", "kind": "expression"},
    {"en": "Chill out.", "zh": "淡定，别激动", "kind": "expression"},
    {"en": "It's on me.", "zh": "这顿我请", "kind": "expression"},
    {"en": "Cross your fingers.", "zh": "祈祷好运吧", "kind": "expression"},
    {"en": "That's a bummer.", "zh": "真扫兴 / 太可惜了", "kind": "expression"},
    {"en": "Way to go!", "zh": "干得漂亮！", "kind": "expression"},
    {"en": "Let's wrap it up.", "zh": "咱们收尾吧", "kind": "expression"},

    # --- common phrases ---
    {"en": "for the time being", "zh": "暂时，目前", "kind": "phrase"},
    {"en": "on the same page", "zh": "看法一致，达成共识", "kind": "phrase"},
    {"en": "around the corner", "zh": "近在眼前，即将到来", "kind": "phrase"},
    {"en": "a rain check", "zh": "改天再约", "kind": "phrase"},
    {"en": "under the weather", "zh": "身体不舒服", "kind": "phrase"},
    {"en": "in the long run", "zh": "从长远来看", "kind": "phrase"},
    {"en": "a ballpark figure", "zh": "大致的估算数字", "kind": "phrase"},
    {"en": "the bottom line", "zh": "最关键的一点 / 底线", "kind": "phrase"},
    {"en": "on second thought", "zh": "再想想的话；转念一想", "kind": "phrase"},
    {"en": "sooner or later", "zh": "迟早", "kind": "phrase"},
    {"en": "a piece of advice", "zh": "一条建议", "kind": "phrase"},
    {"en": "off the top of my head", "zh": "一下子想到的；不加思索地", "kind": "phrase"},

    # --- useful words ---
    {"en": "awesome", "zh": "很棒的，超赞的", "kind": "word"},
    {"en": "cozy", "zh": "温馨舒适的", "kind": "word"},
    {"en": "gorgeous", "zh": "美极了，华丽的", "kind": "word"},
    {"en": "grateful", "zh": "感激的", "kind": "word"},
    {"en": "hilarious", "zh": "非常搞笑的", "kind": "word"},
    {"en": "cheerful", "zh": "开朗愉快的", "kind": "word"},
    {"en": "brilliant", "zh": "聪明的；极好的", "kind": "word"},
    {"en": "delicious", "zh": "美味的", "kind": "word"},
    {"en": "adorable", "zh": "可爱迷人的", "kind": "word"},
    {"en": "fantastic", "zh": "极好的，了不起的", "kind": "word"},
    {"en": "curious", "zh": "好奇的", "kind": "word"},
    {"en": "gentle", "zh": "温柔的，轻柔的", "kind": "word"},
]


_last_index = -1


def random_entry() -> dict[str, str]:
    """Return a random entry, avoiding an immediate repeat."""
    global _last_index
    if len(ENTRIES) <= 1:
        return ENTRIES[0]
    index = random.randrange(len(ENTRIES))
    while index == _last_index:
        index = random.randrange(len(ENTRIES))
    _last_index = index
    return ENTRIES[index]
