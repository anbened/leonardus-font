"""Validate a proposed repertoire and compare it with a font's Unicode cmap.

A mapped codepoint does not establish usable contours, accent positioning or
historical evidence. Those remain separate release checks.
"""
from __future__ import annotations

import json
from pathlib import Path

from fontTools.ttLib import TTFont


def audit_charset(manifest_path: Path, font_path: Path | None = None) -> dict:
    manifest_path = Path(manifest_path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid repertoire JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("Repertoire must be a JSON object")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported repertoire schema_version; expected 1")
    for field in ("id", "status", "direction", "style"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise ValueError(f"Repertoire requires a nonempty {field}")
    if manifest["status"] not in ("proposed", "agreed"):
        raise ValueError("Repertoire status must be proposed or agreed")
    if manifest["direction"] != "ltr" or manifest["style"] != "Regular":
        raise ValueError("Repertoire must describe a left-to-right Regular style")
    groups = manifest.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("Repertoire requires a nonempty groups list")

    required = set()
    group_counts = {}
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError("Each repertoire group must be an object")
        group_id = group.get("id")
        if not isinstance(group_id, str) or not group_id.strip():
            raise ValueError("Each repertoire group requires a nonempty id")
        if group_id in group_counts:
            raise ValueError(f"Duplicate repertoire group: {group_id}")
        label = group.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"Group {group_id} requires a nonempty label")
        codepoints = group.get("codepoints")
        if not isinstance(codepoints, list) or not codepoints:
            raise ValueError(f"Group {group_id} requires a nonempty codepoints list")
        for codepoint in codepoints:
            if (type(codepoint) is not int or not 0 <= codepoint <= 0x10FFFF
                    or 0xD800 <= codepoint <= 0xDFFF):
                raise ValueError(f"Invalid Unicode scalar in group {group_id}: {codepoint!r}")
            if codepoint in required:
                raise ValueError(f"Duplicate codepoint: U+{codepoint:04X}")
            required.add(codepoint)
        group_counts[group_id] = len(codepoints)

    result = {
        "manifest": str(manifest_path),
        "repertoire_id": manifest["id"],
        "status": manifest["status"],
        "required_count": len(required),
        "group_counts": group_counts,
        "required_codepoints": [f"U+{cp:04X}" for cp in sorted(required)],
        "coverage_complete": None,
        "coverage_basis": "Unicode cmap only; no contour, shaping or historical claim",
    }
    if font_path is not None:
        with TTFont(str(font_path)) as font:
            # A mapping to .notdef is not useful coverage.
            cmap = font.getBestCmap() or {}
            mapped = {cp for cp, name in cmap.items() if name != ".notdef"}
        missing = sorted(required - mapped)
        result.update({
            "font": str(font_path),
            "mapped_count": len(mapped),
            "covered_count": len(required & mapped),
            "missing_count": len(missing),
            "missing_codepoints": [f"U+{cp:04X}" for cp in missing],
            "missing_characters": "".join(chr(cp) for cp in missing),
            "coverage_complete": not missing,
        })
    return result
