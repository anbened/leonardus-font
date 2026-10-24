"""Draw the specular right-to-left proof from the compiled mirror and source TTFs."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import freetype
import uharfbuzz as hb
from PIL import Image, ImageDraw

from leonardus.preview import require_coverage
from leonardus.specular import BASE, BASE_SHA256, OUTPUT
from regular_specimen import caption

ROOT = Path(__file__).resolve().parents[1]
LINES = ("Leonardus", "Arte, scienza e immaginazione.", "abcdefghijklmnopqrstuvwxyz",
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "à è é ì ò ù   0123456789   € 1.234,56")


def shaped_run(path: Path, text: str, direction: str):
    font = hb.Font(hb.Face(path.read_bytes()))
    font.scale = (1000, 1000)
    hb.ot_font_set_funcs(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction, buf.script, buf.language = direction, "Latn", "it"
    hb.shape(font, buf)
    return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def draw_line(image, path, text, direction, ppem, baseline, left=None, right=None):
    require_coverage(path, text)
    run, face = shaped_run(path, text, direction), freetype.Face(str(path))
    face.set_pixel_sizes(0, ppem)
    width = sum(advance for _, advance, _, _ in run) * ppem / 1000
    origin = left if left is not None else right - width
    cursor = 0
    for gid, advance, xoffset, yoffset in run:
        face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
        slot, bitmap = face.glyph, face.glyph.bitmap
        if bitmap.width and bitmap.rows:
            mask = Image.frombytes("L", (bitmap.width, bitmap.rows), bytes(bitmap.buffer), "raw", "L", abs(bitmap.pitch))
            x = round(origin + (cursor + xoffset) * ppem / 1000) + slot.bitmap_left
            y = round(baseline - yoffset * ppem / 1000) - slot.bitmap_top
            if x < 0 or y < 0 or x + bitmap.width > image.width or y + bitmap.rows > image.height:
                raise ValueError(f"Proof ink exceeds canvas: {text}")
            image.paste("#252b2d", (x, y), mask)
        cursor += advance
    return width


def create_preview(out: Path, root: Path = ROOT) -> None:
    source, mirror = root / BASE, root / OUTPUT
    if hashlib.sha256(source.read_bytes()).hexdigest() != BASE_SHA256:
        raise ValueError("Expected the preserved Regular 1.270 TTF")
    if out.exists():
        raise FileExistsError("Choose a new output path")
    image = Image.new("RGB", (1800, 1190), "#f7f3ea")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "LEONARDUS SPECCHIO / RTL / 1.270", font=caption(26), fill="#325a49")
    draw_line(image, source, "Leonardus", "ltr", 120, 215, left=80)
    draw_line(image, mirror, "Leonardus", "rtl", 120, 215, right=1720)
    draw.text((80, 245), "Sinistra a destra: Leonardus Regular", font=caption(24), fill="#514b43")
    draw.text((1720, 245), "Destra a sinistra: Leonardus Specchio", font=caption(24), fill="#514b43", anchor="ra")
    draw.line((80, 300, 1720, 300), fill="#cfc4b1", width=2)
    for number, text in enumerate(LINES[1:]):
        baseline = 420 + number * 190
        draw_line(image, source, text, "ltr", 68, baseline, left=80)
        draw_line(image, mirror, text, "rtl", 68, baseline + 95, right=1720)
    draw.text((80, 1110), "Immagine speculare di Regular 1.270 / Reinterpretazione contemporanea, non scrittura autenticata / Contorni OFL 1.1",
              font=caption(22), fill="#514b43")
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "specimen/Leonardus-Specchio-Preview.png")
    create_preview(parser.parse_args().out)
