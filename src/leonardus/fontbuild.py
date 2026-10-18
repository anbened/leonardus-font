"""Reproducibly build a TrueType font from hand-reviewed, filled SVG outlines.

Each SVG is stored in 1000x1000 SVG user units. SVG (0, 800) is the
baseline; resulting font uses 1000 units/em, ascender 800, descender -200.
Only <path> elements are imported; stroke-only SVG paths are not supported.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import epoch_diff
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import SVGPath
from fontTools.ttLib import TTFont

UPM = 1000
ASCENDER = 800
DESCENDER = -200
DEFAULT_SOURCE_DATE_EPOCH = 0


def _name_to_unicode(name: str) -> int:
    if len(name) == 1:
        return ord(name)
    if name.startswith("uni") and len(name) == 7:
        return int(name[3:], 16)
    if name.startswith("u") and len(name) in (6, 7):
        return int(name[1:], 16)
    raise ValueError(f"Unsupported glyph filename {name!r}; use one character or uniXXXX/uXXXXX")


def _blank_glyph():
    return TTGlyphPen(None).glyph()


def _notdef_glyph():
    pen = TTGlyphPen(None)
    pen.moveTo((80, 0))
    pen.lineTo((80, 700))
    pen.lineTo((510, 700))
    pen.lineTo((510, 0))
    pen.closePath()
    return pen.glyph()


def _validate_svg(path: Path):
    root = ET.parse(path).getroot()
    if root.tag not in ("svg", "{http://www.w3.org/2000/svg}svg"):
        raise ValueError(f"Expected SVG root in {path}")
    try:
        view_box = [float(v) for v in root.get("viewBox", "").replace(",", " ").split()]
    except ValueError as exc:
        raise ValueError(f"Invalid viewBox in {path}") from exc
    if view_box != [0, 0, 1000, 1000]:
        raise ValueError(f"SVG must have viewBox='0 0 1000 1000': {path}")
    for dimension in ("width", "height"):
        if dimension in root.attrib and root.get(dimension) not in ("1000", "1000px"):
            raise ValueError(f"SVG {dimension} must be 1000: {path}")

    # Keep the accepted SVG subset explicit: unsupported rendering must never
    # disappear silently when converting a drawing into font outlines.
    allowed_attributes = {
        "svg": {"width", "height", "viewBox", "version", "id", "fill", "fill-rule", "stroke"},
        "path": {"d", "id", "fill", "fill-rule", "stroke"},
        "title": {"id"},
        "desc": {"id"},
    }
    for element in root.iter():
        tag = element.tag.removeprefix("{http://www.w3.org/2000/svg}")
        if tag not in allowed_attributes or (tag == "svg" and element is not root):
            raise ValueError(f"Unsupported SVG element {element.tag!r} in {path}; use paths only")
        if element is not root and len(element):
            raise ValueError(f"Unsupported nested SVG elements in {path}; use direct paths only")
        unsupported = set(element.attrib) - allowed_attributes[tag]
        if unsupported:
            raise ValueError(f"Unsupported SVG attributes {sorted(unsupported)} in {path}")
        if tag not in ("svg", "path"):
            continue
        if element.get("stroke", "none").strip().lower() != "none":
            raise ValueError(f"SVG strokes are not supported: {path}")
        fill = element.get("fill", root.get("fill", "black")).strip().lower()
        if fill in ("none", "transparent", "") or fill.startswith("url("):
            raise ValueError(f"SVG contours must be filled: {path}")
        if element.get("fill-rule", root.get("fill-rule", "nonzero")) != "nonzero":
            raise ValueError(f"SVG must use nonzero fill-rule: {path}")
    return root


def _svg_to_glyph(path: Path):
    root = _validate_svg(path)
    # SVG y axis goes down; font y axis goes up. SVG baseline y=800.
    # Convert any SVG cubic splines to TrueType quadratics within 1 UPM unit.
    raw_pen = TTGlyphPen(None)
    quadratic_pen = Cu2QuPen(raw_pen, max_err=1.0)
    # Some SVG authoring tools use the svg namespace, SVGPath handles it.
    recording = RecordingPen()
    SVGPath.fromstring(ET.tostring(root), transform=(1, 0, 0, -1, 0, ASCENDER)).draw(recording)
    for command, points in recording.value:
        if command == "endPath":
            raise ValueError(f"SVG contours must be explicitly closed with Z: {path}")
        if any(not math.isfinite(value) for point in points for value in point):
            raise ValueError(f"SVG coordinates must be finite: {path}")
    recording.replay(quadratic_pen)
    return raw_pen.glyph()


def _build_timestamp() -> int:
    value = os.environ.get("SOURCE_DATE_EPOCH", str(DEFAULT_SOURCE_DATE_EPOCH))
    try:
        timestamp = int(value)
    except ValueError as exc:
        raise ValueError("SOURCE_DATE_EPOCH must be a nonnegative integer Unix timestamp") from exc
    if timestamp < 0 or timestamp - epoch_diff > 0xFFFFFFFFFFFFFFFF:
        raise ValueError("SOURCE_DATE_EPOCH is outside the supported timestamp range")
    return timestamp - epoch_diff


def build_font(glyph_dir: Path, output: Path, family: str = "Leonardus Lab Demo") -> dict:
    if (Path(glyph_dir) / "design_manifest.json").exists():
        raise ValueError("Design proposals require build-proposal and its validated manifest")
    output = Path(output)
    if output.resolve().name.casefold() == "leonardus-proposalv3-unapproved.ttf":
        raise ValueError("The proposal output is reserved for build-proposal")
    if output.exists():
        with TTFont(output) as font:
            if font["name"].getDebugName(6) == "LeonardusLab-ProposalV3-Unapproved":
                raise ValueError("Cannot overwrite a proposal with a generic build")
            if (font["name"].getDebugName(6) or "").startswith("LeonardusLab-Alpha"):
                raise ValueError("Cannot overwrite a Regular alpha with a generic build")
            if font["name"].getDebugName(6) == "LeonardusLab-Regular":
                raise ValueError("Cannot overwrite a Regular release with a generic build")
    return _build_font(glyph_dir, output, family)


def _build_font(glyph_dir: Path, output: Path, family: str, proposal=None) -> dict:
    """Geometry compiler; proposal settings are supplied by the validated wrapper."""
    glyph_dir, output = Path(glyph_dir), Path(output)
    paths = sorted(path for path in glyph_dir.iterdir() if path.suffix.lower() == ".svg")
    if not paths:
        raise ValueError(f"No SVG files found in {glyph_dir}")
    filenames = [path.name.casefold() for path in paths]
    if len(filenames) != len(set(filenames)):
        raise ValueError("SVG filenames collide on case-insensitive filesystems; use Unicode names")
    timestamp = _build_timestamp()

    metrics_file = glyph_dir / "metrics.json"
    if not metrics_file.exists():
        raise FileNotFoundError(f"Missing {metrics_file}; specify each glyph advance width")
    widths = json.loads(metrics_file.read_text(encoding="utf-8"))
    cmap = {}
    glyphs = {".notdef": _notdef_glyph(), "space": _blank_glyph()}
    adv = {".notdef": 600, "space": proposal["space"]["advance"] if proposal else 300}
    for path in paths:
        codepoint = _name_to_unicode(path.stem)
        name = f"uni{codepoint:04X}" if codepoint <= 0xFFFF else f"u{codepoint:05X}"
        if name in glyphs or codepoint == 32:
            raise ValueError(f"Duplicate character: {path.name}")
        if path.stem not in widths:
            raise ValueError(f"Missing advance width in metrics.json: {path.stem}")
        advance = int(widths[path.stem])
        if not 100 <= advance <= 1500:
            raise ValueError(f"Invalid advance width for {path.stem}: {advance}")
        glyph = _svg_to_glyph(path)
        if not glyph.numberOfContours:
            raise ValueError(f"No filled closed contours in {path}")
        glyphs[name] = glyph
        cmap[codepoint] = name
        adv[name] = advance

    glyph_order = [".notdef", "space"] + [cmap[k] for k in sorted(cmap)]
    fb = FontBuilder(UPM, isTTF=True)
    fb.font["head"].created = timestamp
    fb.font["head"].modified = timestamp
    fb.font.recalcTimestamp = False
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({32: "space", **cmap})
    fb.setupGlyf(glyphs)
    # Glyf bounds need recalc after glyph table registration.
    glyf = fb.font["glyf"]
    horizontal = {}
    for name in glyph_order:
        glyph = glyf[name]
        glyph.recalcBounds(glyf)
        horizontal[name] = (adv[name], getattr(glyph, "xMin", 0))
    fb.setupHorizontalMetrics(horizontal)
    ascent, descent = ASCENDER, DESCENDER
    if proposal:
        ascent = max(700, max(getattr(glyf[n], "yMax", 0) for n in glyph_order)) + 80
        descent = min(0, min(getattr(glyf[n], "yMin", 0) for n in glyph_order)) - 80
    fb.setupHorizontalHeader(ascent=ascent, descent=descent, lineGap=0)
    names = {
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"LeonardusLab: {family} Regular 0.1.0",
        "fullName": f"{family} Regular",
        "psName": "LeonardusLab-EngineeringDemo" if "Demo" in family else "LeonardusLab-Regular",
        "version": "Version 0.1.0",
        "designer": "Leonardus Lab (experimental)",
        "description": "Engineering test; NOT a paleographic reconstruction of Leonardo da Vinci.",
    }
    if proposal:
        names.update(proposal["font_names"])
        fb.font["head"].fontRevision = 0.103
    fb.setupNameTable(names)
    fb.setupOS2(sTypoAscender=ascent, sTypoDescender=descent,
                sTypoLineGap=0, usWinAscent=ascent, usWinDescent=-descent,
                sxHeight=360 if proposal else 450, sCapHeight=0 if proposal else 650)
    fb.setupPost()
    fb.setupDummyDSIG()
    output.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(output))
    # Read back from disk instead of assuming success.
    font = TTFont(str(output))
    best = font.getBestCmap()
    assert all(k in best for k in cmap), "Cmap verification failed"
    result = {
        "file": str(output), "family": family, "version": "0.1.0",
        "glyph_count": len(font.getGlyphOrder()), "mapped_characters": len(cmap),
        "true_type_glyf_table": "glyf" in font,
        "covered_characters": "".join(chr(c) for c in sorted(cmap)),
        "missing_historical_evidence": "Demo geometry is synthetic; no manuscript-derived glyphs",
    }
    if proposal:
        result.update(version="0.103", status="unapproved_proposal",
                      mapped_characters=len(best),
                      covered_characters="".join(chr(c) for c in sorted(best)),
                      missing_historical_evidence="Candidate references only; no human approval or authentication")
    font.close()
    return result
