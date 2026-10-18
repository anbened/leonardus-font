"""Verify provenance gates and that review rendering cannot mutate original scans."""
import copy
import csv
import hashlib
import importlib.util
from pathlib import Path

from PIL import Image
import pytest
from leonardus.evidence import SAMPLE_FIELDS, SOURCE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('corpus_review', ROOT / 'examples/corpus_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


@pytest.fixture
def candidate(tmp_path):
    scans = tmp_path / 'data/scans/expansion'
    scans.mkdir(parents=True)
    path = scans / 'page-018.jpg'
    image = Image.new('RGB', (100, 60))
    image.putdata([(x * 2, y * 3, 80) for y in range(60) for x in range(100)])
    image.save(path)
    sample = dict(sample_id='exp-c-01', character='c', page=18, folio='3r',
                  source_image_id='page-018', image_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  image_width=100, image_height=60, source_local_path='scans/expansion/page-018.jpg',
                  mirror_crop=[20, 10, 10, 20], mirror_context=[10, 5, 40, 40],
                  raw_crop=[70, 10, 10, 20], raw_context=[50, 5, 40, 40],
                  token='<script>alert(1)</script>', position=1, rationale='Context & shape', doubts='Unreviewed')
    batch = dict(batch_id='expansion-test', samples=[sample], source=dict(
        url='https://bnedigital.bne.es/bd/card?oid=0000040157',
        viewer_url='https://bnedigital.bne.es/bd/es/viewer?id=example',
        attribution='Biblioteca Nacional de España'))
    return tmp_path, path, batch


def test_dossier_preserves_original_and_escapes_text(candidate):
    root, original, batch = candidate
    before = original.read_bytes()
    index = review.render_dossier(batch, 'build/review', root)
    assert original.read_bytes() == before
    html = index.read_text(encoding='utf-8')
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert 'candidate, non revisionato' in html
    assert 'viewer?id=example&amp;page=18' in html
    assert 'href="#letter-c"' in html
    assert 'Coordinate [x, y, larghezza, altezza]' in html
    with Image.open(index.parent / 'exp-c-01-crop.png') as image:
        assert image.size == (30, 60)
        with Image.open(original) as raw:
            assert image.getpixel((0, 0)) == raw.getpixel((79, 10))
            assert image.getpixel((29, 59)) == raw.getpixel((70, 29))
    with Image.open(index.parent / 'exp-c-01-context.png') as image:
        assert image.getpixel((10, 5)) == (208, 32, 32)
    csv_path = index.parent / 'review.csv'
    assert 'exp-c-01,c,,,,' in csv_path.read_text(encoding='utf-8')
    csv_path.write_text('existing review', encoding='utf-8')
    review.render_dossier(batch, 'build/review', root)
    assert csv_path.read_text(encoding='utf-8') == 'existing review'


def test_tampered_image_fails_before_any_output(candidate):
    root, original, batch = candidate
    original.write_bytes(original.read_bytes() + b'tampered')
    with pytest.raises(ValueError, match='SHA-256'):
        review.render_dossier(batch, 'build/review', root)
    assert not (root / 'build/review').exists()


def test_inferred_folio_and_extended_metadata_are_explicit_and_escaped(candidate):
    root, _, batch = candidate
    sample = batch['samples'][0]
    sample.update(folio_status='agent_concordance_pending_review', context_kind='diagram_label',
                  observed_form='<img src=x onerror=alert(1)> & ascender',
                  alternatives=['capital K <script>', 'k & uncertain'],
                  case_status='lowercase <pending>')
    batch['excluded_observations'] = [{'note': 'EXCLUDED_SENTINEL <script>'}]
    index = review.render_dossier(batch, 'build/extended-review', root)
    document = index.read_text(encoding='utf-8')
    assert 'Foliazione di lavoro DA REVISIONARE' in document
    assert 'etichetta di diagramma' in document
    assert 'Forma osservata: &lt;img src=x onerror=alert(1)&gt; &amp; ascender' in document
    assert 'capital K &lt;script&gt;; k &amp; uncertain' in document
    assert 'Caso proposto: lowercase &lt;pending&gt;' in document
    assert '<script>' not in document and 'EXCLUDED_SENTINEL' not in document
    assert sample['character'] == 'c' and sample.get('status', 'candidate') == 'candidate'
    sample['folio_status'] = 'working_mapping_pending_review'
    sample['context_kind'] = 'prose'
    document = review.render_dossier(batch, 'build/extended-review', root).read_text(encoding='utf-8')
    assert 'Foliazione di lavoro DA REVISIONARE' in document and 'Contesto: prosa.' in document


def test_invalid_extended_metadata_is_rejected(candidate):
    root, _, batch = candidate
    invalid = [('folio_status', 'confirmed'), ('folio_status', ['working_mapping_pending_review']),
               ('context_kind', 'caption'), ('context_kind', None), ('observed_form', {}),
               ('case_status', False), ('alternatives', 'capital K'), ('alternatives', ['k', 2])]
    for field, value in invalid:
        changed = copy.deepcopy(batch)
        changed['samples'][0][field] = value
        with pytest.raises(ValueError, match=field):
            review.validate_batch(changed, root)


@pytest.mark.parametrize('field,value,message', [
    ('mirror_crop', [99, 10, 10, 20], 'outside'),
    ('raw_crop', [71, 10, 10, 20], 'disagree'),
    ('mirror_context', [25, 5, 40, 40], 'disagree'),
    ('source_local_path', '../original.jpg', 'relative'),
    ('source_local_path', 'other/page.jpg', 'escapes'),
    ('sample_id', '../escape', 'identifiers'),
    ('character', 'a', 'new lowercase'),
    ('status', 'accepted', 'promote'),
    ('position', 0, '1-based'),
])
def test_invalid_metadata_is_rejected(candidate, field, value, message):
    root, _, batch = candidate
    batch['samples'][0][field] = value
    with pytest.raises(ValueError, match=message):
        review.validate_batch(batch, root)


def test_context_must_contain_target(candidate):
    root, _, batch = candidate
    batch['samples'][0]['mirror_context'] = [25, 5, 40, 40]
    batch['samples'][0]['raw_context'] = [35, 5, 40, 40]
    with pytest.raises(ValueError, match='contain'):
        review.validate_batch(batch, root)


def test_metadata_validation_requires_no_scan(candidate):
    root, original, batch = candidate
    original.unlink()
    assert review.validate_batch(batch, root) is batch


def test_duplicate_candidates_and_foreign_links_are_rejected(candidate):
    root, _, batch = candidate
    batch['samples'].append(copy.deepcopy(batch['samples'][0]))
    with pytest.raises(ValueError, match='unique'):
        review.validate_batch(batch, root)
    batch['samples'].pop()
    batch['source']['viewer_url'] = 'https://untrusted.example.test/viewer'
    with pytest.raises(ValueError, match='BNE HTTPS'):
        review.validate_batch(batch, root)


def test_output_cannot_target_original_or_escape_build(candidate):
    root, original, batch = candidate
    before = original.read_bytes()
    with pytest.raises(ValueError, match='escapes'):
        review.render_dossier(batch, 'data/scans/expansion', root)
    with pytest.raises(ValueError, match='escapes'):
        review.render_dossier(batch, 'build/../../outside', root)
    assert original.read_bytes() == before


def test_wrong_source_dimensions_are_rejected(candidate):
    root, _, batch = candidate
    sample = batch['samples'][0]
    sample['image_height'] = 61
    with pytest.raises(ValueError, match='dimensions mismatch'):
        review.validate_batch(batch, root, verify_images=True)


def test_output_symlink_cannot_overwrite_scan(candidate):
    root, original, batch = candidate
    out = root / 'build/review'
    out.mkdir(parents=True)
    try:
        (out / 'exp-c-01-crop.png').symlink_to(original)
    except OSError:
        pytest.skip('Creating symlinks requires privileges on this platform')
    before = original.read_bytes()
    with pytest.raises(ValueError, match='escapes'):
        review.render_dossier(batch, out, root)
    assert original.read_bytes() == before


def test_scan_symlink_cannot_escape_repository(candidate, tmp_path):
    root, original, batch = candidate
    linked = original.parent / 'linked.jpg'
    outside = root.parent / f'{root.name}-external.jpg'
    outside.write_bytes(original.read_bytes())
    try:
        try:
            linked.symlink_to(outside)
        except OSError:
            pytest.skip('Creating symlinks requires privileges on this platform')
        batch['samples'][0]['source_local_path'] = 'scans/expansion/linked.jpg'
        with pytest.raises(ValueError, match='escapes'):
            review.validate_batch(batch, root)
    finally:
        outside.unlink()


def test_duplicate_crop_identity_is_rejected(candidate):
    root, _, batch = candidate
    second = copy.deepcopy(batch['samples'][0])
    second['sample_id'] = 'exp-c-02'
    batch['samples'].append(second)
    with pytest.raises(ValueError, match='Duplicate raw crop'):
        review.validate_batch(batch, root)


def write_registry(root, batch):
    source = dict.fromkeys(SOURCE_FIELDS, '')
    source.update(source_id='BNE_TEST', institution='Biblioteca Nacional de España',
                  manuscript='MSS/8937', url=batch['source']['url'], rights_status='PERMITTED_LOCAL',
                  source_kind='historical', rights_basis='CC BY 4.0; checked source card',
                  permitted_uses='local_study|processing|private_comparison')
    sample = batch['samples'][0]
    row = dict.fromkeys(SAMPLE_FIELDS, '')
    row.update(sample_id=sample['sample_id'], target_character=sample['character'],
               source_id=source['source_id'], folio=sample['folio'], source_url=source['url'],
               source_local_path=sample['source_local_path'], source_image_id=sample['source_image_id'],
               image_width=sample['image_width'], image_height=sample['image_height'],
               image_sha256=sample['image_sha256'], attribution=batch['source']['attribution'],
               mirror_applied='true', rotation_degrees='0', original_direction='rtl',
               review_status='candidate', transcription_confidence='0.5')
    for field in ('rights_status', 'source_kind', 'rights_basis', 'permitted_uses'):
        row[field] = source[field]
    row.update(zip(('crop_x', 'crop_y', 'crop_width', 'crop_height'), sample['raw_crop']))
    source_path, evidence_path = root / 'data/source_registry.csv', root / 'data/glyph_evidence.csv'
    for path, fields, item in ((source_path, SOURCE_FIELDS, source),
                               (evidence_path, SAMPLE_FIELDS, row)):
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerow(item)
    return source_path, evidence_path


def test_registry_metadata_agrees_without_local_images(candidate):
    root, original, batch = candidate
    sources, evidence = write_registry(root, batch)
    original.unlink()
    assert len(review.validate_registry(batch, sources, evidence)) == 1
    batch['samples'][0]['folio'] = '4r'
    with pytest.raises(ValueError, match='folio'):
        review.validate_registry(batch, sources, evidence)


def test_registry_cannot_silently_accept_a_reviewed_sample(candidate):
    root, _, batch = candidate
    sources, evidence = write_registry(root, batch)
    with evidence.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    rows[0].update(review_status='reviewed', reviewer='Review fixture',
                   review_notes='Synthetic test decision', reviewed_at='2026-10-14T12:00:00+00:00')
    with evidence.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=SAMPLE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match='unreviewed'):
        review.validate_registry(batch, sources, evidence)
