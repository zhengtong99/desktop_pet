"""A cute speech bubble that floats above the pet.

It is its own frameless, translucent, always-on-top window with a *solid*
(opaque) rounded background so text stays readable, positioned above the pet so
it never covers the character. It fades in, waits, then fades out.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QWidget

_MAX_WIDTH = 280
_PADDING = 16
_RADIUS = 18
_TAIL = 12  # height of the little pointer under the bubble


class SpeechBubble(QWidget):
    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self._text = ""
        self._text_rect = QRect()
        self._font = self._build_font()
        self._speak_text = ""           # English to pronounce (word cards only)
        # Normal bubbles are click-through; word cards are clickable to speak.
        self._click_through = False

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out)

        self._fade = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade.setDuration(220)
        self._fading_out = False
        self._fade.finished.connect(self._on_fade_finished)

    @staticmethod
    def _build_font() -> QFont:
        # Bundled cute cartoon font first, then friendly per-OS fallbacks.
        from .fonts import cute_font_family

        families = []
        cute = cute_font_family()
        if cute:
            families.append(cute)
        families += [
            "PingFang SC", "Yuanti SC", "Hiragino Sans GB",  # macOS
            "Microsoft YaHei UI", "Microsoft YaHei",         # Windows
            "Segoe UI", "Arial", "sans-serif",
        ]
        font = QFont()
        font.setFamilies(families)
        font.setPointSize(14)
        return font

    # -- public API --------------------------------------------------------

    def show_message(
        self,
        text: str,
        anchor: QPoint,
        duration_ms: int = 4200,
        speak_text: str | None = None,
    ) -> None:
        """Show ``text`` in a bubble whose bottom tail points at ``anchor``.

        ``anchor`` is a global screen point (typically just above the pet's
        head). If ``speak_text`` is given, the bubble shows a speaker icon and
        becomes clickable to pronounce that text aloud.
        """
        self._speak_text = speak_text or ""
        self._text = f"{text}\n🔊 点我发音 / tap to hear" if speak_text else text
        self._set_click_through(speak_text is None)
        self._layout_for_text()
        self._place_above(anchor)

        self._hide_timer.stop()
        self._fade.stop()
        self._fading_out = False
        self.setWindowOpacity(0.0)
        self.show()
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade.start()
        self._hide_timer.start(duration_ms)

    def hide_now(self) -> None:
        self._hide_timer.stop()
        self._fade.stop()
        self.hide()

    def move_to_anchor(self, anchor: QPoint) -> None:
        """Reposition above ``anchor`` (used when the pet is dragged/resized)."""
        if self.isVisible():
            self._place_above(anchor)

    def _set_click_through(self, on: bool) -> None:
        if on == self._click_through:
            return
        self._click_through = on
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, on)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self._speak_text and event.button() == Qt.MouseButton.LeftButton:
            from .speak import speak_async

            speak_async(self._speak_text)
            event.accept()

    # -- geometry ----------------------------------------------------------

    def _layout_for_text(self) -> None:
        metrics = QFontMetrics(self._font)
        avail = QRect(0, 0, _MAX_WIDTH - 2 * _PADDING, 10_000)
        flags = int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter)
        bounds = metrics.boundingRect(avail, flags, self._text)
        self._text_rect = QRect(_PADDING, _PADDING, bounds.width(), bounds.height())
        width = bounds.width() + 2 * _PADDING
        height = bounds.height() + 2 * _PADDING + _TAIL
        self.resize(max(width, 60), height)

    def _place_above(self, anchor: QPoint) -> None:
        x = anchor.x() - self.width() // 2
        y = anchor.y() - self.height()
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        geo = screen.availableGeometry()
        x = max(geo.left() + 4, min(x, geo.right() - self.width() - 4))
        y = max(geo.top() + 4, y)
        self.move(x, y)

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        body = QRectF(1, 1, self.width() - 2, self.height() - _TAIL - 2)
        path = QPainterPath()
        path.addRoundedRect(body, _RADIUS, _RADIUS)

        # Downward tail centered on the bubble.
        cx = self.width() / 2
        tail_top = body.bottom()
        tail = QPainterPath()
        tail.moveTo(cx - 11, tail_top - 2)
        tail.lineTo(cx, tail_top + _TAIL)
        tail.lineTo(cx + 11, tail_top - 2)
        tail.closeSubpath()
        path = path.united(tail)

        painter.setPen(QPen(QColor(255, 175, 195), 2))     # soft pink outline
        painter.setBrush(QColor(255, 252, 250, 245))        # near-opaque cream
        painter.drawPath(path)

        painter.setPen(QColor(124, 58, 140))          # lively orchid purple
        painter.setFont(self._font)
        painter.drawText(
            self._text_rect,
            int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter),
            self._text,
        )

    # -- fade out ----------------------------------------------------------

    def _fade_out(self) -> None:
        self._fade.stop()
        self._fading_out = True
        self._fade.setStartValue(self.windowOpacity())
        self._fade.setEndValue(0.0)
        self._fade.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade.start()

    def _on_fade_finished(self) -> None:
        if self._fading_out:
            self._fading_out = False
            self.hide()
