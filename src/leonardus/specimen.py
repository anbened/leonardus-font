"""Local TTF specimens with explicit coverage, point size and baseline checks."""
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from .preview import require_coverage
from .proposal import NAMES

WORDS = ("leonardo", "dare", "orlo", "nero", "anello", "donna", "ardore", "errore", "reale", "rondone")
LETTERS = "adelnor"
POINTS = (12, 18, 36, 72)
DPI = 96


def caption_font(size):
    for path in ("DejaVuSans.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def draw_font_line(draw, position, text, face, width, height):
    """Reject overflow rather than silently clip ink or substitute a character."""
    left, baseline = position
    box = draw.textbbox(position, text, font=face, anchor="ls")
    if box[0] < 0 or box[1] < 0 or box[2] > width or box[3] > height:
        raise ValueError(f"Specimen ink exceeds canvas: {text!r} {box}")
    draw.text(position, text, font=face, anchor="ls", fill="#242b2c")
    return list(box)


def make_specimens(font_file: Path, output: Path) -> dict:
    font_file, output = Path(font_file), Path(output)
    pairs = [" ".join(c + d for d in LETTERS) for c in LETTERS]
    text = " ".join(WORDS) + " " + " ".join(pairs)
    require_coverage(font_file, text)
    with TTFont(font_file) as font:
        family = font["name"].getDebugName(1)
        if (font["name"].getDebugName(6) != NAMES["psName"]
                or set(font.getBestCmap()) != set(map(ord, " " + LETTERS))):
            raise ValueError("This pilot specimen requires an explicitly unapproved font")
    if output.exists():
        raise ValueError("Choose a new specimen output directory")
    output.mkdir(parents=True)
    receipt = {"font": str(font_file), "family": family, "dpi": DPI,
               "scale": "1 image pixel at 96 DPI; ppem=round(pt*96/72)",
               "status": "unapproved_proposal", "pages": {}}
    for pt in POINTS:
        ppem = round(pt * DPI / 72)
        face = ImageFont.truetype(str(font_file), ppem, layout_engine=ImageFont.Layout.BASIC)
        sheet = Image.new("RGB", (1600, 1550), "#fbf8f1")
        draw = ImageDraw.Draw(sheet)
        draw.text((50, 24), f"LEONARDUS / PROPOSTA V3 NON APPROVATA / {pt} pt", font=caption_font(28), fill="#172638")
        draw.text((50, 72), f"TTF effettivo | {DPI} DPI | {ppem} px/em | scala 1:1 | nessun fallback", font=caption_font(21), fill="#172638")
        draw.text((50, 108), "Repertorio: a d e l n o r + spazio. M1B/M2 aperti; nessuna autenticazione.", font=caption_font(21), fill="#172638")
        draw.text((50, 168), "MONOLINEA", font=caption_font(22), fill="#172638")
        boxes = [draw_font_line(draw, (60, 275), "leonardo dare orlo nero", face, 1540, 1170)]
        draw.text((50, 325), "MULTILINEA / LE STESSE DIECI PAROLE A OGNI DIMENSIONE", font=caption_font(22), fill="#172638")
        lines = ["leonardo dare orlo nero", "anello donna ardore", "errore reale rondone"]
        leading = max(32, ppem)
        for index, line in enumerate(lines):
            boxes.append(draw_font_line(draw, (60, 435 + index * leading), line, face, 1540, 1170))
        draw.text((50, 665), "49 COPPIE / SPAZI LATERALI, SENZA KERNING", font=caption_font(22), fill="#172638")
        for index, line in enumerate(pairs):
            boxes.append(draw_font_line(draw, (60, 780 + index * max(62, ppem + 12)), line, face, 1540, 1460))
        draw.text((50, 1480), "Disegno originale da riferimenti candidati BNE MSS/8937; usi/crediti in RIGHTS.md.", font=caption_font(20), fill="#172638")
        path = output / f"specimen-{pt}pt.png"
        sheet.save(path, dpi=(DPI, DPI))
        receipt["pages"][path.name] = {"pt": pt, "ppem": ppem, "ink_boxes": boxes, "multiline_text": lines}
    return receipt
