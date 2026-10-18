"""Draw the repository preview directly from the pinned Regular 1.270 TTF."""
from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

from regular_specimen import ProofRenderer, caption

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts/Leonardus-Regular-1.270.ttf"
FONT_SHA256 = "0d10af2c358d9a4884e41d910cbcb789f1648073f43f048ac20eee0d5afe1201"


def create_preview() -> None:
    if hashlib.sha256(FONT.read_bytes()).hexdigest() != FONT_SHA256:
        raise ValueError("Expected the preserved Regular 1.270 TTF")
    image = Image.new("RGB", (1800, 1040), "#f7f3ea")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "LEONARDUS REGULAR / 1.270", font=caption(26), fill="#325a49")
    ProofRenderer(FONT, 180).line(image, (80, 290), "Leonardus")
    draw.text((80, 335), "Un carattere contemporaneo ispirato alla grafia documentata di Leonardo da Vinci.",
              font=caption(28), fill="#514b43")
    draw.line((80, 408, 1720, 408), fill="#cfc4b1", width=2)
    for text, baseline in (("Arte, scienza e immaginazione.", 525),
                           ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 650),
                           ("abcdefghijklmnopqrstuvwxyz", 760),
                           ("à è é ì ò ù   0123456789   € 1.234,56", 875)):
        renderer = ProofRenderer(FONT, 74)
        if renderer.width(text) > 1640:
            raise ValueError("Preview line exceeds the available width")
        renderer.line(image, (80, baseline), text)
    draw.text((80, 963), "Da sinistra a destra / Contorni originali OFL 1.1 / Reinterpretazione documentata",
              font=caption(24), fill="#514b43")
    image.save(ROOT / "specimen/Leonardus-Preview.png")


if __name__ == "__main__":
    create_preview()
