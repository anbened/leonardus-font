"""Integrate the four selected OPQR designs while preserving every checkpoint."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

from .fontbuild import _svg_to_glyph
from .lowercase import sha, within
from .regular import accent_features

MANIFEST = 'glyphs/regular/release-1.210.json'
SELECTION = {'o': 'B', 'p': 'A', 'q': 'B', 'r': 'B'}


def validate_integration(root):
    root = Path(root).resolve()
    document = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (document['schema_version'] != 1 or document['version'] != '1.210'
            or document['status'] != 'selected_opqr_designs_for_integration'
            or document['family'] != 'Leonardus 1210'
            or document['postscript'] != 'Leonardus-1210-Regular'
            or document['base_version'] != '1.200' or document['license'] != 'OFL-1.1'
            or document['public_release_approved'] is not False
            or set(document['glyphs']) != set(SELECTION)):
        raise ValueError('Expected the selected four-letter integration candidate')
    for key, directory in [('base_font', 'fonts'), ('study_manifest', 'data'),
                           ('design_review_receipt', 'data')]:
        path = within(root, document[key], directory)
        if sha(path) != document[key+'_sha256']:
            raise ValueError('Base, study or human receipt checkpoint changed')
    study = json.loads((root/document['study_manifest']).read_text(encoding='utf-8'))
    receipt = json.loads((root/document['design_review_receipt']).read_text(encoding='utf-8'))
    if (receipt['status'] != 'human_design_selection_recorded'
            or receipt['reviewer'] != 'Human review'
            or receipt['scope'] != 'selection_of_shown_opqr_designs_for_integration'
            or not receipt['quote'].strip() or receipt['selected_variants'] != SELECTION
            or receipt['study_manifest'] != document['study_manifest']
            or receipt['study_manifest_sha256'] != document['study_manifest_sha256']
            or receipt['reading_changes'] is not False
            or receipt['segmentation_changes'] is not False
            or receipt['authenticity_claim'] is not False
            or receipt['approval_of_other_22_lowercase'] is not False
            or receipt['public_release_approved'] is not False
            or set(receipt['glyphs']) != set(SELECTION)):
        raise ValueError('Explicit selection must retain its actual approval scope')
    shown = within(root, receipt['shown_word_proof'], 'specimen')
    if sha(shown) != receipt['shown_word_proof_sha256']:
        raise ValueError('The shown word comparison changed')
    evidence = within(root, study['evidence'], 'data')
    if sha(evidence) != study['evidence_sha256']:
        raise ValueError('Historical evidence changed')
    for char, variant in SELECTION.items():
        record = document['glyphs'][char]
        original = study['variants'][variant]['glyphs'][char]
        approved = receipt['glyphs'][char]
        if (record['variant'] != variant or record['classification'] != 'reviewed_design'
                or record['sample_ids'] != original['reference_sample_ids']
                or not record['design_notes'].strip()
                or any(record[k] != original[k] or record[k] != approved[k]
                       for k in ('file', 'sha256', 'advance'))):
            raise ValueError('Integrated design differs from the selected variant')
        source = within(root, record['file'], 'glyphs/proposals/2026-10-15-opqr')
        if sha(source) != record['sha256']:
            raise ValueError('Selected outline changed')
    return document


def build_integration(output, root=Path('.')):
    from .release import build_release

    root, output = Path(root).resolve(), Path(output).resolve()
    document = validate_integration(root)
    if output.exists():
        with TTFont(output) as previous:
            if previous['name'].getDebugName(6) != document['postscript']:
                raise ValueError('Cannot overwrite another family or preserved checkpoint')
    protected = [root/'fonts'/p for p in ('Leonardus-Regular.ttf', 'Leonardus-1200-Regular.ttf',
                                         'previous/Leonardus-Regular-1.000.ttf')]
    if output in [p.resolve() for p in protected]:
        raise ValueError('Cannot overwrite a preserved checkpoint')
    with TemporaryDirectory(prefix='leonardus-opqr-integration-') as temporary:
        base = Path(temporary)/'base.ttf'
        build_release(base, root, version='1.200')
        if sha(base) != document['base_font_sha256']:
            raise ValueError('Rebuilt 1.200 differs from the preserved font')
        with TTFont(base, recalcTimestamp=False) as font:
            font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
            cmap = font.getBestCmap()
            for char, record in document['glyphs'].items():
                name = cmap[ord(char)]
                if font['hmtx'][name][0] != record['advance']:
                    raise ValueError('Selected advances must remain unchanged')
                glyph = _svg_to_glyph(root/record['file'])
                glyph.recalcBounds(None)
                font['glyf'][name] = glyph
                font['hmtx'][name] = (record['advance'], glyph.xMin)
            # Keep precomposed ò aligned with the new o and its combining grave.
            o = font['glyf'][cmap[ord('o')]]
            accented = font['glyf'][cmap[ord('ò')]]
            if ([c.glyphName for c in accented.components] != [cmap[ord('o')], cmap[0x0300]]):
                raise ValueError('Expected the preserved o plus grave composite')
            accented.components[1].x = round((o.xMin+o.xMax)/2+35)
            accented.components[1].y = o.yMax+60
            accented.recalcBounds(font['glyf'])
            font['hmtx'][cmap[ord('ò')]] = (font['hmtx'][cmap[ord('o')]][0], accented.xMin)
            reverse = {name: cp for cp, name in cmap.items()}
            records = {}
            for name in font.getGlyphOrder():
                glyph = font['glyf'][name]
                glyph.recalcBounds(font['glyf'])
                records[name] = {'codepoint': reverse.get(name), 'bounds': [
                    getattr(glyph, k, 0) for k in ('xMin', 'yMin', 'xMax', 'yMax')]}
            for tag in ('GPOS', 'GSUB', 'GDEF'):
                if tag in font:
                    del font[tag]
            addOpenTypeFeaturesFromString(font, accent_features(records))
            font['OS/2'].recalcAvgCharWidth(font)
            font['head'].fontRevision = 1.210
            names = {
                1: document['family'], 2: 'Regular', 3: 'Leonardus:1.210:Regular',
                4: document['family']+' Regular', 5: 'Version 1.210; selected OPQR integration candidate',
                6: document['postscript'],
                10: 'Contemporary LTR typeface. Selected OPQR designs approved as B/A/B/B. Twenty lowercase linked to reviewed readings; six reasoned contemporary completions retained. Approval concerns four designs, not new historical readings, segmentation or authenticity. No source images embedded.',
            }
            for name_id, value in names.items():
                font['name'].setName(value, name_id, 3, 1, 0x409)
                font['name'].setName(value, name_id, 1, 0, 0)
            output.parent.mkdir(parents=True, exist_ok=True)
            font.save(output)
    return {'file': str(output), 'version': '1.210', 'family': document['family'],
            'status': document['status'], 'license': 'OFL-1.1', 'selected_variants': SELECTION,
            'codepoints': 119, 'glyphs': 121, 'sha256': sha(output)}
