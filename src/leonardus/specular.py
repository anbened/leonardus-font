"""Derive the specular (mirror-image) right-to-left companion of Regular 1.270.

Every outline is reflected about the vertical axis of its own advance box, so
a line set right to left (bidi override) is the exact mirror image of the same
line set left to right. Metrics, kerning-free spacing and anchors are mirrored
with the outlines; glyphs of Bidi_Mirrored characters are left unreflected
because a right-to-left run already swaps them for their mirror partner.
"""
from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

BASE = "fonts/Leonardus-Regular-1.270.ttf"
BASE_SHA256 = "0d10af2c358d9a4884e41d910cbcb789f1648073f43f048ac20eee0d5afe1201"
OUTPUT = "fonts/Leonardus-Specchio-RTL-1.270.ttf"
NAMES = {1: "Leonardus Specchio", 2: "Regular", 3: "LeonardusSpecchio:1.270:Regular",
         4: "Leonardus Specchio Regular", 5: "Version 1.270", 6: "LeonardusSpecchio-Regular",
         16: "Leonardus Specchio", 17: "Regular"}


def unreflected_glyphs(font: TTFont) -> set[str]:
    """Glyphs whose characters the bidi algorithm already mirrors in RTL runs."""
    return {name for code, name in font.getBestCmap().items() if unicodedata.mirrored(chr(code))}


def _flip_anchor(anchor, advance):
    if anchor is not None:
        anchor.XCoordinate = advance - anchor.XCoordinate


def _flip_gpos(font: TTFont, advance) -> None:
    if "GPOS" not in font:
        return
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if sub.LookupType != 4:
                raise ValueError("Only mark-to-base positioning is mirrored")
            marks = sub.MarkCoverage.glyphs
            for glyph, record in zip(marks, sub.MarkArray.MarkRecord):
                _flip_anchor(record.MarkAnchor, advance(glyph))
            for glyph, record in zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord):
                for anchor in record.BaseAnchor:
                    _flip_anchor(anchor, advance(glyph))


def build_specular_font(output: Path, root: Path) -> dict:
    root, output = Path(root).resolve(), Path(output).resolve()
    source = root / BASE
    if hashlib.sha256(source.read_bytes()).hexdigest() != BASE_SHA256:
        raise ValueError("The preserved 1.270 TTF changed")
    if output.exists():
        raise FileExistsError("Choose a new output path; preserved fonts cannot be overwritten")
    with TTFont(source, recalcTimestamp=False) as font:
        glyf, hmtx, order = font["glyf"], font["hmtx"], font.getGlyphOrder()
        skip = unreflected_glyphs(font)
        advance = lambda name: hmtx[name][0]
        glyphs = font.getGlyphSet()
        flipped = {}
        for name in order:
            ttpen = pen = TTGlyphPen(None)
            if name not in skip:
                pen = TransformPen(ReverseContourPen(pen), (-1, 0, 0, 1, advance(name), 0))
            outline = DecomposingRecordingPen(glyphs)
            glyphs[name].draw(outline)
            outline.replay(pen)
            flipped[name] = ttpen.glyph()
        _flip_gpos(font, advance)
        for name in order:
            glyf[name] = flipped[name]
            flipped[name].recalcBounds(glyf)
            hmtx[name] = (advance(name), getattr(flipped[name], "xMin", 0))
        font["name"].names = [r for r in font["name"].names if r.nameID not in NAMES]
        for name_id, value in NAMES.items():
            font["name"].setName(value, name_id, 3, 1, 0x409)
            font["name"].setName(value, name_id, 1, 0, 0)
        if "DSIG" in font:
            del font["DSIG"]
        output.parent.mkdir(parents=True, exist_ok=True)
        font.save(output)
    return {"family": NAMES[1], "style": "Regular", "version": "1.270", "file": str(output),
            "base": BASE, "base_sha256": BASE_SHA256,
            "unreflected_glyphs": sorted(skip),
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "scope": "Mirror image of the 1.270 outlines and anchors; no new design or reading"}
