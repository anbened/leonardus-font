"""Validate the recorded lowercase design approvals independently of scan images."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .evidence import validated_samples
from .fontbuild import _svg_to_glyph

LETTERS = set('bcfghimpqstuz')
MANIFEST = Path('data/lowercase_design_2026-10-15.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def within(root, relative, directory):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    parent = (root / directory).resolve()
    if not parent.is_relative_to(root) or not path.is_relative_to(parent):
        raise ValueError('Source path escapes its project directory')
    return path


def approved_lowercase(root):
    root = Path(root).resolve()
    manifest = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
    if (manifest['status'] != 'designs_approved_for_integration'
            or manifest['human_design_review'] is not True or set(manifest['glyphs']) != LETTERS):
        raise ValueError('Explicit approval of all thirteen lowercase designs required')
    receipt_path = within(root, manifest['design_review_receipt'], 'data')
    if sha(receipt_path) != manifest['design_review_receipt_sha256']:
        raise ValueError('Design review receipt hash mismatch')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if (receipt['status'] != 'human_design_decisions_recorded'
            or receipt['scope'] != 'glyph_design_and_font_integration'
            or receipt['s_approval_quote'] != 'Anche la nuova s va bene, approvata.'
            or receipt['integration_quote'] != 'Procedi con l’integrazione delle minuscole nel font'
            or set(receipt['approved_designs']) != LETTERS or receipt['pending_designs'] != []
            or receipt['segmentation_approved'] is not False
            or receipt['font_integration_approved'] is not True
            or receipt['public_release_approved'] is not False):
        raise ValueError('Design receipt scope or approval set disagrees')
    prior_path = within(root, receipt['prior_design_receipt'], 'data')
    if sha(prior_path) != receipt['prior_design_receipt_sha256']:
        raise ValueError('Prior design receipt hash mismatch')
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    if (prior['scope'] != 'glyph_design_only' or prior['selected_column'] != 'proposta'
            or set(prior['approved_designs']) != LETTERS - {'s'}
            or prior['pending_designs'] != ['s']
            or any(receipt['approved_designs'][c] != r for c, r in prior['approved_designs'].items())):
        raise ValueError('Prior twelve design approvals changed')
    base = within(root, manifest['base_font'], 'fonts/previous')
    if sha(base) != manifest['accepted_font_sha256']:
        raise ValueError('Accepted base font changed')
    if sha(within(root, manifest['plan'], 'data')) != manifest['plan_sha256']:
        raise ValueError('Design plan hash mismatch')
    if sha(root / 'data/glyph_evidence.csv') != manifest['evidence_sha256']:
        raise ValueError('Evidence checkpoint changed')
    samples = {r['sample_id']: r for r in validated_samples(
        root / 'data/source_registry.csv', root / 'data/glyph_evidence.csv')}
    for letter, record in manifest['glyphs'].items():
        if (record['classification'] != 'reviewed_design' or record['design_review'] != 'approved'
                or record['segmentation_review'] != 'pending'):
            raise ValueError('Design approval does not certify segmentation or historical contours')
        path = within(root, record['file'], 'glyphs/proposals/2026-10-15-lowercase')
        if sha(path) != record['sha256']:
            raise ValueError('Design SVG hash mismatch')
        ids = record['sample_ids']
        if (len(ids) < 4 or len(ids) != len(set(ids))
                or any(sid not in samples or samples[sid]['target_character'] != letter
                       or samples[sid]['review_status'] != 'reviewed'
                       or samples[sid]['source_kind'] != 'historical' for sid in ids)):
            raise ValueError('Design references require reviewed historical letters')
        glyph = _svg_to_glyph(path)
        glyph.recalcBounds(None)
        if (type(record['advance']) is not int or not 150 <= record['advance'] <= 1000
                or glyph.numberOfContours <= 0 or glyph.xMin < 0 or glyph.xMax >= record['advance']
                or glyph.yMin < -200 or glyph.yMax > 800):
            raise ValueError('Design exceeds cell, advance or vertical bounds')
        if any(record[k] != receipt['approved_designs'][letter][k] for k in ('file', 'sha256', 'advance')):
            raise ValueError('Approved design differs from the recorded approval')
    return manifest
