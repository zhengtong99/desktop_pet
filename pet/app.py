"""Application entry point: build the QApplication and launch the pet."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from . import library, macos
from .config import Config
from .pet_window import PetWindow
from .processing import sync_library_once


def main(*, fast_start: bool = False) -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Pet")
    app.setApplicationDisplayName("Desktop Pet")
    # Keep running in the background even though the window is frameless/tool.
    app.setQuitOnLastWindowClosed(True)
    # Run as a background agent so bubbles never steal focus (macOS).
    macos.set_accessory_activation_policy()

    library.ensure_workspace()
    # Keep generated pets strictly aligned with the current pic folder.
    sync_library_once()

    # Nothing to show and nothing to build from: guide the user to add photos.
    if not library.cached_pets() and not library.source_photos():
        QMessageBox.information(
            None,
            "Desktop Pet",
            "No photos found yet.\n\n"
            f"Add pictures or live clips (.jpg/.jpeg/.png/.webp/.bmp/.tiff/.heic/.mp4/.mov/.m4v) to this folder, then reopen:\n"
            f"{library.pic_dir()}",
        )
        return 0

    config = Config()
    pet = PetWindow(config)
    pet.show()
    pet.start_library_sync()
    pet.greet_and_report(skip_weather=fast_start)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
