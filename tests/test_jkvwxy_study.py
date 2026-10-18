"""Keep six experimental completions isolated from releases and reviewed evidence."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from examples import jkvwxy_study as study

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_reproducible_study_preserves_all_other_outlines_and_advances(variant):
    output = ROOT/'build/jkvwxy-tests'/variant
    output.mkdir(parents=True, exist_ok=True)
    first, second = output/'first.ttf', output/'second.ttf'
    study.build_font(variant, first); study.build_font(variant, second)
    assert first.read_bytes() == second.read_bytes()
    with TTFont(first) as font, TTFont(ROOT/'fonts/Leonardus-1220-Regular.ttf') as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        changed = {n for n in font.getGlyphOrder()
                   if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
        assert changed == {f'uni{ord(c):04X}' for c in study.LETTERS}
        assert all(font['hmtx'][n][0] == base['hmtx'][n][0] for n in font.getGlyphOrder())
        assert all(font['hmtx'][n] == base['hmtx'][n] for n in font.getGlyphOrder() if n not in changed)
        assert font['name'].getDebugName(1) == f'Leonardus JKVWXY {variant}'
        assert font['OS/2'].fsType == 0
        shaper = hb.Font(hb.Face(first.read_bytes())); shaper.scale = (1000, 1000); hb.ot_font_set_funcs(shaper)
        for char in study.LETTERS:
            buf = hb.Buffer(); buf.add_str(char+'\u0300'); buf.guess_segment_properties(); hb.shape(shaper, buf)
            assert len(buf.glyph_infos) == 2 and all(i.codepoint for i in buf.glyph_infos)
            glyph = font['glyf'][font.getBestCmap()[ord(char)]]
            advance = font['hmtx'][font.getBestCmap()[ord(char)]][0]
            assert advance+buf.glyph_positions[1].x_offset == round((glyph.xMin+glyph.xMax)/2+35)
            assert buf.glyph_positions[1].y_offset == glyph.yMax+60
            assert buf.glyph_positions[1].x_advance == 0


@pytest.mark.parametrize('variant', ['A', 'B'])
def test_each_word_comparison_changes_only_one_letter(variant):
    output = ROOT/'build/jkvwxy-tests'/variant
    output.mkdir(parents=True, exist_ok=True)
    with TTFont(ROOT/'fonts/Leonardus-1220-Regular.ttf') as base:
        for char in study.LETTERS:
            path = output/f'{char}.ttf'; study.build_font(variant, path, character=char)
            with TTFont(path) as font:
                changed = {n for n in font.getGlyphOrder()
                           if font['glyf'][n].compile(font['glyf']) != base['glyf'][n].compile(base['glyf'])}
                assert changed == {f'uni{ord(char):04X}'}
    with pytest.raises(ValueError): study.build_font(variant, ROOT/'fonts/Leonardus-1220-Regular.ttf')
    for char in ('', 'jk', 'a'):
        with pytest.raises(ValueError): study.build_font(variant, output/'invalid.ttf', character=char)


@pytest.mark.parametrize('mutation', ['approval', 'k_as_reviewed', 'candidate_as_reviewed', 'w_reference', 'image', 'advance'])
def test_study_rejects_evidence_promotion_and_reference_tampering(tmp_path, mutation):
    doc = study.validate()
    files = [study.MANIFEST, doc['base_font'], doc['evidence'], doc['prior_research']]
    files.extend(r['file'] for g in doc['variants'].values() for r in g['glyphs'].values())
    for relative in files:
        target = tmp_path/relative; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/relative, target)
    if mutation == 'approval': doc['integration_approved'] = True
    elif mutation == 'k_as_reviewed': doc['source_contexts'][-1]['review_status'] = 'reviewed'
    elif mutation == 'candidate_as_reviewed': doc['source_contexts'][0]['review_status'] = 'reviewed'
    elif mutation == 'w_reference': doc['variants']['B']['glyphs']['w']['reference_context_ids'] = ['K_CONTEXT_01']
    elif mutation == 'image': doc['source_contexts'][0]['image_sha256'] = '0'*64
    else: doc['variants']['A']['glyphs']['j']['advance'] += 1
    (tmp_path/study.MANIFEST).write_text(json.dumps(doc), encoding='utf-8')
    with pytest.raises(ValueError): study.validate(tmp_path)
