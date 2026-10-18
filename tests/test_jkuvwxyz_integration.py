"""Retain all eight explicit B choices, prior capitals, lowercase shapes and accents."""
import csv
import json
from pathlib import Path
import shutil
import unicodedata

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from leonardus.fontbuild import _svg_to_glyph
from leonardus.jkuvwxyz import MANIFEST, SELECTION, build_integration, validate_integration
from leonardus.lowercase import sha

ROOT = Path(__file__).resolve().parents[1]


def test_selected_capitals_are_exact_and_other_forms_and_advances_are_preserved(tmp_path):
    first, second = tmp_path/'first.ttf', tmp_path/'second.ttf'
    build_integration(first, ROOT); build_integration(second, ROOT)
    assert first.read_bytes() == second.read_bytes() == (ROOT/'fonts/Leonardus-1270-Regular.ttf').read_bytes()
    document = validate_integration(ROOT)
    assert SELECTION == {c: 'B' for c in 'JKUVWXYZ'}
    with TTFont(first) as font, TTFont(ROOT/document['base_font']) as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = {n for n in font.getGlyphOrder()
                   if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
        assert changed == {f'uni{ord(c):04X}' for c in ''.join(SELECTION)+'Ù'}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        for name in font.getGlyphOrder():
            if name not in changed: assert font['hmtx'][name] == base['hmtx'][name]
        for char, variant in SELECTION.items():
            record = document['glyphs'][char]
            assert record['variant'] == variant and record['classification'] == 'designed' and record['historical_capital_attestation'] is False
            expected = _svg_to_glyph(ROOT/record['file']); expected.recalcBounds(None)
            assert expected.compile(font['glyf']) == font['glyf'][font.getBestCmap()[ord(char)]].compile(font['glyf'])
        with (ROOT/'docs/DERIVAZIONE_1_270.csv').open(encoding='utf-8', newline='') as stream:
            derivation = {r['glyph']: r for r in csv.DictReader(stream)}
        for char in SELECTION:
            row = derivation[f'uni{ord(char):04X}']
            assert row['classification'] == 'designed' and row['reviewed_sample_ids'] == ''
            assert row['file_or_components'] == document['glyphs'][char]['file']
        for name in ('uni00D9',):
            expected_parts = [{'glyph': c.glyphName, 'offset': [c.x, c.y]}
                              for c in font['glyf'][name].components]
            assert json.loads(derivation[name]['file_or_components']) == expected_parts
        assert font['name'].getDebugName(1) == 'Leonardus 1270' and font['OS/2'].fsType == 0
        assert font['hmtx']['uni0070'][0]-font['glyf']['uni0070'].xMax+font['glyf']['uni0071'].xMin == 115
        shaper = hb.Font(hb.Face(first.read_bytes())); shaper.scale = (1000,1000); hb.ot_font_set_funcs(shaper)
        for char in SELECTION:
            for mark in ('\u0301',):
                buf = hb.Buffer(); buf.add_str(char+mark); buf.guess_segment_properties(); hb.shape(shaper,buf)
                assert len(buf.glyph_infos) == 2 and all(i.codepoint for i in buf.glyph_infos)
                glyph = font['glyf'][font.getBestCmap()[ord(char)]]
                advance = font['hmtx'][font.getBestCmap()[ord(char)]][0]
                assert advance+buf.glyph_positions[1].x_offset == round((glyph.xMin+glyph.xMax)/2+20)
                assert buf.glyph_positions[1].y_offset == glyph.yMax+60
                assert buf.glyph_positions[1].x_advance == 0
        shaped = []
        for text in ['À È É Ì Ò Ù à è é ì ò ù', unicodedata.normalize('NFD','À È É Ì Ò Ù à è é ì ò ù')]:
            buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(shaper,buf)
            assert all(i.codepoint for i in buf.glyph_infos)
            shaped.append([(i.codepoint,p.x_advance,p.x_offset,p.y_offset) for i,p in zip(buf.glyph_infos,buf.glyph_positions)])
        assert shaped[0] == shaped[1]
    for filename in ['Leonardus-Regular.ttf','Leonardus-1200-Regular.ttf','Leonardus-1210-Regular.ttf',
                     'Leonardus-1211-Regular.ttf','Leonardus-1220-Regular.ttf','Leonardus-1230-Regular.ttf','Leonardus-1240-Regular.ttf','Leonardus-1250-Regular.ttf','Leonardus-1260-Regular.ttf','previous/Leonardus-Regular-1.000.ttf']:
        with pytest.raises(ValueError,match='Cannot overwrite'):
            build_integration(ROOT/'fonts'/filename, ROOT)


@pytest.mark.parametrize('mutation', ['selection','scope','classification','capital_reference','outline','shown_proof'])
def test_changed_selection_scope_or_evidence_classification_cannot_compile(tmp_path, mutation):
    document = validate_integration(ROOT)
    files = [MANIFEST,document['base_font'],document['study_manifest'],document['design_review_receipt'],
             'data/glyph_evidence.csv','specimen/JKUVWXYZ-Study-Words-2026-10-16.png']
    files.extend(r['file'] for r in document['glyphs'].values())
    for relative in files:
        target=tmp_path/relative; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/relative,target)
    path=tmp_path/document['design_review_receipt']; receipt=json.loads(path.read_text(encoding='utf-8'))
    if mutation == 'selection': receipt['selected_variants']['J']='A'
    elif mutation == 'scope': receipt['approval_of_other_characters']=True
    elif mutation == 'classification': document['glyphs']['J']['classification']='reviewed_design'
    elif mutation == 'capital_reference': document['glyphs']['K']['contextual_reference_ids']=['K_CONTEXT_01']
    elif mutation == 'outline':
        with (tmp_path/document['glyphs']['W']['file']).open('a',encoding='utf-8') as stream: stream.write('\n')
    else:
        with (tmp_path/receipt['shown_word_proof']).open('ab') as stream: stream.write(b'changed')
    path.write_text(json.dumps(receipt),encoding='utf-8'); document['design_review_receipt_sha256']=sha(path)
    (tmp_path/MANIFEST).write_text(json.dumps(document),encoding='utf-8')
    with pytest.raises(ValueError): validate_integration(tmp_path)


def test_all_26_capitals_match_the_four_disjoint_human_selections():
    selected = {}
    for version in ('1.240', '1.250', '1.260', '1.270'):
        document = json.loads((ROOT/f'glyphs/regular/release-{version}.json').read_text(encoding='utf-8'))
        assert not set(selected) & set(document['glyphs'])
        selected.update(document['glyphs'])
    assert set(selected) == set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    with TTFont(ROOT/'fonts/Leonardus-1270-Regular.ttf') as font:
        for char, record in selected.items():
            assert record['classification'] == 'designed'
            assert record['historical_capital_attestation'] is False
            expected = _svg_to_glyph(ROOT/record['file']); expected.recalcBounds(None)
            actual = font['glyf'][font.getBestCmap()[ord(char)]]
            assert expected.compile(font['glyf']) == actual.compile(font['glyf'])
