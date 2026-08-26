"""Background removal used both by the dev tool and at runtime.

Turns a photo into a transparent cut-out of the person(s) using the ``rembg``
AI model, then trims empty margins. ``rembg`` is optional at import time so the
app still runs (using already-processed pets) when it isn't installed.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .library import VIDEO_SUFFIXES

# Pixels dimmer than this alpha are treated as transparent when trimming.
ALPHA_THRESHOLD = 12
CROP_PADDING = 12
# Video (live photo) settings: how many frames to keep and their max width.
_VIDEO_FRAMES = 18
_VIDEO_READ_CAP = 150
_VIDEO_MAX_WIDTH = 640

_session = None


def is_available() -> bool:
    """True if the AI cut-out engine can be used."""
    try:
        import PIL  # noqa: F401
        import rembg  # noqa: F401
    except Exception:
        return False
    return True


def _get_session():
    global _session
    if _session is None:
        from rembg import new_session

        # "u2net_human_seg" is tuned for cutting out people.
        _session = new_session("u2net_human_seg")
    return _session


def _trim_to_subject(image):
    """Crop transparent margins so the pet sits snugly in its window."""
    alpha = image.split()[-1]
    mask = alpha.point(lambda a: 255 if a >= ALPHA_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image
    left, upper, right, lower = bbox
    left = max(0, left - CROP_PADDING)
    upper = max(0, upper - CROP_PADDING)
    right = min(image.width, right + CROP_PADDING)
    lower = min(image.height, lower + CROP_PADDING)
    return image.crop((left, upper, right, lower))


def process_source(src: Path, out: Path) -> None:
    """Turn ``src`` into a pet at ``out``.

    * Photo  -> ``out`` is a single transparent PNG file.
    * Video  -> ``out`` is a folder of aligned, same-size frame PNGs that the
      app plays as a looping animation.
    Any stale output of the other kind (from a previous run) is removed.
    """
    if src.suffix.lower() in VIDEO_SUFFIXES:
        _process_video(src, out)
        stale = out.with_suffix(".png")
        if stale.exists():
            stale.unlink()
    else:
        _process_image(src, out)
        stale_dir = out.with_suffix("")
        if stale_dir.is_dir():
            shutil.rmtree(stale_dir, ignore_errors=True)


def _process_image(src: Path, dest: Path) -> None:
    from PIL import Image
    from rembg import remove

    with Image.open(src) as img:
        cut = remove(img.convert("RGBA"), session=_get_session())
    cut = _trim_to_subject(cut)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cut.save(dest)


def _process_video(src: Path, out_dir: Path) -> None:
    from rembg import remove

    raw = _read_video_frames(src, _VIDEO_FRAMES)
    if not raw:
        raise RuntimeError(f"no readable frames in {src.name}")

    cuts = [remove(frame, session=_get_session()) for frame in raw]
    # Crop every frame to one shared box so the animation doesn't jitter.
    box = _union_bbox(cuts)
    if box is not None:
        cuts = [c.crop(box) for c in cuts]

    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    for index, cut in enumerate(cuts):
        cut.save(out_dir / f"{index:03d}.png")


def _read_video_frames(src: Path, count: int):
    """Read a short clip and return ``count`` evenly spaced RGBA frames."""
    import imageio.v3 as iio
    from PIL import Image

    frames = []
    for index, frame in enumerate(iio.imiter(src, plugin="FFMPEG")):
        frames.append(frame)
        if index >= _VIDEO_READ_CAP:
            break
    if not frames:
        return []

    total = len(frames)
    if count > 1 and total > 1:
        picks = sorted({round(k * (total - 1) / (count - 1)) for k in range(count)})
    else:
        picks = [total // 3]

    out = []
    for i in picks:
        img = Image.fromarray(frames[i]).convert("RGBA")
        if img.width > _VIDEO_MAX_WIDTH:
            height = int(img.height * _VIDEO_MAX_WIDTH / img.width)
            img = img.resize((_VIDEO_MAX_WIDTH, height))
        out.append(img)
    return out


def _union_bbox(images):
    """Combined bounding box of the subject across all frames (with padding)."""
    box = None
    for im in images:
        mask = im.split()[-1].point(lambda a: 255 if a >= ALPHA_THRESHOLD else 0)
        found = mask.getbbox()
        if found is None:
            continue
        if box is None:
            box = list(found)
        else:
            box[0], box[1] = min(box[0], found[0]), min(box[1], found[1])
            box[2], box[3] = max(box[2], found[2]), max(box[3], found[3])
    if box is None:
        return None
    width, height = images[0].size
    box[0] = max(0, box[0] - CROP_PADDING)
    box[1] = max(0, box[1] - CROP_PADDING)
    box[2] = min(width, box[2] + CROP_PADDING)
    box[3] = min(height, box[3] + CROP_PADDING)
    return tuple(box)
