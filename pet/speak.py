"""Speak English text aloud using the operating system's built-in voice.

No extra libraries, no API keys, no internet required:

  * macOS   -> the ``say`` command
  * Windows -> System.Speech via PowerShell, falling back to SAPI.SpVoice (cscript)
  * Linux   -> ``spd-say`` or ``espeak`` if available

Speaking happens on a background thread so the pet never freezes, and text is
passed as arguments / stdin (never through a shell) so it is safe.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
# PowerShell reads the phrase from stdin so quoting can't break anything.
_WIN_PS = (
    "Add-Type -AssemblyName System.Speech;"
    "(New-Object System.Speech.Synthesis.SpeechSynthesizer)"
    ".Speak([Console]::In.ReadToEnd())"
)
_WIN_VBS = 'Set v=CreateObject("SAPI.SpVoice")\r\nv.Speak WScript.StdIn.ReadAll\r\n'


def _pipe(cmd: list[str], text: str) -> int:
    return subprocess.run(
        cmd, input=text, text=True, check=False, creationflags=_NO_WINDOW
    ).returncode


def _speak_windows(text: str) -> None:
    # Preferred: PowerShell + System.Speech (unaffected by script exec policy).
    try:
        if _pipe(["powershell", "-NoProfile", "-Command", _WIN_PS], text) == 0:
            return
    except Exception:
        pass
    # Fallback: classic SAPI voice via a tiny temporary VBScript (no PowerShell).
    path = ""
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".vbs", delete=False) as f:
            f.write(_WIN_VBS)
            path = f.name
        _pipe(["cscript", "//nologo", "//B", path], text)
    except Exception:
        pass
    finally:
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


def _speak_blocking(text: str) -> None:
    try:
        if sys.platform == "darwin":
            subprocess.run(["say", text], check=False)
        elif sys.platform.startswith("win"):
            _speak_windows(text)
        else:
            for tool in ("spd-say", "espeak"):
                if shutil.which(tool):
                    subprocess.run([tool, text], check=False)
                    break
    except Exception:
        # Pronunciation is a nice-to-have; never crash if TTS is unavailable.
        pass


def speak_async(text: str) -> None:
    """Pronounce ``text`` without blocking the UI."""
    text = (text or "").strip()
    if not text:
        return
    threading.Thread(target=_speak_blocking, args=(text,), daemon=True).start()
