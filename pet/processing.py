"""Background worker that keeps the pet cut-outs in sync with the photo folder.

Runs on a separate thread so the UI never freezes while the AI processes new
photos. Emits ``finished(processed, unprocessed)`` where ``unprocessed`` is the
number of new photos that could not be handled because the cut-out engine is
unavailable.
"""
from __future__ import annotations

import shutil

from PySide6.QtCore import QObject, QThread, Signal

from . import bg_removal, library


class LibrarySyncWorker(QObject):
    finished = Signal(int, int)  # processed, unprocessed

    def run(self) -> None:
        processed, unprocessed = sync_library_once()
        self.finished.emit(processed, unprocessed)


def sync_library_once() -> tuple[int, int]:
    """Synchronize generated pets with ``pic`` once in the current thread.

    Returns ``(processed, unprocessed)`` where ``unprocessed`` is the number of
    sources that could not be processed because the cut-out engine is missing.
    """
    todo, orphans = library.plan_sync()

    # Remove cut-outs whose source photo the user deleted.
    for pet in orphans:
        try:
            if pet.is_dir():
                shutil.rmtree(pet, ignore_errors=True)
            else:
                pet.unlink()
        except OSError:
            pass

    processed = 0
    unprocessed = 0
    if todo:
        if bg_removal.is_available():
            for src, out in todo:
                try:
                    bg_removal.process_source(src, out)
                    processed += 1
                except Exception:
                    pass
        else:
            unprocessed = len(todo)

    return processed, unprocessed


def sync_library_async(parent: QObject, on_finished) -> QThread:
    """Start a library sync on a worker thread; keep the returned reference."""
    thread = QThread(parent)
    worker = LibrarySyncWorker()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(on_finished)
    worker.finished.connect(thread.quit)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread._worker = worker  # type: ignore[attr-defined]
    thread.start()
    return thread
