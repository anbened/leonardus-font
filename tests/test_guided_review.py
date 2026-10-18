"""Keep guided annotations separate from evidence approval and original images."""
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image
import pytest
from leonardus.evidence import SAMPLE_FIELDS, SOURCE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guided_review', ROOT / 'examples/guided_review.py')
guided = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guided)


@pytest.fixture
def fixture(tmp_path):
    scans = tmp_path / 'data/scans/test'
    scans.mkdir(parents=True)
    samples, images = [], []
    for index, letter in enumerate('cf'):
        image_path = scans / f'page-{index}.png'
        image = Image.new('RGB', (100, 60))
        image.putdata([(x * 2, y * 3, 80) for y in range(60) for x in range(100)])
        image.putpixel((0, 0), (index, 0, 0))
        image.save(image_path)
        images.append(image_path)
        samples.append(dict(sample_id=f'exp-{letter}-01', character=letter,
                            page=index+1, folio=f'{index+1}r', source_image_id=f'page-{index}',
                            image_sha256=hashlib.sha256(image_path.read_bytes()).hexdigest(),
                            image_width=100, image_height=60, source_local_path=f'scans/test/page-{index}.png',
                            mirror_crop=[20, 10, 10, 20], mirror_context=[10, 5, 40, 40],
                            raw_crop=[70, 10, 10, 20], raw_context=[50, 5, 40, 40],
                            token='<script>alert(1)</script>', position=1,
                            rationale='Context & shape', doubts='Unreviewed'))
    batch = dict(batch_id='test-batch', samples=samples, source=dict(
        url='https://bnedigital.bne.es/bd/card?oid=test',
        viewer_url='https://bnedigital.bne.es/bd/es/viewer?id=test',
        attribution='Biblioteca Nacional de España'))
    batch_path = tmp_path / 'data/test-batch.json'
    batch_path.write_text(json.dumps(batch), encoding='utf-8')
    source = dict.fromkeys(SOURCE_FIELDS, '')
    source.update(source_id='BNE_TEST', institution='Biblioteca Nacional de España', manuscript='MSS/8937',
                  url=batch['source']['url'], rights_status='PERMITTED_LOCAL', source_kind='historical',
                  rights_basis='CC BY 4.0; checked source card', permitted_uses='local_study|processing|private_comparison')
    rows = []
    for sample in samples:
        row = dict.fromkeys(SAMPLE_FIELDS, '')
        row.update(sample_id=sample['sample_id'], target_character=sample['character'], source_id='BNE_TEST',
                   folio=sample['folio'], source_url=source['url'], source_local_path=sample['source_local_path'],
                   source_image_id=sample['source_image_id'], image_width=100, image_height=60,
                   image_sha256=sample['image_sha256'], attribution=batch['source']['attribution'],
                   mirror_applied='true', rotation_degrees='0', original_direction='rtl',
                   review_status='candidate', transcription_confidence='0.5')
        for field in ('rights_status', 'source_kind', 'rights_basis', 'permitted_uses'):
            row[field] = source[field]
        row.update(zip(('crop_x', 'crop_y', 'crop_width', 'crop_height'), sample['raw_crop']))
        rows.append(row)
    for path, fields, records in ((tmp_path / 'data/source_registry.csv', SOURCE_FIELDS, [source]),
                                  (tmp_path / 'data/glyph_evidence.csv', SAMPLE_FIELDS, rows)):
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)
    plan = dict(review_id='review-test', status='pending_human_review', batches=['data/test-batch.json'],
                batch_sha256={'data/test-batch.json': guided.digest(batch_path.read_bytes())},
                groups=[dict(id='c-group', title='c <script>', letters=['c'], rationale='First & group',
                             sample_ids=['exp-c-01'], letter_questions={'c': 'Contour <or> context?'},
                             sample_notes={'exp-c-01': 'Do not assume <confirmation>'})], deferred=['f'])
    return tmp_path, images, batch, plan


def draft(plan):
    return dict(review_id=plan['review_id'], status='review_draft', plan_sha256='a' * 64,
                groups=guided.export_groups(plan), decisions=[dict(sample_id='exp-c-01', letter_reading='',
                folio_review='', case_review='', notes='')])


