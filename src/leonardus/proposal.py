"""Explicit experimental proposal build; never authorizes historical derivation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from .evidence import validated_samples
from .fontbuild import _build_font, _svg_to_glyph

CHARACTERS = "adelnor"
FAMILY = "Leonardus Proposal V3 Unapproved"
NAMES = {
    "familyName": FAMILY,
    "styleName": "Regular",
    "uniqueFontIdentifier": "LeonardusLab:ProposalV3-Unapproved:0.103",
    "fullName": FAMILY + " Regular",
    "psName": "LeonardusLab-ProposalV3-Unapproved",
    "version": "Version 0.103; unapproved experimental proposal",
    "designer": "Leonardus Lab; original project outlines with agent assistance",
    "description": "Unapproved original design inspired by candidate samples; NOT authenticated handwriting. Human M1B/M2 review pending. No museum endorsement.",
    "licenseDescription": "No final font license selected. BNE references retain CC BY 4.0 attribution; see accompanying RIGHTS.md. This proposal is supplied for private project review.",
    "licenseInfoURL": "https://github.com/anbened/leonardus-font/blob/main/docs/LICENSES.md",
    "copyright": "Original project outlines. Candidate references: BNE MSS/8937, folios 1r-4r. Imágenes procedentes de los fondos de la Biblioteca Nacional de España. CC BY 4.0; independent design, scaling, spacing and quadratic conversion. https://bnedigital.bne.es/bd/card?oid=0000040157&site=bdh https://creativecommons.org/licenses/by/4.0/",
}


def text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def validate_proposal(directory: Path, sources: Path, evidence: Path) -> dict:
    directory = Path(directory)
    manifest = json.loads((directory / "design_manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("status") != "unapproved_proposal" or manifest.get("human_review") is not False
            or manifest.get("variant") != "v3-readable-angular"):
        raise ValueError("Only the unapproved V3 proposal is supported; historical review cannot be inferred")
    if manifest.get("font_names") != NAMES:
        raise ValueError("Proposal font names and notices must remain explicitly unapproved")
    if set(manifest.get("glyphs", {})) != set(CHARACTERS):
        raise ValueError("Proposal repertoire must be exactly a d e l n o r")
    if {p.name for p in directory.iterdir() if p.suffix.lower() == ".svg"} != {f"{c}.svg" for c in CHARACTERS}:
        raise ValueError("SVG repertoire must match the seven proposal letters")
    widths = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
    if set(widths) != set(CHARACTERS):
        raise ValueError("Metrics repertoire mismatch")
    rows = {r["sample_id"]: r for r in validated_samples(sources, evidence)}
    for c, record in manifest["glyphs"].items():
        if record.get("classification") != "proposal_from_candidates" or record.get("review_status") != "pending":
            raise ValueError("Proposals cannot claim sampled/normalized derivation or human approval")
        if record.get("codepoint") != f"U+{ord(c):04X}" or record.get("file") != f"{c}.svg":
            raise ValueError("Proposal character/file mismatch")
        ids = record.get("sample_ids", [])
        if (not ids or len(set(ids)) != len(ids) or record.get("display_anchor") not in ids
                or any(i not in rows or rows[i]["target_character"] != c for i in ids)):
            raise ValueError("Candidate references must exist and match the letter")
        if any(rows[i]["source_kind"] != "historical" or rows[i]["source_id"] != "BNE_MADRID_I"
               or rows[i]["review_status"] not in {"candidate", "reviewed"} for i in ids):
            raise ValueError("V3 references require historical BNE candidates or human-reviewed samples; no rejected or synthetic samples")
        if not record.get("normalizations"):
            raise ValueError("Normalizations must be declared")
        if text_sha256(directory / record["file"]) != record.get("svg_sha256"):
            raise ValueError("Proposal SVG hash mismatch")
        advance = record.get("advance")
        if type(advance) is not int or not 100 <= advance <= 1500 or type(widths[c]) is not int or widths[c] != advance:
            raise ValueError("Advance must be an integer matching metrics.json")
        glyph = _svg_to_glyph(directory / record["file"])
        if glyph.numberOfContours <= 0:
            raise ValueError("Proposal outline is empty")
        if record.get("contour_count") != glyph.numberOfContours:
            raise ValueError("Proposal contour count mismatch")
        glyph.recalcBounds(None)
        bounds = [glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax]
        if (record.get("bounds") != bounds or record.get("lsb") != glyph.xMin
                or record.get("rsb") != advance - glyph.xMax):
            raise ValueError("Proposal bounds/sidebearings mismatch after quadratic conversion")
        if glyph.xMin < 0 or advance < glyph.xMax or glyph.yMin < -200 or glyph.yMax > 800:
            raise ValueError("Proposal outline exceeds its declared design cell")
    space = manifest.get("space", {})
    if (space.get("classification") != "system" or space.get("codepoint") != "U+0020"
            or space.get("sample_ids") != [] or space.get("review_status") != "technical"
            or type(space.get("advance")) is not int or not 100 <= space["advance"] <= 600
            or space.get("lsb") != 0 or space.get("rsb") != space["advance"]
            or space.get("file") is not None or space.get("svg_sha256") is not None):
        raise ValueError("Space must be technical, with no historical attribution")
    if manifest.get("notdef") != {"classification": "system", "sample_ids": [], "advance": 600,
                                  "review_status": "technical", "source": "leonardus.fontbuild._notdef_glyph"}:
        raise ValueError(".notdef must remain the technical compiler glyph")
    return manifest


def build_proposal(directory: Path, output: Path, sources: Path, evidence: Path) -> dict:
    output = Path(output)
    if output.resolve().name.casefold() == "leonardus-engineeringdemo.ttf":
        raise ValueError("Cannot overwrite the engineering demo")
    if output.exists():
        with TTFont(output) as font:
            if font["name"].getDebugName(6) != NAMES["psName"]:
                raise ValueError("Cannot overwrite a font from another category")
    manifest = validate_proposal(directory, sources, evidence)
    result = _build_font(directory, output, FAMILY, proposal=manifest)
    with TTFont(output) as font:
        if (set(font.getBestCmap()) != set(map(ord, " " + CHARACTERS))
                or len(font.getGlyphOrder()) != 9 or font["name"].getDebugName(6) != NAMES["psName"]):
            raise ValueError("Compiled proposal repertoire/category mismatch")
    return result
