"""Prepare a locally supplied manuscript scan for manual paleographic annotation.

This step never downloads images or claims automatic character recognition.
Original source must be kept unchanged and licensing tracked separately.
"""
import math
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance


def assert_distinct_files(src: Path, dst: Path) -> None:
    """Reject an output that names the source, including filesystem aliases."""
    src, dst = Path(src), Path(dst)
    if src.resolve() == dst.resolve() or (
        src.exists() and dst.exists() and src.samefile(dst)
    ):
        raise ValueError("Source and output must be different files; preserve the original")


def prepare_scan(src: Path, dst: Path, mirror: bool = False, contrast: float = 1.4):
    if not math.isfinite(contrast) or contrast <= 0 or contrast > 10:
        raise ValueError("contrast must be finite, greater than 0 and at most 10")
    src, dst = Path(src), Path(dst)
    assert_distinct_files(src, dst)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if mirror:
            im = ImageOps.mirror(im)
        im = ImageOps.autocontrast(im, preserve_tone=True)
        im = ImageEnhance.Contrast(im).enhance(contrast)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst)
    return str(dst)
