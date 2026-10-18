"""Capital studies must preserve lowercase designs, accents and approval boundaries."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from examples import capitals_study as study

ROOT = Path(__file__).resolve().parents[1]


def changed_outlines(font, base):
    return {n for n in font.getGlyphOrder()
            if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_capital_study_is_reproducible_and_preserves_lowercase_and_advances(variant):
    output = ROOT/'build/capitals-tests'/variant
    output.mkdir(parents=True, exist_ok=True)
    first, second = output/'first.ttf', output/'second.ttf'
    study.build_font(variant, first); study.build_font(variant, second)
    assert first.read_bytes() == second.read_bytes()
    with TTFont(first) as font, TTFont(ROOT/'fonts/Leonardus-1230-Regular.ttf') as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = changed_outlines(font, base)
        assert changed == {f'uni{ord(c):04X}' for c in study.LETTERS+'À'}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        assert all(font['hmtx'][n] == base['hmtx'][n] for n in font.getGlyphOrder() if n not in changed)
        assert font['name'].getDebugName(1) == f'Leonardus Capitals {variant}'
        assert font['OS/2'].fsType == 0
        shaper = hb.Font(hb.Face(first.read_bytes())); shaper.scale = (1000, 1000); hb.ot_font_set_funcs(shaper)
        for char in study.LETTERS:
            buf = hb.Buffer(); buf.add_str(char+'\u0301'); buf.guess_segment_properties(); hb.shape(shaper, buf)
            assert len(buf.glyph_infos) == 2 and all(i.codepoint for i in buf.glyph_infos)
            glyph = font['glyf'][font.getBestCmap()[ord(char)]]
            advance = font['hmtx'][font.getBestCmap()[ord(char)]][0]
            assert advance+buf.glyph_positions[1].x_offset == round((glyph.xMin+glyph.xMax)/2+20)
            assert buf.glyph_positions[1].y_offset == glyph.yMax+60
            assert buf.glyph_positions[1].x_advance == 0
        capital = font['glyf']['uni0041']
        grave = font['glyf']['uni00C0'].components[1]
        assert (grave.x, grave.y) == (round((capital.xMin+capital.xMax)/2+20), capital.yMax+60)


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_isolated_comparison_changes_only_the_named_capital_and_its_dependency(variant):
    output = ROOT/'build/capitals-tests'/variant
    output.mkdir(parents=True, exist_ok=True)
    with TTFont(ROOT/'fonts/Leonardus-1230-Regular.ttf') as base:
        for char in study.LETTERS:
            path = output/f'{char}.ttf'; study.build_font(variant, path, character=char)
            with TTFont(path) as font:
                expected = {f'uni{ord(c):04X}' for c in char+study.DEPENDENCIES.get(char, '')}
                assert changed_outlines(font, base) == expected
    with pytest.raises(ValueError): study.build_font(variant, ROOT/'fonts/Leonardus-1230-Regular.ttf')
    for char in ('', 'LM', 'l'):
        with pytest.raises(ValueError): study.build_font(variant, output/'invalid.ttf', character=char)


@pytest.mark.parametrize('mutation', ['approval', 'capital_reading', 'lowercase_as_capital',
                                    'formal_as_reviewed', 'crop', 'advance'])
def test_reject_evidence_promotion_and_inconsistent_localizations(tmp_path, mutation):
    doc = study.validate()
    files = [study.MANIFEST, doc['base_font'], doc['evidence']]
    files.extend(r['file'] for g in doc['variants'].values() for r in g['glyphs'].values())
    for relative in files:
        target = tmp_path/relative; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/relative, target)
    if mutation == 'approval': doc['integration_approved'] = True
    elif mutation == 'capital_reading': doc['new_reviewed_capital_readings'] = 1
    elif mutation == 'lowercase_as_capital': doc['source_contexts'][-1]['character'] = 'R'
    elif mutation == 'formal_as_reviewed': doc['source_contexts'][0]['review_status'] = 'reviewed'
    elif mutation == 'crop': doc['source_contexts'][0]['raw_crop'][0] += 1
    else: doc['variants']['A']['glyphs']['L']['advance'] += 1
    (tmp_path/study.MANIFEST).write_text(json.dumps(doc), encoding='utf-8')
    with pytest.raises(ValueError): study.validate(tmp_path)
