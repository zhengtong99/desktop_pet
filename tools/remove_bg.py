"""Pre-generate transparent pet cut-outs from the photos in ``pic/``.

This is optional: the app also generates cut-outs automatically at runtime.
It's handy for building the committed default set. Run from the project root:

    python tools/remove_bg.py            # process new/changed photos
    python tools/remove_bg.py --force    # re-process everything
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pet import bg_removal, library  # noqa: E402


def process(force: bool = False) -> None:
    library.ensure_workspace()
    if not bg_removal.is_available():
        raise SystemExit(
            "rembg is not installed. Run: pip install -r requirements-dev.txt"
        )

    photos = library.source_photos()
    if not photos:
        raise SystemExit(f"No photos found in {library.pic_dir()}")

    total = len(photos)
    for index, src in enumerate(photos, start=1):
        out = library.expected_output(src)
        exists = (out.is_dir() and any(out.glob("*.png"))) or out.is_file()
        if exists and not force:
            print(f"[{index}/{total}] skip (exists): {out.name}")
            continue

        print(f"[{index}/{total}] processing: {src.name} ...", flush=True)
        try:
            bg_removal.process_source(src, out)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"    failed: {exc}", file=sys.stderr)
            continue
        print(f"    saved: {out.name}")

    print(f"\nDone. Cut-outs are in: {library.pets_cache_dir()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-process images even if the output PNG already exists.",
    )
    args = parser.parse_args()
    process(force=args.force)


if __name__ == "__main__":
    main()
