"""Preserve the exact five-letter human selection and existing font checkpoints."""
import json
from pathlib import Path
import shutil
import unicodedata

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from leonardus.aemnu import MANIFEST, SELECTION, build_integration, validate_integration
from leonardus.fontbuild import _svg_to_glyph
from leonardus.lowercase import sha

ROOT = Path(__file__).resolve().parents[1]


def test_selected_integration_is_exact_reproducible_and_preserves_other_designs(tmp_path):
    first, second = tmp_path/'first.ttf', tmp_path/'second.ttf'
    build_integration(first, ROOT); build_integration(second, ROOT)
    assert first.read_bytes() == second.read_bytes() == (ROOT/'fonts/Leonardus-1220-Regular.ttf').read_bytes()
    document = validate_integration(ROOT)
    with TTFont(first) as font, TTFont(ROOT/document['base_font']) as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = {n for n in font.getGlyphOrder()
                   if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
        assert changed == {f'uni{ord(c):04X}' for c in 'aemnuàèéù'}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        for name in font.getGlyphOrder():
            if name not in changed: assert font['hmtx'][name] == base['hmtx'][name]
        for char, variant in SELECTION.items():
            record = document['glyphs'][char]
            assert record['variant'] == variant
            expected = _svg_to_glyph(ROOT/record['file']); expected.recalcBounds(None)
            assert expected.compile(font['glyf']) == font['glyf'][font.getBestCmap()[ord(char)]].compile(font['glyf'])
        assert font['name'].getDebugName(1) == 'Leonardus 1220' and font['OS/2'].fsType == 0
        # The mark table and the precomposed forms must share the same base anchors.
        for lookup in font['GPOS'].table.LookupList.Lookup:
            for subtable in lookup.SubTable:
                if not hasattr(subtable, 'BaseCoverage'): continue
                anchors = dict(zip(subtable.BaseCoverage.glyphs, subtable.BaseArray.BaseRecord))
                for char in SELECTION:
                    name = font.getBestCmap()[ord(char)]; glyph = font['glyf'][name]
                    anchor = anchors[name].BaseAnchor[0]
                    assert (anchor.XCoordinate, anchor.YCoordinate) == (round((glyph.xMin+glyph.xMax)/2+35), glyph.yMax+60)
        for char, accents in {'a':'à', 'e':'èé', 'u':'ù'}.items():
            glyph = font['glyf'][font.getBestCmap()[ord(char)]]
            for accented in accents:
                composite = font['glyf'][font.getBestCmap()[ord(accented)]]
                assert (composite.components[1].x, composite.components[1].y) == (round((glyph.xMin+glyph.xMax)/2+35), glyph.yMax+60)
                assert font['hmtx'][font.getBestCmap()[ord(accented)]][0] == font['hmtx'][font.getBestCmap()[ord(char)]][0]
        shaper = hb.Font(hb.Face(first.read_bytes())); shaper.scale = (1000,1000); hb.ot_font_set_funcs(shaper)
        shaped = []
        for text in ['à è é ù', unicodedata.normalize('NFD','à è é ù')]:
            buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(shaper,buf)
            assert all(i.codepoint for i in buf.glyph_infos)
            shaped.append([(i.codepoint,p.x_advance,p.y_advance,p.x_offset,p.y_offset) for i,p in zip(buf.glyph_infos,buf.glyph_positions)])
        assert shaped[0] == shaped[1]
        # Keep the previous p/q gap, advance, contours and selected OPQR forms exact.
        assert font['hmtx']['uni0070'][0]-font['glyf']['uni0070'].xMax+font['glyf']['uni0071'].xMin == 115
    for filename in ['Leonardus-Regular.ttf','Leonardus-1200-Regular.ttf','Leonardus-1210-Regular.ttf','Leonardus-1211-Regular.ttf','previous/Leonardus-Regular-1.000.ttf']:
        with pytest.raises(ValueError,match='Cannot overwrite'):
            build_integration(ROOT/'fonts'/filename,ROOT)


@pytest.mark.parametrize('mutation', ['selection','scope','outline','shown_proof'])
def test_changed_selection_or_approval_scope_cannot_compile(tmp_path,mutation):
    document = validate_integration(ROOT)
    files = [MANIFEST,document['base_font'],document['study_manifest'],document['design_review_receipt'],
             'data/glyph_evidence.csv','specimen/AEMNU-Study-Words-2026-10-15.png']
    files.extend(r['file'] for r in document['glyphs'].values())
    for relative in files:
        target=tmp_path/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
    path=tmp_path/document['design_review_receipt'];receipt=json.loads(path.read_text(encoding='utf-8'))
    if mutation=='selection':receipt['selected_variants']['a']='B'
    elif mutation=='scope':receipt['approval_of_other_21_lowercase']=True
    elif mutation=='outline':
        with (tmp_path/document['glyphs']['u']['file']).open('a',encoding='utf-8') as stream:stream.write('\n')
    else:
        with (tmp_path/receipt['shown_word_proof']).open('ab') as stream:stream.write(b'changed')
    path.write_text(json.dumps(receipt),encoding='utf-8');document['design_review_receipt_sha256']=sha(path)
    (tmp_path/MANIFEST).write_text(json.dumps(document),encoding='utf-8')
    with pytest.raises(ValueError):validate_integration(tmp_path)
