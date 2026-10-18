"""A review pack must preserve source pixels and never imply human approval."""
import hashlib
import json
from pathlib import Path
import shutil
import pytest
from PIL import Image, ImageOps

from examples import segmentation_consolidation as consolidation


def test_original_is_rehashed_before_use(tmp_path):
    path = tmp_path/'source.png'
    Image.new('RGB', (20, 10), 'white').save(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    sample = {'image_sha256': digest, 'image_width': 20, 'image_height': 10}
    index = consolidation.original_index(tmp_path)
    assert consolidation.verified_image(sample, index).size == (20, 10)
    Image.new('RGB', (20, 10), 'black').save(path)
    with pytest.raises(ValueError, match='hash changed'):
        consolidation.verified_image(sample, index)


def test_missing_original_and_wrong_dimensions_are_distinct(tmp_path):
    sample = {'image_sha256': '0'*64, 'image_width': 20, 'image_height': 10}
    assert consolidation.verified_image(sample, {}) is None
    path = tmp_path/'source.png'
    Image.new('RGB', (10, 10)).save(path)
    sample['image_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='dimensions'):
        consolidation.verified_image(sample, consolidation.original_index(tmp_path))


def test_views_keep_original_and_uncertain_pixels():
    original = Image.new('RGB', (20, 10), 'white')
    original.putpixel((16, 3), (0, 0, 0))
    before = original.tobytes()
    sample = {'raw_crop': [12, 2, 6, 6], 'mirror_crop': [2, 2, 6, 6],
              'mirror_context': [0, 0, 12, 10]}
    item = {'retained_polygons': [[[0, 0], [5, 0], [5, 5], [0, 5]]],
            'excluded_polygons': [], 'uncertain_polygons': [[[0, 0], [2, 0], [2, 2]]],
            'cut_lines': [[[3, 0], [3, 5]]]}
    raw, target, overlay, retained, context = consolidation.views(original, sample, item)
    assert raw.tobytes() == original.crop((12, 2, 18, 8)).tobytes()
    assert target.tobytes() == ImageOps.mirror(original).crop((2, 2, 8, 8)).tobytes()
    assert retained.convert('RGB').tobytes() == target.tobytes()
    assert retained.getchannel('A').getextrema() == (255, 255)
    assert original.tobytes() == before


def test_audit_records_missing_images_without_fabricating_decisions(tmp_path, monkeypatch):
    manifest = {'segmentation_sha256': {}, 'glyphs': {}}
    (tmp_path/'data').mkdir()
    path = tmp_path/consolidation.review.MANIFEST
    path.write_text('{}', encoding='utf-8')
    sample = {'character': 'm', 'folio': '1r', 'page': 14,
              'image_sha256': '0'*64, 'image_width': 20, 'image_height': 10}
    item = {'uncertain_polygons': [[[0, 0], [1, 1], [1, 0]]], 'cut_lines': []}
    plan = {'review_id': 'test-plan', 'status': 'pending_human_review', 'source_sha256': {},
            'samples': [{'sample_id': 'TEST_M', 'human_decision': None,
                         'annotation_sha256': consolidation.annotation_sha(item)}]}
    (tmp_path/consolidation.PLAN).write_text(json.dumps(plan), encoding='utf-8')
    monkeypatch.setattr(consolidation.review, 'validate', lambda root: (manifest, {'TEST_M': sample}, {'TEST_M': item}))
    result = consolidation.prepare(tmp_path)
    audit = json.loads((tmp_path/'build/segmentation-consolidation/audit.json').read_text(encoding='utf-8'))
    assert result['human_decisions'] == 0 and result['originals_verified'] == 0
    assert audit['status'] == 'pending_human_segmentation_review'
    assert audit['samples'][0]['human_decision'] is None
    assert audit['samples'][0]['original_verified'] is False
    assert path.read_text(encoding='utf-8') == '{}'


@pytest.mark.parametrize('mutation', ['annotation', 'scope', 'uncertainty', 'duplicate'])
def test_human_boundary_receipt_cannot_promote_other_claims(tmp_path, mutation):
    root = Path(__file__).resolve().parents[1]
    _, _, annotations = consolidation.review.validate(root)
    shutil.copytree(root/'data', tmp_path/'data', ignore=shutil.ignore_patterns('scans', 'crops'))
    receipt = tmp_path/'data/human_segmentation_consolidation_2026-10-15_m.json'
    document = json.loads(receipt.read_text(encoding='utf-8'))
    decisions = consolidation.recorded_decisions(tmp_path, annotations)
    assert decisions['BNE_MI_EXP_020_M_08'] == 'uncertain'
    if mutation == 'annotation':
        document['decisions'][0]['annotation_sha256'] = '0'*64
    elif mutation == 'scope':
        document['design_changes'] = True
    elif mutation == 'uncertainty':
        document['decisions'][0]['uncertain_regions_approved'] = True
    else:
        document['decisions'].append(document['decisions'][0])
    receipt.write_text(json.dumps(document), encoding='utf-8')
    with pytest.raises(ValueError):
        consolidation.recorded_decisions(tmp_path, annotations)


@pytest.mark.parametrize('mutation', [None, 'mirror', 'polygon', 'approval', 'source'])
def test_wider_crop_proposals_preserve_provenance_and_bounds(mutation):
    root = Path(__file__).resolve().parents[1]
    _, samples, annotations = consolidation.review.validate(root)
    document = json.loads((root/'data/segmentation_revisions_2026-10-15_m.json').read_text(encoding='utf-8'))
    if mutation == 'mirror':
        document['samples'][0]['raw_crop'][0] += 1
    elif mutation == 'polygon':
        document['samples'][0]['annotation']['retained_polygons'][0][0] = [-1, 0]
    elif mutation == 'approval':
        document['samples'][0]['human_decision'] = 'approved'
    elif mutation == 'source':
        document['samples'][0]['based_on_annotation_sha256'] = '0'*64
    if mutation is not None:
        with pytest.raises(ValueError):
            consolidation.revised_records(document, samples, annotations, root)
    else:
        updated, proposed, ids = consolidation.revised_records(document, samples, annotations, root)
        assert len(ids) == 2
        assert all(updated[sid]['mirror_crop'] != samples[sid]['mirror_crop'] for sid in ids)
        assert annotations[ids[0]]['retained_polygons'][0][0] == [3, 4]


@pytest.mark.parametrize('mutation', ['revision', 'scope', 'uncertainty', 'duplicate'])
def test_revision_confirmation_cannot_expand_scope_or_lose_version(tmp_path, mutation):
    root = Path(__file__).resolve().parents[1]
    _, samples, annotations = consolidation.review.validate(root)
    shutil.copytree(root/'data', tmp_path/'data', ignore=shutil.ignore_patterns('scans', 'crops'))
    assert consolidation.recorded_revisions(tmp_path, samples, annotations)['BNE_MI_EXP_014_M_01']['decision'] == 'compatible_with_reservations'
    path = tmp_path/'data/human_segmentation_revision_2026-10-15_m.json'
    document = json.loads(path.read_text(encoding='utf-8'))
    if mutation == 'revision':
        document['revision_sha256'] = '0'*64
    elif mutation == 'scope':
        document['authenticity_claim'] = True
    elif mutation == 'uncertainty':
        document['decisions'][0]['uncertain_regions_approved'] = True
    else:
        document['decisions'].append(document['decisions'][0])
    path.write_text(json.dumps(document), encoding='utf-8')
    with pytest.raises(ValueError):
        consolidation.recorded_revisions(tmp_path, samples, annotations)
