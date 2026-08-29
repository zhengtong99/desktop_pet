"""The pet itself: a draggable, pokeable, always-on-top transparent window."""
from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from . import animations, library, messages, phrasebook, processing, weather
from .celebrations import CelebrationOverlay
from .config import Config
from .holidays import active_holiday
from .speech_bubble import SpeechBubble

# Empty room kept around the pet so hops / wobbles never clip.
MARGIN_X = 45
MARGIN_TOP = 70
MARGIN_BOTTOM = 20

SIZE_PRESETS = [
    ("小 / Small", 0.08),
    ("中 / Medium", 0.12),
    ("大 / Large", 0.18),
    ("超大 / X-Large", 0.28),
]
MIN_SCALE, MAX_SCALE = 0.05, 1.20
_DRAG_THRESHOLD = 5  # px before a press counts as a drag rather than a poke


class PetWindow(QWidget):
    def __init__(self, config: Config) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        # Keep the pet visible even when another app is focused (macOS).
        if hasattr(Qt.WidgetAttribute, "WA_MacAlwaysShowToolWindow"):
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)

        self.config = config
        self._pets: list[Path] = library.cached_pets()
        self._pet_index = 0

        self._scale = float(config.get("scale", 0.35))
        self._frames: list[QPixmap] = []          # full-res frames of current pet
        self._scaled_frames: list[QPixmap] = []    # frames scaled to display size
        self._frame_index = 0
        self._frame_step = 1                        # for ping-pong looping
        self._pixmap = QPixmap()   # the frame currently painted

        # Active poke animation + current transform applied while painting.
        self._anim_iter = None
        self._anim_seq_index = 0
        self._transform = {"off_x": 0.0, "off_y": 0.0, "scale_x": 1.0, "scale_y": 1.0}

        self._bubble = SpeechBubble()
        self._overlay: CelebrationOverlay | None = None
        self._weather_thread = None
        self._sync_thread = None
        self._sync_pending = False

        # Drag state.
        self._press_global = QPoint()
        self._drag_offset = QPoint()
        self._dragging = False
        self._maybe_drag = False

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._advance_animation)

        # Loop playback for animated (live-photo) pets.
        self._play_timer = QTimer(self)
        self._play_timer.timeout.connect(self._advance_frame)

        self._chitchat_timer = QTimer(self)
        self._chitchat_timer.timeout.connect(self._chitchat)

        self.setWindowTitle("Desktop Pet")
        self._apply_always_on_top(bool(config.get("always_on_top", True)))
        self._choose_today_pet()
        self._load_pet()
        self._restore_position()
        self._watch_pic_folder()

    def _watch_pic_folder(self) -> None:
        # Auto re-sync whenever pic/ changes, so deleted photos never linger.
        self._pic_watcher = QFileSystemWatcher(self)
        pic = str(library.pic_dir())
        if Path(pic).exists():
            self._pic_watcher.addPath(pic)
        self._pic_watcher.directoryChanged.connect(self._on_pic_folder_changed)
        self._pic_debounce = QTimer(self)
        self._pic_debounce.setSingleShot(True)
        self._pic_debounce.timeout.connect(self.start_library_sync)

    def _on_pic_folder_changed(self, path: str) -> None:
        # Some platforms drop the watch after a change; re-add defensively.
        if path not in self._pic_watcher.directories() and Path(path).exists():
            self._pic_watcher.addPath(path)
        # Coalesce bursts of filesystem events (e.g. dragging in many files).
        self._pic_debounce.start(700)

    # -- asset / sizing ----------------------------------------------------

    def _load_pet(self) -> None:
        if not self._pets:
            return
        paths = library.frame_paths(self._pets[self._pet_index])
        self._frames = [QPixmap(str(p)) for p in paths]
        self._frames = [f for f in self._frames if not f.isNull()]
        self._frame_index = 0
        self._frame_step = 1
        self._rebuild_scaled()
        # Loop only when there is more than one frame (live-photo pets).
        if len(self._frames) > 1:
            self._play_timer.start(80)  # ~12.5 fps
        else:
            self._play_timer.stop()

    def _clear_pet(self) -> None:
        """Drop currently displayed pet frames after library becomes empty."""
        self._play_timer.stop()
        self._frames = []
        self._scaled_frames = []
        self._frame_index = 0
        self._frame_step = 1
        self._pixmap = QPixmap()
        self.update()

    def _rebuild_scaled(self) -> None:
        if not self._frames:
            return
        w = max(1, int(self._frames[0].width() * self._scale))
        self._scaled_frames = [
            f.scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
            for f in self._frames
        ]
        self._frame_index = min(self._frame_index, len(self._scaled_frames) - 1)
        self._pixmap = self._scaled_frames[self._frame_index]
        pw, ph = self._pixmap.width(), self._pixmap.height()
        # Keep the feet anchored: remember old bottom-center, resize, restore.
        old_anchor = self._foot_global()
        self.resize(pw + 2 * MARGIN_X, ph + MARGIN_TOP + MARGIN_BOTTOM)
        if old_anchor is not None:
            self._move_foot_to(old_anchor)
        self.update()
        self._follow_bubble()

    def _advance_frame(self) -> None:
        count = len(self._scaled_frames)
        if count <= 1:
            return
        # Ping-pong so the loop has no visible seam.
        self._frame_index += self._frame_step
        if self._frame_index >= count - 1:
            self._frame_index = count - 1
            self._frame_step = -1
        elif self._frame_index <= 0:
            self._frame_index = 0
            self._frame_step = 1
        self._pixmap = self._scaled_frames[self._frame_index]
        self.update()

    def _follow_bubble(self) -> None:
        # Keep any visible speech bubble anchored above the pet's head.
        bubble = getattr(self, "_bubble", None)
        if bubble is not None:
            bubble.move_to_anchor(self._head_global())

    def moveEvent(self, event) -> None:  # noqa: N802
        super().moveEvent(event)
        self._follow_bubble()

    def _foot_global(self) -> QPoint | None:
        if self._pixmap.isNull() or not self.isVisible():
            return None
        cx = MARGIN_X + self._pixmap.width() / 2
        by = MARGIN_TOP + self._pixmap.height()
        return self.mapToGlobal(QPoint(int(cx), int(by)))

    def _move_foot_to(self, global_point: QPoint) -> None:
        cx = MARGIN_X + self._pixmap.width() / 2
        by = MARGIN_TOP + self._pixmap.height()
        self.move(int(global_point.x() - cx), int(global_point.y() - by))

    def _head_global(self) -> QPoint:
        cx = MARGIN_X + self._pixmap.width() / 2
        return self.mapToGlobal(QPoint(int(cx), MARGIN_TOP - 4))

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        if self._pixmap.isNull():
            return
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        pw, ph = self._pixmap.width(), self._pixmap.height()
        cx = MARGIN_X + pw / 2 + self._transform["off_x"]
        by = MARGIN_TOP + ph + self._transform["off_y"]
        painter.translate(cx, by)
        painter.scale(self._transform["scale_x"], self._transform["scale_y"])
        painter.drawPixmap(int(-pw / 2), int(-ph), self._pixmap)

    # -- mouse interaction -------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._drag_offset = self._press_global - self.frameGeometry().topLeft()
            self._maybe_drag = True
            self._dragging = False
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self._maybe_drag:
            return
        current = event.globalPosition().toPoint()
        if not self._dragging:
            if (current - self._press_global).manhattanLength() >= _DRAG_THRESHOLD:
                self._dragging = True
        if self._dragging:
            self.move(current - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._dragging:
            self._save_position()
        elif self._maybe_drag:
            self._poke()
        self._maybe_drag = False
        self._dragging = False

    def wheelEvent(self, event) -> None:  # noqa: N802
        step = 0.05 if event.angleDelta().y() > 0 else -0.05
        new_scale = max(MIN_SCALE, min(MAX_SCALE, self._scale + step))
        if abs(new_scale - self._scale) > 1e-6:
            self._scale = new_scale
            self._rebuild_scaled()
            self.config.set("scale", self._scale)
        event.accept()

    def contextMenuEvent(self, event) -> None:  # noqa: N802
        self._show_menu(event.globalPos())

    # -- context menu ------------------------------------------------------

    def _show_menu(self, global_pos: QPoint) -> None:
        menu = QMenu(self)

        size_menu = menu.addMenu("调整大小 / Size")
        group = QActionGroup(size_menu)
        group.setExclusive(True)
        for label, value in SIZE_PRESETS:
            act = QAction(label, size_menu, checkable=True)
            act.setChecked(abs(value - self._scale) < 0.03)
            act.triggered.connect(lambda _=False, v=value: self._set_scale(v))
            group.addAction(act)
            size_menu.addAction(act)

        if len(self._pets) > 1:
            switch = QAction("换一个 / Switch character", menu)
            switch.triggered.connect(self._next_pet)
            menu.addAction(switch)

        hi = QAction("陪我聊聊 / Say hi", menu)
        hi.triggered.connect(lambda: self._say(messages.random_chitchat()))
        menu.addAction(hi)

        learn = QAction("学个英语 / Learn English", menu)
        learn.triggered.connect(self._learn_english)
        menu.addAction(learn)

        learn_chinese = QAction("学中文和文化 / Learn Chinese & Culture", menu)
        learn_chinese.triggered.connect(self._learn_chinese)
        menu.addAction(learn_chinese)

        wx = QAction("今天天气 / Weather", menu)
        wx.triggered.connect(self._start_weather)
        menu.addAction(wx)

        party = QAction("庆祝一下 / Celebrate", menu)
        party.triggered.connect(self._celebrate_now)
        menu.addAction(party)

        sync_now = QAction("立即同步素材 / Sync library now", menu)
        sync_now.triggered.connect(self._sync_library_now)
        menu.addAction(sync_now)

        menu.addSeparator()

        top = QAction("始终置顶 / Always on top", menu, checkable=True)
        top.setChecked(bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        top.triggered.connect(self._toggle_always_on_top)
        menu.addAction(top)

        about = QAction("关于 / About", menu)
        about.triggered.connect(self._show_about)
        menu.addAction(about)

        menu.addSeparator()
        quit_act = QAction("退出 / Quit", menu)
        quit_act.triggered.connect(QApplication.quit)
        menu.addAction(quit_act)

        menu.exec(global_pos)

    # -- behaviours --------------------------------------------------------

    def _poke(self) -> None:
        factory = animations.SEQUENCE[self._anim_seq_index % len(animations.SEQUENCE)]
        self._anim_seq_index += 1
        self._anim_iter = factory()
        if not self._anim_timer.isActive():
            self._anim_timer.start(16)
        if random.random() < 0.7:
            self._say(messages.random_poke(), duration_ms=2600)

    def _advance_animation(self) -> None:
        if self._anim_iter is None:
            self._anim_timer.stop()
            return
        try:
            frame = next(self._anim_iter)
        except StopIteration:
            self._anim_iter = None
            self._transform = {"off_x": 0.0, "off_y": 0.0, "scale_x": 1.0, "scale_y": 1.0}
            self._anim_timer.stop()
            self.update()
            return
        self._transform = {
            "off_x": frame.get("off_x", 0.0),
            "off_y": frame.get("off_y", 0.0),
            "scale_x": frame.get("scale_x", 1.0),
            "scale_y": frame.get("scale_y", 1.0),
        }
        self.update()

    def _say(self, text: str, duration_ms: int = 4200) -> None:
        self._bubble.show_message(text, self._head_global(), duration_ms)

    def _chitchat(self) -> None:
        # Lean towards English mini-lessons, with cute lines mixed in.
        if random.random() < 0.65:
            self._learn_english()
        else:
            self._say(messages.random_chitchat())
        self._chitchat_timer.start(random.randint(25_000, 55_000))

    def _learn_english(self) -> None:
        entry = phrasebook.random_entry()
        text = f"{entry['en']}\n{entry['zh']}"
        self._bubble.show_message(
            text, self._head_global(), duration_ms=8000, speak_text=entry["en"]
        )

    def _learn_chinese(self) -> None:
        entry = phrasebook.random_chinese_entry()
        text = (
            f"{entry['zh']}\n"
            f"{entry['pinyin']}\n"
            f"{entry['en']}\n"
            f"{entry['culture']}"
        )
        self._bubble.show_message(
            text,
            self._head_global(),
            duration_ms=9000,
            speak_text=entry["zh"],
            speak_language="zh-CN",
        )

    def _set_scale(self, value: float) -> None:
        self._scale = value
        self._rebuild_scaled()
        self.config.set("scale", value)

    def _next_pet(self) -> None:
        if len(self._pets) < 2:
            return
        self._pet_index = (self._pet_index + 1) % len(self._pets)
        self._remember_choice()
        self._load_pet()

    def _choose_today_pet(self) -> None:
        """Pick the pet for today: the same one all day, random each new day.

        With a single photo, that one is always used. A manual switch sticks
        until the next day.
        """
        import datetime as dt
        import random as _random

        if not self._pets:
            self._pet_index = 0
            return
        names = [p.stem for p in self._pets]
        today = dt.date.today().isoformat()
        saved_name = str(self.config.get("pet_name", ""))
        saved_date = str(self.config.get("daily_date", ""))

        if len(names) == 1:
            self._pet_index = 0
        elif saved_date == today and saved_name in names:
            self._pet_index = names.index(saved_name)
        else:
            self._pet_index = names.index(_random.Random(today).choice(names))
        self._remember_choice()

    def _remember_choice(self) -> None:
        import datetime as dt

        if not self._pets:
            return
        self.config.set("daily_date", dt.date.today().isoformat())
        self.config.set("pet_name", self._pets[self._pet_index].stem)

    # -- library sync (generate pets from the photo folder) ----------------

    def start_library_sync(self) -> None:
        if self._sync_thread is not None and self._sync_thread.isRunning():
            self._sync_pending = True
            return
        todo, orphans = library.plan_sync()
        if not todo and not orphans:
            return
        self._sync_pending = False
        self._sync_thread = processing.sync_library_async(
            self, self._on_library_synced
        )

    def _sync_library_now(self) -> None:
        if self._sync_thread is not None and self._sync_thread.isRunning():
            self._sync_pending = True
            self._say("正在同步中，请稍等～ Sync already running.", duration_ms=2600)
            return
        self.start_library_sync()
        self._say("开始同步素材～ Sync started.", duration_ms=2400)

    def _on_library_synced(self, processed: int, unprocessed: int) -> None:
        sync_pending = self._sync_pending
        self._sync_thread = None
        self._sync_pending = False
        had_none = not self._pets
        self._pets = library.cached_pets()
        if not self._pets:
            self._clear_pet()
            self.hide()
            if sync_pending:
                QTimer.singleShot(0, self.start_library_sync)
            return

        if not self.isVisible():
            self.show()

        names = [p.stem for p in self._pets]
        current = str(self.config.get("pet_name", ""))

        if had_none and self._pets:
            self._choose_today_pet()
            self._load_pet()
            self._restore_position()
        elif current in names:
            self._pet_index = names.index(current)
        elif self._pets:
            # Current pet was removed; fall back to today's pick.
            self._choose_today_pet()
            self._load_pet()

        if processed:
            self._say("新朋友准备好啦！ New friend is ready! 🎉", duration_ms=4500)
        elif unprocessed:
            self._say(
                "发现新照片，但缺少抠图组件～\n"
                "Found new photos, but the cut-out engine isn't available.",
                duration_ms=6000,
            )

        if sync_pending:
            QTimer.singleShot(0, self.start_library_sync)

    def _toggle_always_on_top(self, checked: bool) -> None:
        self._apply_always_on_top(checked)
        self.config.set("always_on_top", checked)

    def _apply_always_on_top(self, on: bool) -> None:
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, on)
        # Changing flags on an already-visible window requires re-showing.
        if self.isVisible():
            self.show()

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "关于 / About Desktop Pet",
            "非官方·非商业·粉丝自制，与艺人无关。仅供个人非商业使用。\n"
            "照片版权/肖像权归原权利人，用户自行添加并负责。\n\n"
            "Unofficial, non-commercial, fan-made. Not affiliated with any "
            "artist. Personal use only; photos belong to their owners.\n\n"
            "Takedown / 侵权删除: jtanpp0319@gmail.com\n"
            "License: PolyForm Noncommercial 1.0.0",
        )

    # -- startup extras: weather + holidays --------------------------------

    def greet_and_report(self, *, skip_weather: bool = False) -> None:
        """Show an opening greeting, celebrate any holiday, fetch weather."""
        import datetime as dt

        holiday = active_holiday(dt.date.today())
        if self.config.get("greeting_on_start", True):
            if holiday is not None:
                self._say(holiday.greeting, duration_ms=6000)
            else:
                self._say(messages.random_chitchat(), duration_ms=5000)

        if holiday is not None:
            QTimer.singleShot(400, lambda: self._celebrate(holiday.theme, holiday.emojis))

        if (not skip_weather) and self.config.get("weather_on_start", True):
            QTimer.singleShot(6500, self._start_weather)

        self._chitchat_timer.start(random.randint(30_000, 60_000))

    def _start_weather(self) -> None:
        self._weather_thread = weather.fetch_weather_async(
            self, on_ready=self._on_weather, on_failed=self._on_weather_failed
        )

    def _on_weather(self, report: str) -> None:
        self._say(report, duration_ms=8000)

    def _on_weather_failed(self, _error: str) -> None:
        # Stay quiet if the network is unavailable.
        pass

    # -- celebrations ------------------------------------------------------

    def _celebrate_now(self) -> None:
        import datetime as dt

        holiday = active_holiday(dt.date.today())
        if holiday is not None:
            self._say(holiday.greeting, duration_ms=5000)
            self._celebrate(holiday.theme, holiday.emojis)
        else:
            self._say("撒花庆祝一下～ Yay, confetti! 🎉", duration_ms=4000)
            self._celebrate("confetti", ["🎉", "🎊", "✨", "💖"])

    def _celebrate(self, theme: str, emojis: list[str]) -> None:
        # Confine the effect to a box around the pet, not the whole screen.
        frame = self.frameGeometry()
        side, top = 104, 128  # extra room at the sides/below and above (fireworks)
        region = QRect(
            frame.x() - side,
            frame.y() - top,
            frame.width() + 2 * side,
            frame.height() + top + side,
        )
        screen = self.screen() or QApplication.primaryScreen()
        region = region.intersected(screen.geometry())
        self._overlay = CelebrationOverlay(region, theme, emojis)
        self._overlay.start()

    # -- position persistence ---------------------------------------------

    def _restore_position(self) -> None:
        x, y = self.config.get("pos_x"), self.config.get("pos_y")
        if x is not None and y is not None:
            self.move(int(x), int(y))
            return
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.right() - self.width() - 40,
            screen.bottom() - self.height() - 40,
        )

    def _save_position(self) -> None:
        pos = self.frameGeometry().topLeft()
        self.config.set("pos_x", pos.x())
        self.config.set("pos_y", pos.y())

    def closeEvent(self, event) -> None:  # noqa: N802
        self._bubble.hide_now()
        super().closeEvent(event)
