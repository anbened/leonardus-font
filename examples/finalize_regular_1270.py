"""Apply the approved family name to the preserved Regular 1.270 checkpoint."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = "data/human_family_naming_review_2026-10-17.json"
BASE = "fonts/Leonardus-1270-Regular.ttf"
BASE_SHA256 = "3e1e7e6ac2416f6f321b302b46fb1b598ac04015663d731324224ce0221c240d"
NAMES = {1: "Leonardus", 2: "Regular", 3: "Leonardus:1.270:Regular",
         4: "Leonardus Regular", 5: "Version 1.270", 6: "Leonardus-Regular",
         16: "Leonardus", 17: "Regular"}


def build_named_font(output: Path, root: Path = ROOT) -> dict:
    root, output = Path(root).resolve(), Path(output).resolve()
    approval = json.loads((root / RECEIPT).read_text(encoding="utf-8"))
    if (approval["status"] != "human_family_naming_selected"
            or approval["scope"] != "font_naming_only" or not approval["quote"].strip()
            or approval["base_font"] != BASE or approval["base_font_sha256"] != BASE_SHA256
            or (approval["family"], approval["style"], approval["version"], approval["postscript_name"])
                != ("Leonardus", "Regular", "1.270", "Leonardus-Regular")
            or any(approval[k] is not False for k in ("outline_changes", "metric_changes",
                      "historical_evidence_changes", "public_release_approved"))):
        raise ValueError("Expected the explicit naming-only decision")
    source = root / BASE
    if hashlib.sha256(source.read_bytes()).hexdigest() != BASE_SHA256:
        raise ValueError("The preserved 1.270 checkpoint changed")
    if output.exists():
        raise FileExistsError("Choose a new output path; preserved fonts cannot be overwritten")
    with TTFont(source, recalcTimestamp=False) as font:
        if font["name"].getDebugName(1) != "Leonardus 1270":
            raise ValueError("Unexpected source family")
        for record in list(font["name"].names):
            if record.nameID in NAMES:
                font["name"].setName(NAMES[record.nameID], record.nameID,
                                     record.platformID, record.platEncID, record.langID)
        for name_id, value in NAMES.items():
            font["name"].setName(value, name_id, 3, 1, 0x409)
            font["name"].setName(value, name_id, 1, 0, 0)
        output.parent.mkdir(parents=True, exist_ok=True)
        font.save(output)
    return {"family": "Leonardus", "style": "Regular", "version": "1.270",
            "file": str(output), "base_sha256": BASE_SHA256,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "scope": "Naming only; no change to outlines, metrics or shaping"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build/Leonardus-Regular-1.270.ttf")
    args = parser.parse_args()
    print(json.dumps(build_named_font(args.out), indent=2))
