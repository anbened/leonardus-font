"""Build the specular right-to-left companion of the preserved Regular 1.270."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from leonardus.specular import build_specular_font

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build/Leonardus-Specchio-RTL-1.270.ttf")
    args = parser.parse_args()
    print(json.dumps(build_specular_font(args.out, ROOT), indent=2))