def record_fixture_review(fixture):
    root, _, _, plan = fixture
    path = root / 'data/review-plan.json'
    path.write_text(json.dumps(plan), encoding='utf-8')
    receipt = dict(status='human_decisions_recorded', review_id=plan['review_id'],
                   plan_path='data/review-plan.json', plan_sha256=guided.digest(path.read_bytes()),
                   group_id='c-group', reviewer='Human review', recorded_at='2026-10-15T06:28:13+00:00',
                   decisions=[dict(sample_id='exp-c-01', letter_reading='accepted',
                                   folio_review='confirmed', case_review='lowercase', notes='Synthetic fixture')])
    receipt_path = root / 'data/human_guided_review_fixture.json'
    receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
    recorded = guided.corpus.recorded_reviews(root / 'data')['exp-c-01']
    evidence = root / 'data/glyph_evidence.csv'
    with evidence.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    rows[0]['review_status'] = 'reviewed'
    for field in ('reviewer', 'review_notes', 'reviewed_at'):
        rows[0][field] = recorded[field]
    with evidence.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=SAMPLE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return receipt_path, receipt


def test_recorded_review_is_checked_and_rendered_readonly(fixture):
    root, _, _, plan = fixture
    record_fixture_review(fixture)
    guided.validate_plan(plan, root)
    document = guided.render_review(plan, 'a' * 64, root).read_text(encoding='utf-8')
    assert 'Revisione umana registrata' in document
    assert 'Revisione guidata completata' in document
    assert 'La pagina apre il primo gruppo ancora da valutare.' not in document
    assert 'value="accepted" selected' in document
    assert document.count(' disabled') == 4
    embedded = document.split('<script id="review-data" type="application/json">')[1].split('</script>')[0]
    exported = json.loads(embedded)
    assert exported['decisions'][0]['letter_reading'] == 'accepted'
    guided.validate_decisions(exported, plan, 'a' * 64)


def test_recorded_folio_and_case_are_shown_as_confirmed(fixture):
    root, _, batch, plan = fixture
    batch['samples'][0].update(folio_status='working_mapping_pending_review',
                               case_status='unresolved_isolated_label')
    path = root / 'data/test-batch.json'
    path.write_text(json.dumps(batch), encoding='utf-8')
    plan['batch_sha256']['data/test-batch.json'] = guided.digest(path.read_bytes())
    record_fixture_review(fixture)
    index = guided.corpus.render_dossier(batch, 'build/recorded-corpus', root)
    document = index.read_text(encoding='utf-8')
    assert 'Caso confermato: minuscola confermata nella revisione registrata' in document
    assert 'Foliazione di lavoro DA REVISIONARE' not in document
    assert 'maiuscola/minuscola non stabilita' not in document


@pytest.mark.parametrize('mutation,message', [
    (lambda r: r.update(status='review_draft'), 'recorded human'),
    (lambda r: r.update(plan_sha256='0' * 64), 'SHA-256'),
    (lambda r: r.update(group_id='unknown'), 'planned group'),
    (lambda r: r.update(decisions=[]), 'exactly'),
    (lambda r: r['decisions'][0].update(letter_reading='uncertain'), 'explicit'),
    (lambda r: r['decisions'][0].update(folio_review='uncertain'), 'explicit'),
    (lambda r: r['decisions'][0].update(case_review='uppercase'), 'explicit'),
])
def test_draft_or_mismatched_receipt_cannot_approve_registry(fixture, mutation, message):
    root, _, _, plan = fixture
    path, receipt = record_fixture_review(fixture)
    mutation(receipt)
    path.write_text(json.dumps(receipt), encoding='utf-8')
    with pytest.raises(ValueError, match=message):
        guided.validate_plan(plan, root)


def test_recorded_receipt_cannot_hide_missing_csv_review(fixture):
    root, _, _, plan = fixture
    record_fixture_review(fixture)
    path = root / 'data/glyph_evidence.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    rows[0].update(review_status='candidate', reviewer='', review_notes='', reviewed_at='')
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=SAMPLE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match='recorded human decision'):
        guided.validate_plan(plan, root)


