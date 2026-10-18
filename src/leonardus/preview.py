"""Create a proof sheet. The actual font is used to render the text."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


def require_coverage(font_file: Path, text: str):
    with TTFont(font_file) as face:
        missing = sorted(set(map(ord, text.replace("\n", ""))) - face.getBestCmap().keys())
    if missing:
        raise ValueError("Missing characters (no fallback): " + ", ".join(f"U+{c:04X}" for c in missing))


def make_preview(font_file: Path, output: Path, text: str = "Leonardo"):
    font_file, output = Path(font_file), Path(output)
    require_coverage(font_file, text + text.lower())
    image = Image.new("RGB", (1600, 900), "#f5f0e7")
    draw = ImageDraw.Draw(image)
    for caption_path in ("DejaVuSans.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            caption_font = ImageFont.truetype(caption_path, 27)
            head_font = ImageFont.truetype(caption_path, 46)
            break
        except OSError:
            continue
    else:
        caption_font = ImageFont.load_default()
        head_font = caption_font
    experiment = ImageFont.truetype(str(font_file), 200)
    draw.text((100, 80), "LEONARDUS LAB", fill="#554b42", font=head_font)
    draw.line([(100, 152), (1500, 152)], fill="#c4b3a3", width=2)
    draw.text((100, 212), text, font=experiment, fill="#24211d")
    draw.text((100, 515), text.lower(), font=experiment, fill="#42382e")
    with TTFont(font_file) as face:
        proposal = "Unapproved" in face["name"].getDebugName(1)
    notice = ("UNAPPROVED DESIGN PROPOSAL — human M1B/M2 review pending" if proposal else
              "ENGINEERING DEMO ONLY — not traced from Leonardo's manuscripts")
    draw.text((100, 795), notice,
              fill="#855f50", font=caption_font)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    return str(output)
