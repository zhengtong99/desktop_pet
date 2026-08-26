"""Manage the user's photo folder and the generated transparent pets.

Layout depends on how the app is run:

* From source (repo present): photos live in ``<project>/pic`` and their
  cut-outs in ``<project>/assets/pets`` (both editable in the repo).
* Bundled app: a friendly, writable folder ``~/DesktopPet`` is used, with
  ``pic/`` for the user's photos and ``pets/`` for the cut-outs. On first run it
  is seeded with the bundled sample photos and their ready-made cut-outs, so the
  user can simply delete the samples and drop in their own pictures.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

IMAGE_SUFFIXES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".heic",
    ".heif",
}
# "Live photo" / short video clips turned into an animated (looping) pet.
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v"}
MEDIA_SUFFIXES = IMAGE_SUFFIXES | VIDEO_SUFFIXES


def _is_bundled() -> bool:
    return getattr(sys, "_MEIPASS", None) is not None


def _bundle_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS"))


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def user_base() -> Path:
    if _is_bundled():
        return Path.home() / "DesktopPet"
    return _project_root()


def pic_dir() -> Path:
    return user_base() / "pic"


def pets_cache_dir() -> Path:
    if _is_bundled():
        return user_base() / "pets"
    return _project_root() / "assets" / "pets"


def _list_media(folder: Path, suffixes: set[str]) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in suffixes
    )


def source_photos() -> list[Path]:
    return _list_media(pic_dir(), MEDIA_SUFFIXES)


def cached_pets() -> list[Path]:
    """Return one path per pet: a ``.png`` file (static) or a folder (animated).

    A folder holds the frames of a live-photo pet. If both exist for the same
    name, the animated folder wins.
    """
    folder = pets_cache_dir()
    if not folder.exists():
        return []
    items: dict[str, Path] = {}
    for p in sorted(folder.iterdir()):
        if p.is_dir():
            if any(p.glob("*.png")):
                items[p.stem] = p
        elif p.suffix.lower() == ".png":
            items.setdefault(p.stem, p)
    return [items[name] for name in sorted(items)]


def frame_paths(pet: Path) -> list[Path]:
    """Ordered frame files for ``pet`` (one for a static pet, many for animated)."""
    if pet.is_dir():
        return sorted(pet.glob("*.png"))
    return [pet]


def expected_output(src: Path) -> Path:
    """Where a source's cut-out lives: a folder for video, a PNG for photos."""
    stem = src.stem
    if src.suffix.lower() in VIDEO_SUFFIXES:
        return pets_cache_dir() / stem
    return pets_cache_dir() / (stem + ".png")


def ensure_workspace() -> None:
    """Create the folders and, for the bundled app, seed the first-run samples."""
    pic = pic_dir()
    cache = pets_cache_dir()
    pic.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    if not _is_bundled():
        return

    # Seed sample photos/videos so the user has something to look at and can
    # replace. (Videos are kept so their animated pets aren't seen as orphans.)
    if not source_photos():
        bundled_pics = _bundle_dir() / "pic"
        if bundled_pics.exists():
            for f in _list_media(bundled_pics, MEDIA_SUFFIXES):
                shutil.copy2(f, pic / f.name)

    # Seed ready-made cut-outs (static PNGs and animated folders) so a pet
    # appears instantly on first launch.
    if not cached_pets():
        bundled_pets = _bundle_dir() / "assets" / "pets"
        if bundled_pets.exists():
            for f in bundled_pets.iterdir():
                if f.is_dir():
                    shutil.copytree(f, cache / f.name, dirs_exist_ok=True)
                elif f.suffix.lower() == ".png":
                    shutil.copy2(f, cache / f.name)


def _needs_processing(src: Path, out: Path) -> bool:
    if out.is_dir():
        frames = list(out.glob("*.png"))
        if not frames:
            return True
        return src.stat().st_mtime > max(f.stat().st_mtime for f in frames)
    if not out.exists():
        return True
    return src.stat().st_mtime > out.stat().st_mtime


def plan_sync() -> tuple[list[tuple[Path, Path]], list[Path]]:
    """Return (sources_to_process, orphan_pets_to_delete).

    A source needs processing if it has no cut-out yet or was edited after its
    cut-out was made. An orphan is a cut-out whose source was deleted.
    """
    sources = source_photos()
    stems = {p.stem for p in sources}

    todo: list[tuple[Path, Path]] = []
    for src in sources:
        out = expected_output(src)
        if _needs_processing(src, out):
            todo.append((src, out))

    orphans = [pet for pet in cached_pets() if pet.stem not in stems]
    return todo, orphans
