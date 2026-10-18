"""The final family name must not change drawing, layout or archived checkpoints."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from examples.finalize_regular_1270 import BASE, NAMES, RECEIPT, build_named_font

ROOT = Path(__file__).resolve().parents[1]


def test_naming_is_reproducible_and_all_non_name_tables_are_preserved(tmp_path):
    first, second = tmp_path / "first.ttf", tmp_path / "second.ttf"
    build_named_font(first, ROOT)
    build_named_font(second, ROOT)
    assert first.read_bytes() == second.read_bytes() == (ROOT / "fonts/Leonardus-Regular-1.270.ttf").read_bytes()
    with TTFont(first) as named, TTFont(ROOT / BASE) as base:
        assert set(named.keys()) == set(base.keys())
        for tag in named.keys():
            if tag not in {"GlyphOrder", "name", "head"}:
                assert named.getTableData(tag) == base.getTableData(tag), tag
        for field, value in base["head"].__dict__.items():
            if field != "checkSumAdjustment":
                assert named["head"].__dict__[field] == value
        for name_id, expected in NAMES.items():
            assert named["name"].getDebugName(name_id) == expected
            assert all(record.toUnicode() == expected for record in named["name"].names
                       if record.nameID == name_id)
        assert len(named.getBestCmap()) == 119 and len(named.getGlyphOrder()) == 121
    for points in (12, 18, 36, 72):
        shaped = []
        for path in (ROOT / BASE, first):
            font = hb.Font(hb.Face(path.read_bytes()))
            font.scale = (points * 64, points * 64)
            hb.ot_font_set_funcs(font)
            buf = hb.Buffer()
            buf.add_str("Leonardus Vinci Jazz op pq qr À È É Ì Ò Ù b̀ b́ ì í ù")
            buf.guess_segment_properties()
            hb.shape(font, buf)
            shaped.append([(i.codepoint, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
                           for i, p in zip(buf.glyph_infos, buf.glyph_positions)])
        assert shaped[0] == shaped[1]
    with pytest.raises(FileExistsError):
        build_named_font(ROOT / BASE, ROOT)


def test_naming_rejects_an_expanded_approval_scope(tmp_path):
    for name in (BASE, RECEIPT):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    path = tmp_path / RECEIPT
    approval = json.loads(path.read_text(encoding="utf-8"))
    approval["outline_changes"] = True
    path.write_text(json.dumps(approval), encoding="utf-8")
    with pytest.raises(ValueError, match="naming-only"):
        build_named_font(tmp_path / "invalid.ttf", tmp_path)
