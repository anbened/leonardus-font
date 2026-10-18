"""Reproducible A4 print specimen of Regular 1.270, drawn from its TTF paths.

No Office export, manuscript images or substitute fonts in the sample text.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import unicodedata
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]
FONT_SHA256 = "0d10af2c358d9a4884e41d910cbcb789f1648073f43f048ac20eee0d5afe1201"
ACCENTS = "à è é ì ò ù À È É Ì Ò Ù"
SAMPLES = {
    12: ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz",
         "".join(chr(i) for i in range(32, 127)),
         "Leonardo Vinci Arte Natura Scienza Ragione Luce Movimento",
         "Jazz Junior Kilo Karate Uomo Universo Volo Weekend Whisky Xenon Yoga Zaino",
         "op pq qr pr po qo or ro pp qq rr oo", "0123456789 € 1.234,56 “prova” — l’esperienza",
         "° … – — ‘ ’ “ ” €\u00a0prova",
         ACCENTS, unicodedata.normalize("NFD", ACCENTS), "b̀ b́ ì í ù",
         "La natura insegna: osservare, ragionare e disegnare.",
         "Questa è una prova moderna di leggibilità e spaziatura."],
    18: ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz",
         "Leonardo Vinci Arte Natura Scienza Ragione", "Jazz Kilo Uomo Volo Weekend Xenon Yoga Zaino",
         "op pq qr pr po qo or ro pp qq rr oo", "0123456789 € 1.234,56 “prova” — l’esperienza",
         ACCENTS, unicodedata.normalize("NFD", ACCENTS), "b̀ b́ ì í ù",
         "La natura insegna: osservare, ragionare e disegnare."],
    36: ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "abcdefghijklm", "nopqrstuvwxyz",
         "Leonardo Vinci", "Natura Scienza", "op pq qr pp qq", "À È É Ì Ò Ù", "b̀ b́ ì í ù"],
    72: ["J K U V W", "X Y Z À Ù", "Vinci Volo", "È É Ì Ò", "b̀ b́ ì í ù"],
}


class PDFPen(BasePen):
    def __init__(self, glyphs, path):
        super().__init__(glyphs)
        self.path = path

    def _moveTo(self, p): self.path.moveTo(*p)
    def _lineTo(self, p): self.path.lineTo(*p)
    def _curveToOne(self, a, b, c): self.path.curveTo(*a, *b, *c)
    def _closePath(self): self.path.close()


def create_specimen(font_path: Path, output: Path) -> None:
    data = font_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != FONT_SHA256:
        raise ValueError("The print specimen requires the pinned Regular 1.270 TTF")
    if output.exists():
        raise FileExistsError("Choose a new output path")
    font = TTFont(font_path)
    upem = font["head"].unitsPerEm
    glyphs, order = font.getGlyphSet(), font.getGlyphOrder()
    shaper = hb.Font(hb.Face(data))
    shaper.scale = (upem, upem)
    hb.ot_font_set_funcs(shaper)

    def shape(text):
        if not text:
            return []
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(shaper, buf)
        if any(i.codepoint == 0 for i in buf.glyph_infos):
            raise ValueError("Missing glyph in print specimen")
        return list(zip(buf.glyph_infos, buf.glyph_positions))

    def width(text, pt):
        return sum(p.x_advance for _, p in shape(text)) * pt / upem

    def wrap(text, pt):
        # Character wrapping also permits inspection of the ASCII repertoire.
        line = ""
        for word in text.split(" "):
            proposed = (line + " " + word) if line else word
            if width(proposed, pt) > A4[0] - 90 and line:
                yield line
                line = ""
            for char in (" " + word if line else word):
                if line and width(line + char, pt) > A4[0] - 90:
                    yield line
                    line = ""
                line += char
        if line:
            yield line

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output), pagesize=A4, invariant=1)
    canvas.setTitle("Leonardus Regular 1.270 - campionario A4")
    canvas.setAuthor("Leonardus Lab")
    canvas.setSubject("Contorni originali OFL 1.1; campione contemporaneo LTR")
    for page, (pt, texts) in enumerate(SAMPLES.items(), 1):
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 16)
        canvas.drawString(45, 797, f"Leonardus Regular 1.270 | {pt} punti")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(45, 777, "A4, dimensioni reali 100%. Disattivare Adatta alla pagina.")
        canvas.drawString(45, 762, "Testo moderno; contorni del TTF, shaping HarfBuzz. Nessuna autenticazione storica.")
        y = 680 if pt == 72 else 714
        for text in texts:
            for line in wrap(text, pt):
                x = 45
                for info, pos in shape(line):
                    glyph = font["glyf"][order[info.codepoint]]
                    if hasattr(glyph, "xMax"):
                        left = x + (pos.x_offset + glyph.xMin) * pt / upem
                        right = x + (pos.x_offset + glyph.xMax) * pt / upem
                        bottom = y + (pos.y_offset + glyph.yMin) * pt / upem
                        top = y + (pos.y_offset + glyph.yMax) * pt / upem
                        if left < 35 or right > A4[0] - 35 or bottom < 95 or top > 748:
                            raise ValueError(f"Ink outside printable sample area: page {page}")
                    canvas.saveState()
                    canvas.translate(x + pos.x_offset * pt / upem, y + pos.y_offset * pt / upem)
                    canvas.scale(pt / upem, pt / upem)
                    path = canvas.beginPath()
                    glyphs[order[info.codepoint]].draw(PDFPen(glyphs, path))
                    canvas.drawPath(path, fill=1, stroke=0, fillMode=1)
                    canvas.restoreState()
                    x += pos.x_advance * pt / upem
                y -= pt * 1.4
            y -= 4
        canvas.setLineWidth(.5)
        canvas.line(45, 72, 45 + 50 * mm, 72)
        for x in (45, 45 + 50 * mm):
            canvas.line(x, 69, x, 75)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(45, 58, "Controllo scala: 50 mm. Stampa fisica da verificare.")
        canvas.drawRightString(A4[0] - 45, 58, f"{page}/4")
        canvas.drawString(45, 42, "Contorni OFL 1.1 | 26 minuscole ragionate; 26 maiuscole designed | 17 ottobre 2026")
        canvas.showPage()
    canvas.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=ROOT / "fonts/Leonardus-Regular-1.270.ttf")
    parser.add_argument("--out", type=Path, default=ROOT / "build/Leonardus-1270-Print-Specimen.pdf")
    args = parser.parse_args()
    create_specimen(args.font, args.out)
    print(args.out)
