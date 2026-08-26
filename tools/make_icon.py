"""Generate the app icon (PNG + .ico + .icns) from a chosen pet image.

Dev-only. Produces:
    build/icon.png     - 1024x1024 master
    build/icon.ico     - Windows icon
    build/icon.icns    - macOS icon (only when run on macOS, needs iconutil)

Usage:
    python tools/make_icon.py [source_png]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
# Dedicated icon source, kept out of the user-managed pic/ and assets/pets/.
DEFAULT_SOURCE = PROJECT_ROOT / "assets" / "icon_source.png"

CANVAS = 1024
MARGIN = 90


def _make_master(source: Path):
    from PIL import Image, ImageDraw

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    # Soft rounded-square gradient-ish background (two tones).
    draw.rounded_rectangle([0, 0, CANVAS, CANVAS], radius=220,
                           fill=(255, 214, 224, 255))
    draw.rounded_rectangle([0, CANVAS // 2, CANVAS, CANVAS], radius=220,
                           fill=(255, 198, 214, 255))

    pet = Image.open(source).convert("RGBA")
    max_side = CANVAS - 2 * MARGIN
    scale = min(max_side / pet.width, max_side / pet.height)
    pet = pet.resize((max(1, int(pet.width * scale)),
                      max(1, int(pet.height * scale))), Image.LANCZOS)
    x = (CANVAS - pet.width) // 2
    y = (CANVAS - pet.height) // 2
    canvas.alpha_composite(pet, (x, y))

    # Clip everything to the rounded square.
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, CANVAS, CANVAS],
                                           radius=220, fill=255)
    canvas.putalpha(mask)
    return canvas


def main() -> None:
    from PIL import Image

    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    if not source.exists():
        raise SystemExit(f"Source image not found: {source}")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    master = _make_master(source)

    png_path = BUILD_DIR / "icon.png"
    master.save(png_path)
    print(f"saved {png_path.relative_to(PROJECT_ROOT)}")

    ico_path = BUILD_DIR / "icon.ico"
    master.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48),
                                 (64, 64), (128, 128), (256, 256)])
    print(f"saved {ico_path.relative_to(PROJECT_ROOT)}")

    if sys.platform == "darwin":
        with tempfile.TemporaryDirectory() as tmp:
            iconset = Path(tmp) / "icon.iconset"
            iconset.mkdir()
            for size in (16, 32, 64, 128, 256, 512):
                master.resize((size, size), Image.LANCZOS).save(
                    iconset / f"icon_{size}x{size}.png")
                master.resize((size * 2, size * 2), Image.LANCZOS).save(
                    iconset / f"icon_{size}x{size}@2x.png")
            icns_path = BUILD_DIR / "icon.icns"
            subprocess.run(
                ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
                check=True,
            )
            print(f"saved {icns_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
