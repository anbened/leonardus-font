"""Correct p/q sidebearings using translations only, preserving the chosen shapes."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

from .lowercase import sha, within
from .regular import accent_features

MANIFEST = 'glyphs/regular/release-1.211.json'


def validate_spacing(root):
    root = Path(root).resolve()
    document = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (document['schema_version'] != 1 or document['version'] != '1.211'
            or document['status'] != 'pq_spacing_correction_candidate'
            or document['family'] != 'Leonardus 1211'
            or document['postscript'] != 'Leonardus-1211-Regular'
            or document['base_version'] != '1.210' or document['license'] != 'OFL-1.1'
            or not document['authorization_quote'].strip()
            or document['outline_shape_changes'] is not False
            or document['historical_evidence_changes'] is not False
            or document['new_human_visual_approval'] is not False
            or document['public_release_approved'] is not False
            or set(document['adjustments']) != set('pq')):
        raise ValueError('Expected an authorized p/q spacing correction without shape changes')
    base = within(root, document['base_font'], 'fonts')
    if sha(base) != document['base_font_sha256']:
        raise ValueError('Preserved 1.210 font changed')
    with TTFont(base) as font:
        for char, record in document['adjustments'].items():
            name = font.getBestCmap()[ord(char)]
            glyph = font['glyf'][name]
            advance, left = font['hmtx'][name]
            if record['before'] != {'advance': advance, 'left': left, 'right': advance-glyph.xMax}:
                raise ValueError('Original sidebearings differ from the checkpoint')
            after = record['after']
            if (any(type(after[k]) is not int for k in ('advance', 'left', 'right'))
                    or min(after.values()) <= 0
                    or type(record['translation_x']) is not int
                    or record['translation_x'] != after['left']-glyph.xMin
                    or after['advance']-(glyph.xMax+record['translation_x']) != after['right']):
                raise ValueError('Spacing correction must be a valid horizontal translation')
    return document


def build_spacing(output, root=Path('.')):
    from .release import build_release

    root, output = Path(root).resolve(), Path(output).resolve()
    document = validate_spacing(root)
    if output.exists():
        with TTFont(output) as previous:
            if previous['name'].getDebugName(6) != document['postscript']:
                raise ValueError('Cannot overwrite another family or preserved checkpoint')
    if output == (root/document['base_font']).resolve():
        raise ValueError('Cannot overwrite the preserved 1.210 font')
    with TemporaryDirectory(prefix='leonardus-spacing-') as temporary:
        base = Path(temporary)/'base.ttf'
        build_release(base, root, version='1.210')
        if sha(base) != document['base_font_sha256']:
            raise ValueError('Rebuilt 1.210 differs from the preserved checkpoint')
        with TTFont(base, recalcTimestamp=False) as font:
            font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
            cmap = font.getBestCmap()
            for char, record in document['adjustments'].items():
                name = cmap[ord(char)]
                glyph = font['glyf'][name]
                glyph.coordinates.translate((record['translation_x'], 0))
                glyph.recalcBounds(font['glyf'])
                font['hmtx'][name] = (record['after']['advance'], record['after']['left'])
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
            font['head'].fontRevision = 1.211
            names = {
                1: document['family'], 2: 'Regular', 3: 'Leonardus:1.211:Regular',
                4: document['family']+' Regular', 5: 'Version 1.211; p/q spacing correction candidate',
                6: document['postscript'],
                10: 'Contemporary LTR typeface. Selected OPQR shapes retained as B/A/B/B; p/q horizontally positioned and respaced without reshaping. Twenty lowercase linked to reviewed readings; six reasoned completions retained. No new historical reading, segmentation, authenticity or full-design approval. No source images embedded.',
            }
            for name_id, value in names.items():
                font['name'].setName(value, name_id, 3, 1, 0x409)
                font['name'].setName(value, name_id, 1, 0, 0)
            output.parent.mkdir(parents=True, exist_ok=True)
            font.save(output)
    return {'file': str(output), 'version': '1.211', 'family': document['family'],
            'status': document['status'], 'codepoints': 119, 'glyphs': 121,
            'outline_shape_changes': False, 'adjustments': document['adjustments'], 'sha256': sha(output)}
