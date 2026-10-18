"""Protect approved outlines, accent derivatives and reproducible version lineage."""
import csv
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from leonardus.fontbuild import _svg_to_glyph
from leonardus.lowercase import approved_lowercase, sha
from leonardus.release import build_release

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = '92e3c7d22bcd34652b502b643e1efed61aedf83fac3659c29c73593d028a3d94'


def test_old_release_remains_reproducible(tmp_path):
    output = tmp_path / 'previous.ttf'
    build_release(output, ROOT, version='1.000')
    assert sha(output) == BASE_SHA
    assert output.read_bytes() == (ROOT / 'fonts/previous/Leonardus-Regular-1.000.ttf').read_bytes()


def test_only_approved_lowercase_and_three_accent_dependencies_change():
    manifest = approved_lowercase(ROOT)
    with TTFont(ROOT / manifest['base_font']) as base, TTFont(ROOT / 'fonts/Leonardus-Regular.ttf') as font:
        changed = set()
        for name in font.getGlyphOrder():
            differs = (font['glyf'][name].compile(font['glyf']) != base['glyf'][name].compile(base['glyf'])
                       or font['hmtx'][name] != base['hmtx'][name])
            if differs:
                changed.add(name)
        expected = {f'uni{ord(c):04X}' for c in manifest['glyphs']} | {'dotlessi', 'uni00EC', 'uni00F9'}
        assert changed == expected
        for c, record in manifest['glyphs'].items():
            name = font.getBestCmap()[ord(c)]
            glyph = _svg_to_glyph(ROOT / record['file'])
            assert font['glyf'][name].compile(font['glyf']) == glyph.compile(font['glyf'])
            assert font['hmtx'][name][0] == record['advance']
        assert round(font['head'].fontRevision, 3) == 1.100
        assert font['name'].getDebugName(3) == 'LeonardusLab:1.100:Regular'
        assert font['name'].getDebugName(6) == base['name'].getDebugName(6)


def test_combining_accents_follow_all_new_base_anchors_and_remove_i_dot():
    path = ROOT / 'fonts/Leonardus-Regular.ttf'
    shaper = hb.Font(hb.Face(path.read_bytes()))
    shaper.scale = (1000, 1000)
    hb.ot_font_set_funcs(shaper)
    with TTFont(path) as font:
        for c in 'bcfghimpqstuz':
            for accent in '\u0300\u0301':
                buffer = hb.Buffer()
                buffer.add_str(c + accent)
                buffer.guess_segment_properties()
                hb.shape(shaper, buffer)
                infos, positions = buffer.glyph_infos, buffer.glyph_positions
                if len(infos) == 1:
                    assert (c, accent) in {('i', '\u0300'), ('u', '\u0300')}
                    composite = font['glyf'][font.getGlyphName(infos[0].codepoint)]
                    base_component, mark_component = composite.components
                    base = font['glyf'][base_component.glyphName]
                    if c == 'i':
                        assert base_component.glyphName == 'dotlessi' and base.numberOfContours == 1
                    assert mark_component.x == round((base.xMin + base.xMax) / 2 + 35)
                    assert mark_component.y == base.yMax + 60
                    continue
                assert len(infos) == 2
                names = [font.getGlyphName(i.codepoint) for i in infos]
                base = font['glyf'][names[0]]
                if c == 'i':
                    assert names[0] == 'dotlessi' and base.numberOfContours == 1
                assert positions[1].x_advance == 0
                assert positions[0].x_advance == font['hmtx'][names[0]][0]
                assert positions[1].x_offset + positions[0].x_advance == round((base.xMin + base.xMax) / 2 + 35)
                assert positions[1].y_offset == base.yMax + 60


def test_exported_derivation_table_matches_compiled_metrics_and_composites():
    manifest = approved_lowercase(ROOT)
    with (ROOT / 'docs/DERIVAZIONE.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    with TTFont(ROOT / 'fonts/Leonardus-Regular.ttf') as font:
        assert {r['glyph'] for r in rows} == set(font.getGlyphOrder()) - {'.notdef'}
        reviewed = set()
        for row in rows:
            name = row['glyph']
            assert int(row['advance']) == font['hmtx'][name][0]
            if row['classification'] == 'reviewed_design':
                c = chr(int(row['codepoint'][2:], 16))
                reviewed.add(c)
                assert set(row['reviewed_sample_ids'].split('|')) == set(manifest['glyphs'][c]['sample_ids'])
            glyph = font['glyf'][name]
            if glyph.isComposite():
                parts = json.loads(row['file_or_components'])
                assert [(p['glyph'], *p['offset']) for p in parts] == [
                    (p.glyphName, p.x, p.y) for p in glyph.components]
        assert reviewed == set(manifest['glyphs'])


@pytest.fixture
def source_root(tmp_path):
    for directory in ('data', 'glyphs', 'fonts'):
        shutil.copytree(ROOT / directory, tmp_path / directory,
                        ignore=shutil.ignore_patterns('scans', 'crops'))
    return tmp_path


def update_manifest_hash(root):
    path = root / 'glyphs/regular/release-1.100.json'
    config = json.loads(path.read_text(encoding='utf-8'))
    config['design_manifest_sha256'] = sha(root / config['design_manifest'])
    path.write_text(json.dumps(config), encoding='utf-8')


@pytest.mark.parametrize('field,value', [('s_approval_quote', 'pending'),
                                       ('font_integration_approved', False),
                                       ('segmentation_approved', True)])
def test_approval_cannot_be_invented_by_rehashing(source_root, tmp_path, field, value):
    path = source_root / 'data/lowercase_design_2026-10-15.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    receipt_path = source_root / manifest['design_review_receipt']
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    receipt[field] = value
    receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
    manifest['design_review_receipt_sha256'] = sha(receipt_path)
    path.write_text(json.dumps(manifest), encoding='utf-8')
    update_manifest_hash(source_root)
    output = tmp_path / 'denied.ttf'
    with pytest.raises(ValueError, match='receipt scope'):
        build_release(output, source_root)
    assert not output.exists()


def test_preserved_checkpoint_cannot_be_overwritten(source_root):
    path = source_root / 'fonts/previous/Leonardus-Regular-1.000.ttf'
    with pytest.raises(ValueError, match='preserved'):
        build_release(path, source_root)
    assert sha(path) == BASE_SHA


def test_dotless_i_cannot_drift_from_approved_stem_even_after_rehash(source_root, tmp_path):
    path = source_root / 'glyphs/regular/release-1.100.json'
    config = json.loads(path.read_text(encoding='utf-8'))
    support = source_root / config['dotlessi']['file']
    support.write_text(support.read_text(encoding='utf-8').replace('M105 454', 'M106 454'), encoding='utf-8')
    config['dotlessi']['sha256'] = sha(support)
    path.write_text(json.dumps(config), encoding='utf-8')
    with pytest.raises(ValueError, match='approved i stem'):
        build_release(tmp_path / 'denied.ttf', source_root)
    assert not (tmp_path / 'denied.ttf').exists()
