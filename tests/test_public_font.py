"""Technical checks on the exported sources, without source images or Git."""
import csv
import hashlib
import json
import shutil
import unicodedata
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from leonardus.proposal import text_sha256
from leonardus.release import build_release

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = '1f65d26ece4c8a0fe9c275fcdedfa037fab88a9687b0cd89a941d131eb899632'


def test_rebuilt_font_matches_shipped_font(tmp_path):
    one, two = tmp_path / 'one.ttf', tmp_path / 'two.ttf'
    build_release(one, ROOT)
    build_release(two, ROOT)
    assert one.read_bytes() == two.read_bytes() == (ROOT / 'fonts/Leonardus-Regular.ttf').read_bytes()
    assert hashlib.sha256(one.read_bytes()).hexdigest() == EXPECTED


def test_coverage_contours_and_license():
    with TTFont(ROOT / 'fonts/Leonardus-Regular.ttf') as font:
        repertoire = json.loads((ROOT / 'data/charset_regular_v1.json').read_text(encoding='utf-8'))
        expected = {cp for group in repertoire['groups'] for cp in group['codepoints']}
        assert set(font.getBestCmap()) == expected and len(expected) == 119
        assert len(font.getGlyphOrder()) == 121
        assert sum(g.isComposite() for g in font['glyf'].values()) == 12
        for cp, name in font.getBestCmap().items():
            assert (font['glyf'][name].numberOfContours == 0) == (cp in {32, 160})
            assert (font['hmtx'][name][0] == 0) == (cp in {0x300, 0x301})
        assert font['OS/2'].fsType == 0
        assert font['name'].getDebugName(13) == (ROOT / 'OFL.txt').read_text(encoding='utf-8')


def test_precomposed_and_combining_accents_shape_identically():
    face = hb.Font(hb.Face((ROOT / 'fonts/Leonardus-Regular.ttf').read_bytes()))
    hb.ot_font_set_funcs(face)

    def shape(text):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(face, buffer)
        return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buffer.glyph_infos, buffer.glyph_positions)]

    for char in 'àèéìòùÀÈÉÌÒÙ':
        assert shape(char) == shape(unicodedata.normalize('NFD', char))


@pytest.mark.parametrize('gate', ['design', 'license'])
def test_changed_approval_is_rejected_even_with_updated_hash(tmp_path, gate):
    root = tmp_path / 'sources'
    shutil.copytree(ROOT / 'data', root / 'data')
    shutil.copytree(ROOT / 'glyphs', root / 'glyphs')
    config_path = root / 'glyphs/regular/release-1.000.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    receipt_path = root / config['human_release_receipt']
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    receipt[gate]['quote'] = 'pending'
    receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
    config['human_release_receipt_sha256'] = text_sha256(receipt_path)
    config_path.write_text(json.dumps(config), encoding='utf-8')
    with pytest.raises(ValueError, match='Explicit full-design approval'):
        build_release(tmp_path / 'denied.ttf', root, version='1.000')
    assert not (tmp_path / 'denied.ttf').exists()


def test_unreviewed_letter_cannot_bypass_provenance_gate(tmp_path):
    root = tmp_path / 'sources'
    shutil.copytree(ROOT / 'data', root / 'data')
    shutil.copytree(ROOT / 'glyphs', root / 'glyphs')
    path = root / 'data/glyph_evidence.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    row = next(r for r in rows if r['target_character'] == 'a' and r['review_status'] == 'reviewed')
    row.update(review_status='candidate', reviewer='', review_notes='', reviewed_at='')
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match='M1B requires'):
        build_release(tmp_path / 'denied.ttf', root, version='1.000')
    assert not (tmp_path / 'denied.ttf').exists()
