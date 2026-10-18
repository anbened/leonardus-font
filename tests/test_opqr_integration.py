"""Verify the exact human selection and preserve its limited approval scope."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from leonardus.fontbuild import _svg_to_glyph
from leonardus.lowercase import sha
from leonardus.opqr import MANIFEST, SELECTION, build_integration, validate_integration

ROOT = Path(__file__).resolve().parents[1]


def test_selected_integration_is_exact_reproducible_and_preserves_other_designs(tmp_path):
    first, second = tmp_path/'first.ttf', tmp_path/'second.ttf'
    build_integration(first, ROOT)
    build_integration(second, ROOT)
    assert first.read_bytes() == second.read_bytes() == (ROOT/'fonts/Leonardus-1210-Regular.ttf').read_bytes()
    document = validate_integration(ROOT)
    with TTFont(first) as font, TTFont(ROOT/document['base_font']) as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = {n for n in font.getGlyphOrder()
                   if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
        assert changed == {f'uni{ord(c):04X}' for c in 'opqrò'}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        for char, variant in SELECTION.items():
            record = document['glyphs'][char]
            assert record['variant'] == variant
            expected = _svg_to_glyph(ROOT/record['file'])
            expected.recalcBounds(None)
            assert expected.compile(font['glyf']) == font['glyf'][font.getBestCmap()[ord(char)]].compile(font['glyf'])
        assert font['name'].getDebugName(1) == 'Leonardus 1210'
        assert font['OS/2'].fsType == 0
        o = font['glyf']['uni006F']
        accent = font['glyf']['uni00F2'].components[1]
        assert (accent.x, accent.y) == (round((o.xMin+o.xMax)/2+35), o.yMax+60)
        assert font['hmtx']['uni00F2'] == font['hmtx']['uni006F']
        shaper = hb.Font(hb.Face(first.read_bytes()))
        shaper.scale = (1000, 1000)
        hb.ot_font_set_funcs(shaper)
        for char in 'opqr':
            buffer = hb.Buffer()
            buffer.add_str(char+'\u0301')
            buffer.guess_segment_properties()
            hb.shape(shaper, buffer)
            assert len(buffer.glyph_infos) == 2 and all(i.codepoint != 0 for i in buffer.glyph_infos)
            glyph = font['glyf'][font.getBestCmap()[ord(char)]]
            position = buffer.glyph_positions[1]
            assert position.x_advance == 0
            assert position.y_offset == glyph.yMax+60
    with pytest.raises(ValueError, match='Cannot overwrite'):
        build_integration(ROOT/'fonts/Leonardus-1200-Regular.ttf', ROOT)


@pytest.mark.parametrize('mutation', ['selection', 'scope', 'outline', 'shown_proof'])
def test_changed_selection_or_approval_scope_cannot_compile(tmp_path, mutation):
    document = validate_integration(ROOT)
    files = [MANIFEST, document['base_font'], document['study_manifest'], document['design_review_receipt'],
             'data/glyph_evidence.csv', 'specimen/OPQR-Study-Words-2026-10-15.png']
    files.extend(r['file'] for r in document['glyphs'].values())
    for relative in files:
        target = tmp_path/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/relative, target)
    receipt_path = tmp_path/document['design_review_receipt']
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if mutation == 'selection':
        receipt['selected_variants']['p'] = 'B'
    elif mutation == 'scope':
        receipt['approval_of_other_22_lowercase'] = True
    elif mutation == 'outline':
        with (tmp_path/document['glyphs']['q']['file']).open('a', encoding='utf-8') as stream:
            stream.write('\n')
    else:
        with (tmp_path/receipt['shown_word_proof']).open('ab') as stream:
            stream.write(b'changed')
    receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
    document['design_review_receipt_sha256'] = sha(receipt_path)
    (tmp_path/MANIFEST).write_text(json.dumps(document), encoding='utf-8')
    with pytest.raises(ValueError):
        validate_integration(tmp_path)
