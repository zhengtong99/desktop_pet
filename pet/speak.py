"""Speak English or Chinese text using the operating system's built-in voice.

No extra libraries, no API keys, no internet required:

  * macOS   -> the ``say`` command
  * Windows -> System.Speech via PowerShell (falls back to SAPI.SpVoice).
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
_WIN_PS_ZH = (
    "Add-Type -AssemblyName System.Speech;"
    "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
    "$s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::NotSet,"
    "[System.Speech.Synthesis.VoiceAge]::NotSet,0,"
    "[System.Globalization.CultureInfo]::GetCultureInfo('zh-CN'));"
    "$s.Speak([Console]::In.ReadToEnd())"
)
_WIN_VBS = (
    'Set v=CreateObject("SAPI.SpVoice")\r\n'
    'v.Speak WScript.StdIn.ReadAll\r\n'
)


def _pipe(cmd: list[str], text: str) -> int:
    return subprocess.run(
        cmd, input=text, text=True, check=False, creationflags=_NO_WINDOW
    ).returncode


def _speak_windows(text: str, language: str | None = None) -> None:
    # Preferred: PowerShell + System.Speech (unaffected by script exec policy).
    try:
        script = _WIN_PS_ZH if language == "zh-CN" else _WIN_PS
        if _pipe(["powershell", "-NoProfile", "-Command", script], text) == 0:
            return
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    # Fallback: SAPI voice via temporary VBScript.
    path = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".vbs", delete=False
        ) as f:
            f.write(_WIN_VBS)
            path = f.name
        _pipe(["cscript", "//nologo", "//B", path], text)
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    finally:
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


def _speak_blocking(text: str, language: str | None = None) -> None:
    try:
        if sys.platform == "darwin":
            voice = (
                "Eddy (Chinese (China mainland))"
                if language == "zh-CN"
                else None
            )
            command = ["say"]
            if voice:
                command += ["-v", voice]
            command.append(text)
            subprocess.run(command, check=False)
        elif sys.platform.startswith("win"):
            _speak_windows(text, language)
        else:
            for tool in ("spd-say", "espeak"):
                if shutil.which(tool):
                    subprocess.run([tool, text], check=False)
                    break
    except (FileNotFoundError, subprocess.SubprocessError):
        # Pronunciation is a nice-to-have; never crash if TTS is unavailable.
        pass


def speak_async(text: str, language: str | None = None) -> None:
    """Pronounce ``text`` without blocking the UI."""
    text = (text or "").strip()
    if not text:
        return
    threading.Thread(
        target=_speak_blocking, args=(text, language), daemon=True
    ).start()
