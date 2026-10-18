"""Comparison sheets for declared local samples, with originals left unchanged."""
from io import BytesIO
import hashlib
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .evidence import image_path, validated_samples
from .prepare import assert_distinct_files


def _font(size):
    candidates = ["DejaVuSans.ttf", str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/segoeui.ttf")]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow 10.0's default font does not accept a size.
        return ImageFont.load_default()


def _crop_views(row, source_path):
    """Use raw source pixels: EXIF orientation is deliberately not applied."""
    encoded = Path(source_path).read_bytes()
    if hashlib.sha256(encoded).hexdigest() != row["image_sha256"]:
        raise ValueError(f"Original image changed: {row['sample_id']}")
    x, y = int(row["crop_x"]), int(row["crop_y"])
    width, height = int(row["crop_width"]), int(row["crop_height"])
    with Image.open(BytesIO(encoded)) as source:
        original = source.crop((x, y, x + width, y + height)).convert("RGB")
    prepared = original.rotate(int(row["rotation_degrees"]), expand=True)
    if row["mirror_applied"] == "true":
        prepared = ImageOps.mirror(prepared)
    return original, prepared


def _draw_text(draw, xy, value, font, max_width, fill="#172638"):
    """Fit registry labels on one line without allowing long notes to overlap."""
    value = str(value)
    if draw.textlength(value, font=font) > max_width:
        while value and draw.textlength(value + "...", font=font) > max_width:
            value = value[:-1]
        value += "..."
    draw.text(xy, value, font=font, fill=fill)


def _wrap_text(draw, value, font, max_width):
    """Wrap complete credit text, retaining every character and explicit line break."""
    lines = []
    for paragraph in str(value).split("\n"):
        if not paragraph:
            lines.append("")
        while paragraph:
            if draw.textlength(paragraph, font=font) <= max_width:
                lines.append(paragraph)
                break
            low, high = 1, len(paragraph)
            while low < high:
                middle = (low + high + 1) // 2
                if draw.textlength(paragraph[:middle], font=font) <= max_width:
                    low = middle
                else:
                    high = middle - 1
            cut = low
            space = paragraph.rfind(" ", 0, cut)
            if space > 0:
                cut = space + 1
            lines.append(paragraph[:cut])
            paragraph = paragraph[cut:]
    return lines


def _paste_view(sheet, view, left, top, width, height):
    view.thumbnail((width, height), Image.Resampling.LANCZOS)
    sheet.paste(view, (left + (width - view.width) // 2,
                      top + (height - view.height) // 2))


def make_comparison(sources_path, evidence_path, output, character, sample_ids=None):
    """Render 4–10 samples of one character into a new PNG comparison sheet.

    A transformed view is a declared processing aid, never the historical original.
    Historical and synthetic samples cannot be combined in the same sheet.
    """
    sources_path, evidence_path, output = map(Path, (sources_path, evidence_path, output))
    if not isinstance(character, str) or len(character) != 1:
        raise ValueError("character must be exactly one Unicode character")
    rows = validated_samples(sources_path, evidence_path, check_images=True)
    by_id = {row["sample_id"]: row for row in rows}
    if sample_ids is None:
        selected = [row for row in rows if row["target_character"] == character]
    else:
        ids = list(sample_ids)
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate sample IDs are not allowed")
        unknown = [sample_id for sample_id in ids if sample_id not in by_id]
        if unknown:
            raise ValueError("unknown sample IDs: " + ", ".join(unknown))
        selected = [by_id[sample_id] for sample_id in ids]
    if any(row["target_character"] != character for row in selected):
        raise ValueError("all selected samples must have the requested target character")
    if not 4 <= len(selected) <= 10:
        raise ValueError("comparison requires 4 to 10 samples")
    kinds = {row["source_kind"] for row in selected}
    if len(kinds) != 1:
        raise ValueError("historical and synthetic samples cannot share a comparison sheet")
    if not kinds <= {"historical", "synthetic"}:
        raise ValueError("unsupported source kind")
    for row in selected:
        if row["rights_status"] not in {"PERMITTED_LOCAL", "SELF_CREATED"}:
            raise ValueError(f"sample {row['sample_id']} does not permit local comparison")
        if "private_comparison" not in row["permitted_uses"].split("|"):
            raise ValueError(f"sample {row['sample_id']} lacks private_comparison permission")
    if output.suffix.lower() != ".png":
        raise ValueError("comparison output must be a PNG file")
    for protected in [sources_path, evidence_path] + [
        image_path(evidence_path, row) for row in rows
    ]:
        assert_distinct_files(protected, output)
    if output.exists():
        raise ValueError("comparison output already exists; choose a new path")

    kind = next(iter(kinds))
    width, header_height, line_height = 1100, 116, 20
    title_font, font, small_font = _font(24), _font(16), _font(14)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    credits = []
    row_heights = []
    for row in selected:
        lines = _wrap_text(measure, f"Source image: {row['source_image_id']}", small_font, 1052)
        lines += _wrap_text(measure, f"Attribution: {row['attribution']}", small_font, 1052)
        credits.append(lines)
        row_heights.append(216 + line_height * len(lines) + 16)
    sheet = Image.new("RGB", (width, header_height + sum(row_heights) + 36), "white")
    draw = ImageDraw.Draw(sheet)
    designation = "SYNTHETIC ENGINEERING DEMO" if kind == "synthetic" else "HISTORICAL SOURCE SAMPLES"
    _draw_text(draw, (20, 12), f"{designation} | {character} U+{ord(character):04X}", title_font, 1060)
    draw.text((20, 48), "Sample metadata", font=font, fill="#172638")
    draw.text((340, 48), "Original pixel crop", font=font, fill="#172638")
    draw.text((730, 48), "Declared transformed view", font=font, fill="#172638")
    draw.text((20, 78), "Transformed views are processing aids; review status does not authenticate handwriting.",
              font=small_font, fill="#49596b")
    top = header_height
    for row, credit_lines, row_height in zip(selected, credits, row_heights):
        draw.rectangle((12, top, width - 12, top + row_height - 8), fill="#f1f4f7")
        labels = [
            row["sample_id"], f"Source: {row['source_id']}", f"Folio: {row['folio']}",
            f"Original direction: {row['original_direction']}",
            f"Review: {row['review_status']}", f"Confidence: {row['transcription_confidence']}",
            f"Rights: {row['rights_status']}",
            f"Rotate CCW: {row['rotation_degrees']} / mirror: {row['mirror_applied']}",
        ]
        for line, label in enumerate(labels):
            _draw_text(draw, (24, top + 12 + 24 * line), label, small_font, 295)
        original, prepared = _crop_views(row, image_path(evidence_path, row))
        _paste_view(sheet, original, 340, top + 12, 345, 200)
        _paste_view(sheet, prepared, 730, top + 12, 345, 200)
        for line, credit in enumerate(credit_lines):
            draw.text((24, top + 216 + line * line_height), credit, font=small_font, fill="#172638")
        top += row_height
    draw.text((20, sheet.height - 28), "Leonardus Lab | Local samples only | Originals preserved", font=small_font, fill="#49596b")
    encoded = BytesIO()
    sheet.save(encoded, format="PNG")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        destination.write(encoded.getvalue())
    return {"comparison_file": str(output), "character": character,
            "sample_ids": [row["sample_id"] for row in selected], "source_kind": kind}
