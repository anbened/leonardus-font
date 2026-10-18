"""Protect provenance, unapproved status and the separate study output boundary."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
from examples import segmentation_review as review

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def study_root(tmp_path):
    shutil.copytree(ROOT / 'data', tmp_path / 'data', ignore=shutil.ignore_patterns('scans', 'crops'))
    directory = 'glyphs/proposals/2026-10-15-lowercase'
    shutil.copytree(ROOT / directory, tmp_path / directory)
    shutil.copytree(ROOT / 'fonts', tmp_path / 'fonts')
    return tmp_path


def test_real_selection_has_61_segmentations_and_13_approved_designs():
    manifest, samples, annotations = review.validate()
    assert len(annotations) == 61 and len(manifest['glyphs']) == 13
    assert sum(record['limited_support'] for record in manifest['glyphs'].values()) == 4
    assert {samples[sid]['character'] for sid in annotations} == review.LETTERS
    assert manifest['glyphs']['s']['alternatives'][0]['file'].endswith('/s-short.svg')
    assert {c for c, r in manifest['glyphs'].items() if r['design_review'] == 'approved'} == review.LETTERS
    assert (ROOT / 'specimen/Lowercase-Proposals-2026-10-15.svg').read_text(encoding='utf-8') == review.specimen(manifest)
    assert (ROOT / 'specimen/S-Revision-2026-10-15.svg').read_text(encoding='utf-8') == review.s_specimen(manifest)


@pytest.mark.parametrize('shape,minimum', [
    ([[0, 0], [20, 0], [0, 4]], 3),
    ([[0, 0], [1, 1], [2, 2]], 3),
    ([[0, 0], [True, 1], [0, 4]], 3),
    ([[0, 0], [float('nan'), 1], [0, 4]], 3),
    ([[1, 1], [1, 1]], 2),
])
def test_invalid_annotations_are_rejected(shape, minimum):
    with pytest.raises(ValueError):
        review.points(shape, 20, 20, minimum)


@pytest.mark.parametrize('mutation,message', [
    (lambda m: m.update(human_design_review=False), 'approval'),
    (lambda m: m.update(status='approved'), 'approval'),
    (lambda m: m.update(evidence_sha256='0'*64), 'Evidence'),
    (lambda m: m.update(plan_sha256='0'*64), 'plan hash'),
    (lambda m: m['glyphs']['b'].update(classification='normalized'), 'approval'),
    (lambda m: m['glyphs']['b'].update(limited_support=True), 'approval'),
    (lambda m: m['glyphs']['b'].update(sample_ids=[]), 'references'),
    (lambda m: m['glyphs']['b'].update(sha256='0'*64), 'SVG hash'),
    (lambda m: m['glyphs']['b'].update(advance=30), 'cell'),
    (lambda m: m['glyphs']['b'].update(file='fonts/Leonardus-Regular.ttf'), 'escapes'),
    (lambda m: m['glyphs']['s'].update(design_review='pending'), 'approval'),
    (lambda m: m.update(design_review_receipt_sha256='0'*64), 'receipt hash'),
])
def test_metadata_cannot_promote_or_retarget_a_design(study_root, mutation, message):
    path = study_root / review.MANIFEST
    manifest = json.loads(path.read_text(encoding='utf-8'))
    mutation(manifest)
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match=message):
        review.validate(study_root)


def test_separate_study_font_is_reproducible_and_preserves_approved_font(study_root):
    manifest, _, _ = review.validate(study_root)
    approved = study_root / manifest['base_font']
    before = approved.read_bytes()
    output = review.study_font(manifest, study_root)
    first = output.read_bytes()
    assert review.study_font(manifest, study_root).read_bytes() == first
    alternate = review.study_font(manifest, study_root, short_s=True)
    assert alternate.read_bytes() != first
    assert approved.read_bytes() == before
    with TTFont(output) as font, TTFont(approved) as original, TTFont(alternate) as short:
        assert font.getBestCmap() == original.getBestCmap()
        assert font['name'].getDebugName(1) == review.FAMILY
        assert font['name'].getDebugName(6) != original['name'].getDebugName(6)
        assert 'unapproved' in font['name'].getDebugName(5)
        assert short['name'].getDebugName(1) != font['name'].getDebugName(1)
        for letter, record in manifest['glyphs'].items():
            name = font.getBestCmap()[ord(letter)]
            assert font['hmtx'][name][0] == record['advance']
            assert font['glyf'][name].compile(font['glyf']) != original['glyf'][name].compile(original['glyf'])


def test_annotations_cannot_claim_approval_even_after_rehash(study_root):
    path = study_root / review.MANIFEST
    manifest = json.loads(path.read_text(encoding='utf-8'))
    relative = next(iter(manifest['segmentation_sha256']))
    segment_path = study_root / relative
    data = json.loads(segment_path.read_text(encoding='utf-8'))
    data['status'] = 'approved'
    segment_path.write_text(json.dumps(data), encoding='utf-8')
    manifest['segmentation_sha256'][relative] = review.sha(segment_path)
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='cannot claim'):
        review.validate(study_root)


def test_approved_design_cannot_change_even_after_manifest_rehash(study_root):
    path = study_root / review.MANIFEST
    manifest = json.loads(path.read_text(encoding='utf-8'))
    record = manifest['glyphs']['b']
    svg = study_root / record['file']
    svg.write_text(svg.read_text(encoding='utf-8').replace('<title>', '<title>Revised: '), encoding='utf-8')
    record['sha256'] = review.sha(svg)
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='recorded approval'):
        review.validate(study_root)


def test_receipt_cannot_extend_approval_to_segmentation_or_s(study_root):
    path = study_root / review.MANIFEST
    manifest = json.loads(path.read_text(encoding='utf-8'))
    receipt_path = study_root / manifest['design_review_receipt']
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    receipt['segmentation_approved'] = True
    receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
    manifest['design_review_receipt_sha256'] = review.sha(receipt_path)
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='receipt scope'):
        review.validate(study_root)


def test_study_output_directory_cannot_point_to_fonts(study_root):
    out = study_root / 'build/segmentation-review'
    out.parent.mkdir()
    try:
        out.symlink_to(study_root / 'fonts', target_is_directory=True)
    except OSError:
        pytest.skip('Creating symlinks requires privileges on this platform')
    with pytest.raises(ValueError, match='symlinks'):
        review.output_dir(study_root)
