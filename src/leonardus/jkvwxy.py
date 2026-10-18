"""Integrate the selected six contemporary completions, preserving historical status."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

from .fontbuild import _svg_to_glyph
from .lowercase import sha, within
from .regular import accent_features

MANIFEST = 'glyphs/regular/release-1.230.json'
SELECTION = {'j': 'A', 'k': 'B', 'v': 'B', 'w': 'B', 'x': 'B', 'y': 'B'}


def validate_integration(root):
    root = Path(root).resolve()
    document = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (document['schema_version'] != 1 or document['version'] != '1.230'
            or document['status'] != 'selected_jkvwxy_completions_for_integration'
            or document['family'] != 'Leonardus 1230'
            or document['postscript'] != 'Leonardus-1230-Regular'
            or document['base_version'] != '1.220' or document['license'] != 'OFL-1.1'
            or document['public_release_approved'] is not False
            or set(document['glyphs']) != set(SELECTION)):
        raise ValueError('Expected the selected six-letter completion integration candidate')
    for key, directory in [('base_font', 'fonts'), ('study_manifest', 'data'),
                           ('design_review_receipt', 'data')]:
        if sha(within(root, document[key], directory)) != document[key+'_sha256']:
            raise ValueError('Base, study or human selection checkpoint changed')
    study = json.loads((root/document['study_manifest']).read_text(encoding='utf-8'))
    receipt = json.loads((root/document['design_review_receipt']).read_text(encoding='utf-8'))
    if (receipt['status'] != 'human_design_selection_recorded'
            or receipt['reviewer'] != 'Human review'
            or receipt['scope'] != 'selection_of_shown_jkvwxy_designs_for_integration'
            or not receipt['quote'].strip() or receipt['selected_variants'] != SELECTION
            or receipt['study_manifest'] != document['study_manifest']
            or receipt['study_manifest_sha256'] != document['study_manifest_sha256']
            or any(receipt[k] is not False for k in ('reading_changes', 'segmentation_changes',
                    'authenticity_claim', 'approval_of_other_20_lowercase', 'public_release_approved'))
            or set(receipt['glyphs']) != set(SELECTION)):
        raise ValueError('Explicit design selection must retain its actual approval scope')
    if (study['scope'] != 'jkvwxy_only' or study['status'] != 'unapproved_reasoned_completion_variants'
            or study['evidence_registry_changed'] is not False
            or sha(within(root, study['evidence'], 'data')) != study['evidence_sha256']):
        raise ValueError('Historical evidence or original study status changed')
    if sha(within(root, receipt['shown_word_proof'], 'specimen')) != receipt['shown_word_proof_sha256']:
        raise ValueError('The shown word comparison changed')
    for char, variant in SELECTION.items():
        record = document['glyphs'][char]
        original = study['variants'][variant]['glyphs'][char]
        approved = receipt['glyphs'][char]
        if (record['variant'] != variant or record['classification'] != 'reasoned_completion'
                or original['classification'] != 'unapproved_reasoned_completion'
                or record['contextual_reference_ids'] != original['reference_context_ids']
                or record['parent_motifs'] != original['parent_motifs']
                or not record['design_notes'].strip()
                or any(record[k] != original[k] or record[k] != approved[k]
                       for k in ('file', 'sha256', 'advance'))):
            raise ValueError('Integrated completion differs from the explicit selected variant')
        source = within(root, record['file'], 'glyphs/proposals/2026-10-16-jkvwxy')
        if sha(source) != record['sha256']:
            raise ValueError('Selected outline changed')
    return document


def build_integration(output, root=Path('.')):
    from .release import build_release

    root, output = Path(root).resolve(), Path(output).resolve()
    document = validate_integration(root)
    protected = [root/'fonts'/p for p in ('Leonardus-Regular.ttf', 'Leonardus-1200-Regular.ttf',
                 'Leonardus-1210-Regular.ttf', 'Leonardus-1211-Regular.ttf',
                 'Leonardus-1220-Regular.ttf', 'previous/Leonardus-Regular-1.000.ttf')]
    if output in [p.resolve() for p in protected]:
        raise ValueError('Cannot overwrite a preserved checkpoint')
    if output.exists():
        with TTFont(output) as previous:
            if previous['name'].getDebugName(6) != document['postscript']:
                raise ValueError('Cannot overwrite another font family')
    with TemporaryDirectory(prefix='leonardus-jkvwxy-integration-') as temporary:
        base = Path(temporary)/'base.ttf'
        build_release(base, root, version='1.220')
        if sha(base) != document['base_font_sha256']:
            raise ValueError('Rebuilt 1.220 differs from the preserved font')
        with TTFont(base, recalcTimestamp=False) as font:
            font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
            cmap = font.getBestCmap()
            for char, record in document['glyphs'].items():
                name = cmap[ord(char)]
                if font['hmtx'][name][0] != record['advance']:
                    raise ValueError('Selected advances must remain unchanged')
                glyph = _svg_to_glyph(root/record['file']); glyph.recalcBounds(None)
                font['glyf'][name] = glyph
                font['hmtx'][name] = (record['advance'], glyph.xMin)
            reverse = {name: cp for cp, name in cmap.items()}
            records = {}
            for name in font.getGlyphOrder():
                glyph = font['glyf'][name]; glyph.recalcBounds(font['glyf'])
                records[name] = {'codepoint': reverse.get(name), 'bounds': [
                    getattr(glyph, k, 0) for k in ('xMin', 'yMin', 'xMax', 'yMax')]}
            for tag in ('GPOS', 'GSUB', 'GDEF'):
                if tag in font: del font[tag]
            addOpenTypeFeaturesFromString(font, accent_features(records))
            font['OS/2'].recalcAvgCharWidth(font)
            font['head'].fontRevision = 1.230
            names = {
                1: document['family'], 2: 'Regular', 3: 'Leonardus:1.230:Regular',
                4: document['family']+' Regular', 5: 'Version 1.230; selected JKVWXY completion candidate',
                6: document['postscript'],
                10: 'Contemporary LTR typeface. Six completion designs selected as j A, k B, v B, w B, x B, y B. Previous AEMNU, OPQR and p/q spacing retained. Twenty lowercase linked to reviewed readings; six reasoned contemporary completions. Design selection does not confirm new readings, segmentation or authenticity. No source images embedded.',
            }
            for name_id, value in names.items():
                font['name'].setName(value, name_id, 3, 1, 0x409)
                font['name'].setName(value, name_id, 1, 0, 0)
            output.parent.mkdir(parents=True, exist_ok=True); font.save(output)
    return {'file': str(output), 'version': '1.230', 'family': document['family'],
            'status': document['status'], 'license': 'OFL-1.1', 'selected_variants': SELECTION,
            'codepoints': 119, 'glyphs': 121, 'sha256': sha(output)}
