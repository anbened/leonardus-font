"""Protect the accepted evidence and the correspondence of the new review batch."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from leonardus.evidence import validated_samples
from examples.corpus_review import recorded_reviews

ROOT = Path(__file__).resolve().parents[1]


def before_recorded_reviews(data):
    """Reconstruct the batch checkpoint by undoing only receipt-backed review fields."""
    reviews = recorded_reviews(ROOT / 'data')
    lines = data.splitlines(keepends=True)
    fields = next(csv.reader([lines[0].decode('utf-8')]))
    for index, line in enumerate(lines[1:], 1):
        row = dict(zip(fields, next(csv.reader([line.decode('utf-8')]))))
        if row['sample_id'] not in reviews:
            continue
        recorded = reviews[row['sample_id']]
        assert row['review_status'] == 'reviewed'
        assert all(row[key] == recorded[key] for key in ('reviewer', 'review_notes', 'reviewed_at'))
        row.update(review_status='candidate', reviewer='', review_notes='', reviewed_at='')
        stream = io.StringIO(newline='')
        csv.DictWriter(stream, fields, lineterminator='\r\n' if line.endswith(b'\r\n') else '\n').writerow(row)
        lines[index] = stream.getvalue().encode('utf-8')
    return b''.join(lines)


def test_expansion_preserves_original_evidence_bytes_and_decisions():
    batch = json.loads((ROOT / 'data/lowercase_expansion_2026-10-14.json').read_text(encoding='utf-8'))
    data = (ROOT / 'data/glyph_evidence.csv').read_bytes()
    # The original 44 records occupy 45 physical lines; quoted notes have no newlines.
    prefix = b''.join(data.splitlines(keepends=True)[:45])
    assert hashlib.sha256(prefix).hexdigest() == batch['baseline_evidence_prefix_sha256']
    original = list(csv.DictReader(io.StringIO(prefix.decode('utf-8'))))
    canonical = json.dumps(original, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    assert hashlib.sha256(canonical).hexdigest() == batch['baseline_evidence_rows_sha256']
    assert len(original) == batch['baseline_evidence_count'] == 44
    assert Counter(row['review_status'] for row in original) == {'reviewed': 40, 'candidate': 4}


def test_expansion_coverage_and_only_recorded_reviews_are_promoted():
    batch = json.loads((ROOT / 'data/lowercase_expansion_2026-10-14.json').read_text(encoding='utf-8'))
    rows = validated_samples(ROOT / 'data/source_registry.csv', ROOT / 'data/glyph_evidence.csv')
    ids = {sample['sample_id'] for sample in batch['samples']}
    new = [row for row in rows if row['sample_id'] in ids]
    assert len(new) == len(ids) == len(batch['samples']) == 65
    second = json.loads((ROOT / 'data/lowercase_search_2026-10-14.json').read_text(encoding='utf-8'))
    assert len(rows) == 109 + len(second['samples'])
    reviews = recorded_reviews(ROOT / 'data')
    assert len(set(reviews) & ids) == 46
    assert Counter(row['review_status'] for row in new) == {'candidate': 19, 'reviewed': 46}
    assert all(row['review_status'] == 'candidate' and
               not any(row[key] for key in ('reviewer', 'review_notes', 'reviewed_at'))
               for row in new if row['sample_id'] not in reviews)
    expected = {letter: {'candidates': sum(s['character'] == letter for s in batch['samples']),
                         'folios': sorted({s['folio'] for s in batch['samples'] if s['character'] == letter})}
                for letter in sorted({s['character'] for s in batch['samples']})}
    assert batch['coverage'] == expected
    assert set(expected).isdisjoint('adelnor')


def test_second_search_preserves_all_previous_evidence_and_review_gates():
    second = json.loads((ROOT / 'data/lowercase_search_2026-10-14.json').read_text(encoding='utf-8'))
    data = (ROOT / 'data/glyph_evidence.csv').read_bytes()
    prefix = b''.join(before_recorded_reviews(data).splitlines(keepends=True)[:110])
    assert second['baseline_evidence_count'] == 109
    assert hashlib.sha256(prefix).hexdigest() == second['baseline_evidence_prefix_sha256']
    rows = validated_samples(ROOT / 'data/source_registry.csv', ROOT / 'data/glyph_evidence.csv')
    assert len(rows) == 144
    assert sum(row['review_status'] == 'reviewed' for row in rows) == 101
    ids = {sample['sample_id'] for sample in second['samples']}
    assert len(ids) == len(second['samples']) == 35
    reviews = recorded_reviews(ROOT / 'data')
    assert len(set(reviews) & ids) == 15
    assert Counter(row['review_status'] for row in rows if row['sample_id'] in ids) == {'reviewed': 15, 'candidate': 20}
    assert all(row['review_status'] == 'candidate' for row in rows if row['sample_id'] in ids - set(reviews))
    assert all(sample['folio_status'].endswith('pending_review') for sample in second['samples'])


def test_recorded_group_one_has_exactly_five_m_and_five_t():
    plan = json.loads((ROOT / 'data/guided_review_2026-10-14.json').read_text(encoding='utf-8'))
    reviews = recorded_reviews(ROOT / 'data')
    group_one = set(plan['groups'][0]['sample_ids'])
    assert group_one.issubset(reviews)
    rows = validated_samples(ROOT / 'data/source_registry.csv', ROOT / 'data/glyph_evidence.csv')
    assert Counter(row['target_character'] for row in rows if row['sample_id'] in group_one) == {'m': 5, 't': 5}
    assert Counter(row['review_status'] for row in rows) == {'reviewed': 101, 'candidate': 43}
    assert all(item['letter_reading'] == 'accepted' and item['folio_review'] == 'confirmed'
               and item['case_review'] == 'lowercase' for item in reviews.values())


def test_all_seven_guided_groups_and_only_their_samples_are_recorded():
    plan = json.loads((ROOT / 'data/guided_review_2026-10-14.json').read_text(encoding='utf-8'))
    selected = {sid for group in plan['groups'] for sid in group['sample_ids']}
    reviews = recorded_reviews(ROOT / 'data')
    assert set(reviews) == selected and len(selected) == 61
    assert len(plan['groups']) == 7
    first = json.loads((ROOT / 'data/lowercase_expansion_2026-10-14.json').read_text(encoding='utf-8'))
    second = json.loads((ROOT / 'data/lowercase_search_2026-10-14.json').read_text(encoding='utf-8'))
    expansion_ids = {sample['sample_id'] for batch in (first, second) for sample in batch['samples']}
    rows = validated_samples(ROOT / 'data/source_registry.csv', ROOT / 'data/glyph_evidence.csv')
    assert Counter(row['target_character'] for row in rows if row['sample_id'] in selected) == {
        'b': 5, 'c': 4, 'f': 4, 'g': 5, 'h': 5, 'i': 4, 'm': 5,
        'p': 5, 'q': 5, 's': 5, 't': 5, 'u': 5, 'z': 4}
    assert all(row['review_status'] == ('reviewed' if row['sample_id'] in selected else 'candidate')
               for row in rows if row['sample_id'] in expansion_ids)


def test_capitals_and_search_misses_do_not_create_lowercase_evidence():
    second = json.loads((ROOT / 'data/lowercase_search_2026-10-14.json').read_text(encoding='utf-8'))
    assert set(second['coverage']) == set('bchijvxyz')
    assert not set('kw') & {sample['character'] for sample in second['samples']}
    assert len(second['excluded_observations']) == 4
    assert all(obs['status'] == 'excluded_from_lowercase_evidence'
               for obs in second['excluded_observations'])
    concordances = {item['viewer_page']: item for item in second['folio_concordances']}
    assert concordances[303]['editorial_folio'] == '153v'
    assert concordances[319]['status'] == concordances[147]['status'] == 'rejected_arithmetic_mapping'
    for letter, coverage in second['coverage'].items():
        matching = [sample for sample in second['samples'] if sample['character'] == letter]
        assert coverage == {'candidates': len(matching), 'folios': sorted({s['folio'] for s in matching})}
