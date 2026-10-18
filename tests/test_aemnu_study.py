"""Verify isolated AEMNU changes, accent dependencies and study boundaries."""
import json
from pathlib import Path
import shutil
import unicodedata

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from examples import aemnu_study as study

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_study_is_reproducible_and_preserves_other_glyphs(variant):
    output = ROOT/'build/aemnu-tests'/variant
    output.mkdir(parents=True, exist_ok=True)
    first, second = output/'first.ttf', output/'second.ttf'
    study.build_font(variant, first); study.build_font(variant, second)
    assert first.read_bytes() == second.read_bytes()
    with TTFont(first) as font, TTFont(ROOT/'fonts/Leonardus-1211-Regular.ttf') as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = {n for n in font.getGlyphOrder()
                   if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
        assert changed == {f'uni{ord(c):04X}' for c in 'aemnuàèéù'}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        assert font['name'].getDebugName(1) == f'Leonardus AEMNU {variant}'
        assert font['OS/2'].fsType == 0
        shaper = hb.Font(hb.Face(first.read_bytes())); shaper.scale = (1000, 1000); hb.ot_font_set_funcs(shaper)
        for char in study.LETTERS:
            for mark in ('\u0300', '\u0301'):
                buf = hb.Buffer(); buf.add_str(char+mark); buf.guess_segment_properties()
                hb.shape(shaper, buf)
                assert all(i.codepoint for i in buf.glyph_infos)
                glyph = font['glyf'][font.getBestCmap()[ord(char)]]
                if len(buf.glyph_infos) == 1:
                    composed = unicodedata.normalize('NFC', char+mark)
                    assert len(composed) == 1
                    assert buf.glyph_infos[0].codepoint == font.getGlyphID(font.getBestCmap()[ord(composed)])
                    continue
                assert len(buf.glyph_infos) == 2
                position = buf.glyph_positions[1]
                advance = font['hmtx'][font.getBestCmap()[ord(char)]][0]
                assert advance+position.x_offset == round((glyph.xMin+glyph.xMax)/2+35)
                assert position.y_offset == glyph.yMax+60 and position.x_advance == 0
            for accented in study.DEPENDENCIES.get(char, ''):
                composite = font['glyf'][font.getBestCmap()[ord(accented)]]
                assert (composite.components[1].x, composite.components[1].y) == (
                    round((glyph.xMin+glyph.xMax)/2+35), glyph.yMax+60)


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_single_letter_comparisons_are_actually_isolated(variant):
    output = ROOT/'build/aemnu-tests'/variant
    output.mkdir(parents=True, exist_ok=True)
    with TTFont(ROOT/'fonts/Leonardus-1211-Regular.ttf') as base:
        for char in study.LETTERS:
            path = output/f'{char}.ttf'; study.build_font(variant, path, character=char)
            with TTFont(path) as font:
                changed = {n for n in font.getGlyphOrder()
                           if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
                assert changed == {f'uni{ord(c):04X}' for c in char+study.DEPENDENCIES.get(char, '')}
                for name in font.getGlyphOrder():
                    if name not in changed: assert font['hmtx'][name] == base['hmtx'][name]
    with pytest.raises(ValueError):
        study.build_font(variant, ROOT/'fonts/Leonardus-1211-Regular.ttf')


@pytest.mark.parametrize('mutation', ['approval', 'reference', 'image', 'advance', 'evidence'])
def test_study_rejects_scope_and_provenance_tampering(tmp_path, mutation):
    doc = study.validate()
    files = [study.MANIFEST, doc['base_font'], doc['evidence']]
    files.extend(r['file'] for g in doc['variants'].values() for r in g['glyphs'].values())
    for relative in files:
        target = tmp_path/relative; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/relative, target)
    if mutation == 'approval': doc['integration_approved'] = True
    elif mutation == 'reference': doc['variants']['B']['glyphs']['u']['reference_sample_ids'].append('BNE_MI_EXP_020_U_08')
    elif mutation == 'image': doc['source_contexts'][0]['image_sha256'] = '0'*64
    elif mutation == 'advance': doc['variants']['A']['glyphs']['a']['advance'] += 1
    else:
        with (tmp_path/doc['evidence']).open('a', encoding='utf-8') as stream: stream.write('\n')
    (tmp_path/study.MANIFEST).write_text(json.dumps(doc), encoding='utf-8')
    with pytest.raises(ValueError): study.validate(tmp_path)
