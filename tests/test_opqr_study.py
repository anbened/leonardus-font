"""Keep exploratory designs separate and tied to their actual evidence."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from examples import opqr_study as study

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_study_changes_only_four_bases_and_the_o_accent_dependency(tmp_path, variant):
    first, second = tmp_path/'first.ttf', tmp_path/'second.ttf'
    study.build_font(variant, first)
    study.build_font(variant, second)
    assert first.read_bytes() == second.read_bytes()
    with TTFont(ROOT/'fonts/Leonardus-1200-Regular.ttf') as base, TTFont(first) as font:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = {name for name in font.getGlyphOrder()
                   if font['glyf'][name].compile(font['glyf']) != base['glyf'][name].compile(base['glyf'])}
        assert changed == {f'uni{ord(c):04X}' for c in 'opqrò'}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        assert font['glyf']['uni00F2'].components[0].glyphName == 'uni006F'
        assert font['name'].getDebugName(1) == f'Leonardus OPQR {variant}'
        assert font['OS/2'].fsType == 0
        shaper = hb.Font(hb.Face(first.read_bytes()))
        shaper.scale = (1000, 1000)
        hb.ot_font_set_funcs(shaper)
        for char in 'opqr':
            buffer = hb.Buffer()
            buffer.add_str(char+'\u0300')
            buffer.guess_segment_properties()
            hb.shape(shaper, buffer, {'ccmp': False})
            assert all(info.codepoint != 0 for info in buffer.glyph_infos)
            # HarfBuzz may compose o+grave to the precomposed, linked glyph.
            if len(buffer.glyph_infos) == 2:
                base_glyph = font['glyf'][font.getBestCmap()[ord(char)]]
                position = buffer.glyph_positions[1]
                advance = font['hmtx'][font.getBestCmap()[ord(char)]][0]
                assert position.x_advance == 0
                assert advance+position.x_offset == round((base_glyph.xMin+base_glyph.xMax)/2+35)
                assert position.y_offset == base_glyph.yMax+60
    with pytest.raises(ValueError, match='cannot overwrite'):
        study.build_font(variant, ROOT/'fonts/Leonardus-1200-Regular.ttf')


@pytest.mark.parametrize('mutation', ['approval', 'reference', 'image', 'evidence'])
def test_study_rejects_false_approval_and_changed_evidence(tmp_path, mutation):
    document = study.validate()
    files = [study.MANIFEST, document['base_font'], document['evidence']]
    files.extend(r['file'] for g in document['variants'].values() for r in g['glyphs'].values())
    for relative in files:
        target = tmp_path/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/relative, target)
    if mutation == 'approval':
        document['human_visual_design_approval'] = True
    elif mutation == 'reference':
        document['variants']['A']['glyphs']['p']['reference_sample_ids'].append('BNE_MI_EXP_018_P_05')
    elif mutation == 'image':
        document['source_contexts'][0]['image_sha256'] = '0'*64
    else:
        with (tmp_path/document['evidence']).open('a', encoding='utf-8') as stream:
            stream.write('\n')
    (tmp_path/study.MANIFEST).write_text(json.dumps(document), encoding='utf-8')
    with pytest.raises(ValueError):
        study.validate(tmp_path)
