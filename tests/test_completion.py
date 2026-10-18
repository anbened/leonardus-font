"""Protect preserved designs, honest attribution, and the usable completion font."""
from pathlib import Path
import json
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from examples import segmentation_consolidation as consolidation
from leonardus.completion import build_completion, validate_completion
from leonardus.lowercase import sha

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def completed_font(tmp_path_factory):
    path = tmp_path_factory.mktemp('completion')/'font.ttf'
    build_completion(path, ROOT)
    return path


def test_completion_changes_only_six_and_preserves_coverage(completed_font):
    with TTFont(ROOT/'fonts/Leonardus-Regular.ttf') as base, TTFont(completed_font) as font:
        assert base.getBestCmap() == font.getBestCmap()
        assert len(font.getBestCmap()) == 119
        changed = {name for name in font.getGlyphOrder()
                   if font['glyf'][name].compile(font['glyf']) != base['glyf'][name].compile(base['glyf'])
                   or font['hmtx'][name] != base['hmtx'][name]}
        assert changed == {f'uni{ord(c):04X}' for c in 'jkvwxy'}
        assert font['name'].getDebugName(1) == 'Leonardus 1200'
        assert font['name'].getDebugName(6) != base['name'].getDebugName(6)
        assert round(font['head'].fontRevision, 3) == 1.200
        assert font['OS/2'].fsType == 0


def test_completion_reproducible_and_cannot_overwrite_approved(completed_font, tmp_path):
    second = tmp_path/'second.ttf'
    build_completion(second, ROOT)
    assert sha(second) == sha(completed_font)
    with pytest.raises(ValueError, match='preserved'):
        build_completion(ROOT/'fonts/Leonardus-Regular.ttf', ROOT)


def test_new_bases_keep_combining_marks_anchored(completed_font):
    shaper = hb.Font(hb.Face(completed_font.read_bytes()))
    shaper.scale = (1000, 1000)
    hb.ot_font_set_funcs(shaper)
    with TTFont(completed_font) as font:
        for char in 'jkvwxy':
            for mark in '\u0300\u0301':
                buffer = hb.Buffer()
                buffer.add_str(char+mark)
                buffer.guess_segment_properties()
                hb.shape(shaper, buffer)
                assert len(buffer.glyph_infos) == 2
                assert all(info.codepoint != 0 for info in buffer.glyph_infos)
                base = font['glyf'][font.getBestCmap()[ord(char)]]
                pos = buffer.glyph_positions[1]
                advance = font['hmtx'][font.getBestCmap()[ord(char)]][0]
                assert advance+pos.x_offset == round((base.xMin+base.xMax)/2+35)
                assert pos.y_offset == base.yMax+60 and pos.x_advance == 0


@pytest.mark.parametrize('mutation', ['approval', 'image', 'scope', 'coverage'])
def test_delegated_boundary_assessments_cannot_become_human_reviews(tmp_path, mutation):
    shutil.copytree(ROOT/'data', tmp_path/'data', ignore=shutil.ignore_patterns('scans','crops'))
    _, samples, annotations = consolidation.review.validate(ROOT)
    human = consolidation.recorded_decisions(tmp_path, annotations)
    path = tmp_path/'data/agent_segmentation_review_2026-10-15.json'
    record = json.loads(path.read_text(encoding='utf-8'))
    assert len(consolidation.delegated_decisions(tmp_path, samples, annotations, human)) == 32
    if mutation == 'approval':
        record['human_visual_review'] = True
    elif mutation == 'image':
        record['decisions'][0]['image_sha256'] = '0'*64
    elif mutation == 'scope':
        record['reading_changes'] = True
    else:
        record['decisions'].pop()
    path.write_text(json.dumps(record), encoding='utf-8')
    with pytest.raises(ValueError):
        consolidation.delegated_decisions(tmp_path, samples, annotations, human)
