"""The specular font is the exact mirror image of Regular 1.270, laid out right to left."""
from pathlib import Path

import freetype
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageOps
import pytest
import uharfbuzz as hb

from leonardus.specular import BASE, NAMES, build_specular_font, unreflected_glyphs

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "fonts/Leonardus-Specchio-RTL-1.270.ttf"
TEXT = "Leonardus Vinci Jazz (op) pq qr 1.234 À È É Ì Ò Ù à è é ì ò ù b̀ b́ € “x” — …"


def placements(path, text, direction):
    """(glyph name, absolute origin x including offset, advance, y offset) in visual order."""
    font = hb.Font(hb.Face(Path(path).read_bytes()))
    hb.ot_font_set_funcs(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = direction
    buf.script, buf.language = "Latn", "it"
    hb.shape(font, buf)
    order = TTFont(path).getGlyphOrder()
    pen_x, found = 0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        assert info.codepoint != 0
        found.append((order[info.codepoint], pen_x + pos.x_offset, pos.x_advance, pos.y_offset))
        pen_x += pos.x_advance
    return found, pen_x


def ink(path, name, size=1000):
    """Anti-aliased bitmap of one glyph at one pixel per font unit, with its box."""
    face = freetype.Face(str(path))
    face.set_pixel_sizes(0, size)
    face.load_glyph(face.get_name_index(name.encode()), freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
    glyph, bitmap = face.glyph, face.glyph.bitmap
    image = Image.frombytes("L", (bitmap.width, bitmap.rows), bytes(bitmap.buffer)) if bitmap.rows else None
    return image, glyph.bitmap_left, glyph.bitmap_top, glyph.advance.x // 64


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    path = tmp_path_factory.mktemp("specular") / "specular.ttf"
    build_specular_font(path, ROOT)
    return path


def test_build_is_reproducible_and_matches_the_distributed_font(built, tmp_path):
    second = tmp_path / "second.ttf"
    build_specular_font(second, ROOT)
    assert built.read_bytes() == second.read_bytes() == PUBLISHED.read_bytes()
    with pytest.raises(FileExistsError):
        build_specular_font(PUBLISHED, ROOT)


def test_names_repertoire_and_metrics(built):
    with TTFont(built) as mirror, TTFont(ROOT / BASE) as base:
        for name_id, expected in NAMES.items():
            assert mirror["name"].getDebugName(name_id) == expected
        assert mirror.getBestCmap() == base.getBestCmap()
        assert mirror.getGlyphOrder() == base.getGlyphOrder()
        assert "DSIG" not in mirror
        for tag in ("head", "hhea", "OS/2"):
            for field in ("unitsPerEm", "ascent", "descent", "sTypoAscender", "sTypoDescender",
                          "usWinAscent", "usWinDescent", "fontRevision"):
                if hasattr(base[tag], field):
                    assert getattr(mirror[tag], field) == getattr(base[tag], field)
        for name in base.getGlyphOrder():
            assert mirror["hmtx"][name][0] == base["hmtx"][name][0]
            box = mirror["glyf"][name]
            assert mirror["hmtx"][name][1] == getattr(box, "xMin", 0)
            assert box.numberOfContours >= 0


def test_every_glyph_renders_as_the_mirror_image_of_the_original(built):
    with TTFont(ROOT / BASE) as base:
        skip = unreflected_glyphs(base)
        names = base.getGlyphOrder()
        assert skip == {"uni0028", "uni0029", "uni003C", "uni003E",
                        "uni005B", "uni005D", "uni007B", "uni007D"}
    for name in names:
        old, left, top, advance = ink(ROOT / BASE, name)
        new, new_left, new_top, new_advance = ink(built, name)
        assert advance == new_advance and top == new_top or old is None, name
        if old is None:
            assert new is None
            continue
        expected = old if name in skip else ImageOps.mirror(old)
        expected_left = left if name in skip else advance - left - old.width
        assert abs(new_left - expected_left) <= 1 and new.size == expected.size, name
        diff = ImageChops.difference(new, expected)
        mismatched = sum(1 for value in diff.get_flattened_data() if value > 96)
        assert mismatched <= max(8, 0.002 * sum(1 for v in expected.get_flattened_data() if v > 96)), name


def test_mark_anchors_are_reflected(built):
    with TTFont(built) as mirror, TTFont(ROOT / BASE) as base:
        for font in (base, mirror):
            assert [r.FeatureTag for r in font["GPOS"].table.FeatureList.FeatureRecord] == ["mark"]
        for old, new in zip(base["GPOS"].table.LookupList.Lookup[0].SubTable,
                            mirror["GPOS"].table.LookupList.Lookup[0].SubTable):
            for glyph, a, b in zip(old.MarkCoverage.glyphs, old.MarkArray.MarkRecord, new.MarkArray.MarkRecord):
                assert b.MarkAnchor.XCoordinate == base["hmtx"][glyph][0] - a.MarkAnchor.XCoordinate
                assert b.MarkAnchor.YCoordinate == a.MarkAnchor.YCoordinate
            for glyph, a, b in zip(old.BaseCoverage.glyphs, old.BaseArray.BaseRecord, new.BaseArray.BaseRecord):
                for x, y in zip(a.BaseAnchor, b.BaseAnchor):
                    assert y.XCoordinate == base["hmtx"][glyph][0] - x.XCoordinate


def test_right_to_left_line_places_every_glyph_at_its_mirrored_position(built):
    text = TEXT.replace("(op)", "op").replace("1.234", "x")
    ltr, width = placements(ROOT / BASE, text, "ltr")
    rtl, mirrored_width = placements(built, text, "rtl")
    assert width == mirrored_width
    expected = [(g, width - x - advance, advance, y) for g, x, advance, y in ltr]
    assert sorted(rtl) == sorted(expected)


def test_brackets_are_not_reflected_twice(built):
    with TTFont(built) as mirror, TTFont(ROOT / BASE) as base:
        for code in (0x28, 0x29, 0x5B, 0x5D, 0x7B, 0x7D, 0x3C, 0x3E):
            name = mirror.getBestCmap()[code]
            assert mirror["glyf"][name].coordinates == base["glyf"][name].coordinates