def test_metadata_validation_checks_whole_batch_without_images(fixture):
    root, images, _, plan = fixture
    for image in images:
        image.unlink()
    samples, _ = guided.validate_plan(plan, root)
    assert set(samples) == {'exp-c-01', 'exp-f-01'}


@pytest.mark.parametrize('mutation,message', [
    (lambda p: p.update(status='approved'), 'promote'),
    (lambda p: p['groups'][0]['sample_ids'].append('unknown'), 'Unknown'),
    (lambda p: p['groups'][0]['sample_ids'].append('exp-c-01'), 'Duplicate sample'),
    (lambda p: p['groups'][0].update(sample_ids=['exp-c-01'] * 11), '1 to 10'),
    (lambda p: p['groups'][0].update(letters=['f']), 'match group'),
    (lambda p: p['batch_sha256'].update({'data/test-batch.json': '0' * 64}), 'SHA-256 mismatch'),
    (lambda p: p['groups'][0]['sample_notes'].update({'unknown': 'note'}), 'sample_notes'),
    (lambda p: p['groups'][0]['letter_questions'].update({'f': 'question'}), 'letter_questions'),
])
def test_invalid_plans_are_rejected(fixture, mutation, message):
    root, _, _, plan = fixture
    mutation(plan)
    with pytest.raises(ValueError, match=message):
        guided.validate_plan(plan, root)


def test_duplicate_group_and_cross_group_selection_are_rejected(fixture):
    root, _, _, plan = fixture
    second = copy.deepcopy(plan['groups'][0])
    plan['groups'].append(second)
    with pytest.raises(ValueError, match='Duplicate group'):
        guided.validate_plan(plan, root)
    second['id'] = 'other-group'
    with pytest.raises(ValueError, match='Duplicate sample'):
        guided.validate_plan(plan, root)


def test_registry_checked_for_unselected_samples(fixture):
    root, _, batch, plan = fixture
    batch['samples'][1]['folio'] = '9r'
    path = root / 'data/test-batch.json'
    path.write_text(json.dumps(batch), encoding='utf-8')
    plan['batch_sha256']['data/test-batch.json'] = guided.digest(path.read_bytes())
    with pytest.raises(ValueError, match='folio'):
        guided.validate_plan(plan, root)


def test_tampered_unselected_image_fails_before_any_output(fixture):
    root, images, _, plan = fixture
    images[1].write_bytes(images[1].read_bytes() + b'tampered')
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        guided.render_review(plan, 'a' * 64, root)
    assert not (root / 'build/guided-review').exists()


def test_wrong_image_dimensions_fail_before_any_output(fixture):
    root, _, batch, plan = fixture
    batch['samples'][0]['image_height'] = 61
    path = root / 'data/test-batch.json'
    path.write_text(json.dumps(batch), encoding='utf-8')
    plan['batch_sha256']['data/test-batch.json'] = guided.digest(path.read_bytes())
    evidence = root / 'data/glyph_evidence.csv'
    with evidence.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    rows[0]['image_height'] = '61'
    with evidence.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=SAMPLE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match='dimensions mismatch'):
        guided.render_review(plan, 'a' * 64, root)
    assert not (root / 'build/guided-review').exists()


def test_render_is_offline_escaped_blank_and_preserves_originals(fixture):
    root, images, batch, plan = fixture
    before = [image.read_bytes() for image in images]
    index = guided.render_review(plan, 'a' * 64, root)
    assert [image.read_bytes() for image in images] == before
    document = index.read_text(encoding='utf-8')
    assert 'c &lt;script&gt;' in document and '&lt;script&gt;alert(1)&lt;/script&gt;' in document
    assert 'Contour &lt;or&gt; context?' in document
    assert document.count('<option value="" selected>Da valutare</option>') == 3
    assert 'folio proposto' in document.lower() and 'da revisionare' in document
    assert 'tipo di contesto non registrato' in document
    assert 'review_draft' in document and 'pending_human_review' not in document
    assert 'localStorage' not in document and 'fetch(' not in document and '<script src=' not in document
    assert "connect-src 'none'" in document
    embedded = document.split('<script id="review-data" type="application/json">')[1].split('</script>')[0]
    exported = json.loads(embedded)
    guided.validate_decisions(exported, plan, 'a' * 64)
    assert exported['decisions'][0]['letter_reading'] == ''
    assert len(list(index.parent.glob('*.png'))) == 3
    with Image.open(index.parent / 'exp-c-01-crop.png') as image:
        assert image.size == (30, 60)
        with Image.open(images[0]) as original:
            assert image.getpixel((0, 0)) == original.getpixel((79, 10))
    with Image.open(index.parent / 'exp-c-01-context.png') as image:
        assert image.getpixel((10, 5)) == (208, 32, 32)
    with Image.open(index.parent / 'exp-c-01-original.png') as image:
        assert image.size == (10, 20)


def test_output_is_restricted_to_exact_ignored_directory(fixture):
    root, _, _, plan = fixture
    for destination in ('data/scans/test', 'build/another', 'build/guided-review/subfolder'):
        with pytest.raises(ValueError, match='must be build/guided-review'):
            guided.render_review(plan, 'a' * 64, root, destination)


def test_output_directory_symlink_cannot_write_to_scans(fixture):
    root, images, _, plan = fixture
    out = root / 'build/guided-review'
    out.parent.mkdir(parents=True)
    scans = images[0].parent
    before = {path.name: path.read_bytes() for path in scans.iterdir()}
    try:
        out.symlink_to(scans, target_is_directory=True)
    except OSError:
        pytest.skip('Creating symlinks requires privileges on this platform')
    with pytest.raises(ValueError, match='directory escapes'):
        guided.render_review(plan, 'a' * 64, root)
    assert {path.name: path.read_bytes() for path in scans.iterdir()} == before


def test_output_symlink_cannot_modify_originals(fixture):
    root, images, _, plan = fixture
    out = root / 'build/guided-review'
    out.mkdir(parents=True)
    try:
        (out / 'exp-c-01-crop.png').symlink_to(images[0])
    except OSError:
        pytest.skip('Creating symlinks requires privileges on this platform')
    before = images[0].read_bytes()
    with pytest.raises(ValueError, match='escapes'):
        guided.render_review(plan, 'a' * 64, root)
    assert images[0].read_bytes() == before


def test_blank_and_uncertain_drafts_do_not_approve_evidence(fixture):
    _, _, _, plan = fixture
    document = draft(plan)
    assert guided.validate_decisions(document, plan, 'a' * 64) is document
    document['decisions'][0].update(letter_reading='uncertain', folio_review='uncertain', case_review='uncertain', notes='Alternative reading')
    assert guided.validate_decisions(document, plan, 'a' * 64) is document


@pytest.mark.parametrize('mutation,message', [
    (lambda d: d.update(plan_sha256='b' * 64), 'SHA-256 mismatch'),
    (lambda d: d.update(status='approved'), 'Draft status'),
    (lambda d: d['decisions'][0].update(sample_id='unknown'), 'Unknown'),
    (lambda d: d['decisions'].append(copy.deepcopy(d['decisions'][0])), 'Duplicate'),
    (lambda d: d['decisions'][0].update(letter_reading='reviewed'), 'letter_reading'),
    (lambda d: d['decisions'][0].update(folio_review=[]), 'folio_review'),
    (lambda d: d['decisions'][0].update(case_review='prose'), 'case_review'),
    (lambda d: d['decisions'][0].update(notes={}), 'notes'),
    (lambda d: d['decisions'][0].update(reviewer='Personal field'), 'documented fields'),
    (lambda d: d.update(decisions=[]), 'every selected sample'),
    (lambda d: d.update(groups=[]), 'Draft groups'),
])
def test_invalid_decision_drafts_are_rejected(fixture, mutation, message):
    _, _, _, plan = fixture
    document = draft(plan)
    mutation(document)
    with pytest.raises(ValueError, match=message):
        guided.validate_decisions(document, plan, 'a' * 64)
