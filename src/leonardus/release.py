"""Compile the approved Regular forms with OFL and validated Windows metadata.

Code: MIT. Original font outlines: copyright 2026 Leonardus Lab contributors,
SIL Open Font License 1.1, https://openfontlicense.org (glyphs/regular/OFL.txt).
Historical source reproductions have separate rights; none are embedded here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fontTools.ttLib import TTFont

from .proposal import text_sha256
from .regular import build_regular

UNCHANGED_TABLES = ('cmap', 'glyf', 'hmtx', 'GPOS', 'GSUB', 'GDEF')


def build_release_1000(output: Path, root: Path = Path('.')) -> dict:
    root, output = Path(root), Path(output)
    config = json.loads((root / 'glyphs/regular/release-1.000.json').read_text(encoding='utf-8'))
    if (config.get('schema_version') != 1 or config.get('version') != '1.000'
            or config.get('family') != 'Leonardus' or config.get('postscript') != 'LeonardusLab-Regular'
            or config.get('license') != 'OFL-1.1' or config.get('reserved_font_names') != []
            or config.get('outline_changes_from_approved_alpha') is not False):
        raise ValueError('Expected approved OFL Regular release 1.000')
    sources = root / config['source_directory']
    human_path = root / config['human_release_receipt']
    license_path = root / config['license_file']
    if (text_sha256(sources / 'design_manifest.json') != config['source_manifest_sha256']
            or text_sha256(human_path) != config['human_release_receipt_sha256']
            or text_sha256(license_path) != config['license_sha256']):
        raise ValueError('Approved source, human receipt or license hash differs')
    human = json.loads(human_path.read_text(encoding='utf-8'))
    if (human.get('status') != 'human_decisions_recorded'
            or human.get('design', {}).get('quote') != 'Approvo il disegno della alpha e la leggibilità'
            or human['design']['source_manifest_sha256'] != config['source_manifest_sha256']
            or human.get('license', {}).get('quote') != 'Scelgo OFL 1.1 per il font originale'
            or human['license'].get('reserved_font_names') != []):
        raise ValueError('Explicit full-design approval and OFL choice required')
    if output.exists():
        with TTFont(output) as old:
            if old['name'].getDebugName(6) != config['postscript']:
                raise ValueError('Cannot overwrite another font version/category')
    license_text = license_path.read_text(encoding='utf-8')
    with TemporaryDirectory(prefix='leonardus-release-') as temporary:
        alpha = Path(temporary) / 'approved-alpha.ttf'
        build_regular(sources, alpha, root)
        with TTFont(alpha, recalcTimestamp=False) as font:
            font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
            before = {tag: font.getTableData(tag) for tag in UNCHANGED_TABLES}
            font['head'].fontRevision = 1.000
            font['OS/2'].ulCodePageRange1 = 1
            font['OS/2'].ulCodePageRange2 = 0
            font['OS/2'].fsType = 0
            replacements = {
                0: config['copyright'], 1: config['family'], 2: 'Regular',
                3: 'LeonardusLab:1.000:Regular', 4: 'Leonardus Regular',
                5: 'Version 1.000; contemporary LTR Regular', 6: config['postscript'],
                10: 'Contemporary LTR reinterpretation. Seven normalized V3 letterforms linked to reviewed BNE MSS/8937 working folios 1r-4r; remaining forms are designed completions. NOT authenticated handwriting or signature. Original outlines; no source images embedded.',
                13: license_text, 14: 'https://openfontlicense.org',
            }
            for name_id, value in replacements.items():
                font['name'].setName(value, name_id, 3, 1, 0x409)
                font['name'].setName(value, name_id, 1, 0, 0)
            output.parent.mkdir(parents=True, exist_ok=True)
            font.save(output)
    with TTFont(output, recalcTimestamp=False) as font:
        font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
        if any(font.getTableData(tag) != value for tag, value in before.items()):
            raise ValueError('Release metadata changed approved glyph/metric/layout tables')
        if len(font.getBestCmap()) != 119 or font['OS/2'].fsType != 0:
            raise ValueError('Release coverage or embedding metadata differs')
    return {'file': str(output), 'status': 'compiled_regular_release',
            'version': '1.000', 'family': config['family'], 'license': 'OFL-1.1',
            'codepoints': 119, 'glyphs': 121, 'fsType': 0,
            'unchanged_tables_from_approved_alpha': list(UNCHANGED_TABLES),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def build_release(output: Path, root: Path = Path('.'), version: str = '1.100') -> dict:
    if version == '1.270':
        from .jkuvwxyz import build_integration
        return build_integration(output, root)
    if version == '1.260':
        from .bfhioq import build_integration
        return build_integration(output, root)
    if version == '1.250':
        from .cdegpt import build_integration
        return build_integration(output, root)
    if version == '1.240':
        from .capitals import build_integration
        return build_integration(output, root)
    if version == '1.230':
        from .jkvwxy import build_integration
        return build_integration(output, root)
    if version == '1.220':
        from .aemnu import build_integration
        return build_integration(output, root)
    if version == '1.211':
        from .metrics import build_spacing
        return build_spacing(output, root)
    if version == '1.210':
        from .opqr import build_integration
        return build_integration(output, root)
    if version == '1.200':
        from .completion import build_completion
        return build_completion(output, root)
    if version == '1.000':
        return build_release_1000(output, root)
    if version != '1.100':
        raise ValueError('Unsupported Regular version')
    from copy import deepcopy
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from .fontbuild import _svg_to_glyph
    from .lowercase import approved_lowercase, sha, within
    from .regular import accent_features

    root, output = Path(root).resolve(), Path(output)
    config = json.loads((root / 'glyphs/regular/release-1.100.json').read_text(encoding='utf-8'))
    if (config['version'] != '1.100' or config['license'] != 'OFL-1.1'
            or config['base_version'] != '1.000'):
        raise ValueError('Expected OFL Regular integration 1.100')
    if sha(root / 'glyphs/regular/release-1.000.json') != config['base_config_sha256']:
        raise ValueError('Base release configuration changed')
    if sha(within(root, config['design_manifest'], 'data')) != config['design_manifest_sha256']:
        raise ValueError('Integrated design manifest hash mismatch')
    manifest = approved_lowercase(root)
    support = config['dotlessi']
    support_path = within(root, support['file'], 'glyphs/regular/release-1.100')
    if sha(support_path) != support['sha256']:
        raise ValueError('Dotless i source hash mismatch')
    if output.resolve() == (root / manifest['base_font']).resolve():
        raise ValueError('Cannot overwrite the preserved 1.000 checkpoint')
    if output.exists():
        with TTFont(output) as old:
            if old['name'].getDebugName(6) != 'LeonardusLab-Regular':
                raise ValueError('Cannot overwrite another font version/category')
    records = deepcopy(json.loads((root / 'glyphs/regular/alpha-0.200/design_manifest.json')
                                 .read_text(encoding='utf-8'))['glyphs'])
    with TemporaryDirectory(prefix='leonardus-integration-') as temporary:
        base_path = Path(temporary) / 'base.ttf'
        build_release_1000(base_path, root)
        if sha(base_path) != manifest['accepted_font_sha256']:
            raise ValueError('Rebuilt base differs from the recorded 1.000 checkpoint')
        with TTFont(base_path, recalcTimestamp=False) as font:
            font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
            for letter, record in manifest['glyphs'].items():
                name = font.getBestCmap()[ord(letter)]
                glyph = _svg_to_glyph(root / record['file'])
                glyph.recalcBounds(None)
                font['glyf'][name] = glyph
                font['hmtx'][name] = (record['advance'], glyph.xMin)
                records[name].update(advance=record['advance'],
                                     bounds=[glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax])
            glyph = _svg_to_glyph(support_path)
            glyph.recalcBounds(None)
            if glyph.numberOfContours != 1:
                raise ValueError('Dotless i must contain only the approved i stem')
            # The dotless form is the first contour of the approved dotted i.
            dotted = font['glyf'][font.getBestCmap()[ord('i')]]
            end = dotted.endPtsOfContours[0] + 1
            if (list(glyph.coordinates) != list(dotted.coordinates[:end])
                    or list(glyph.flags) != list(dotted.flags[:end])):
                raise ValueError('Dotless i differs from the approved i stem')
            font['glyf']['dotlessi'] = glyph
            advance = manifest['glyphs']['i']['advance']
            font['hmtx']['dotlessi'] = (advance, glyph.xMin)
            records['dotlessi'].update(advance=advance,
                                      bounds=[glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax])
            for name, record in records.items():
                if 'components' not in record:
                    continue
                base, accent = record['components']
                xmin, _, xmax, ymax = records[base['glyph']]['bounds']
                lower = base['glyph'] == 'dotlessi' or chr(records[base['glyph']]['codepoint']).islower()
                accent['offset'] = [round((xmin + xmax) / 2 + (35 if lower else 20)), ymax + 60]
                record['advance'] = records[base['glyph']]['advance']
                pen = TTGlyphPen(font['glyf'])
                for part in record['components']:
                    pen.addComponent(part['glyph'], (1, 0, 0, 1, *part['offset']))
                composite = pen.glyph()
                composite.recalcBounds(font['glyf'])
                font['glyf'][name] = composite
                font['hmtx'][name] = (record['advance'], composite.xMin)
            for tag in ('GPOS', 'GSUB', 'GDEF'):
                if tag in font:
                    del font[tag]
            addOpenTypeFeaturesFromString(font, accent_features(records))
            bounds = [font['glyf'][name] for name in font.getGlyphOrder()]
            ascent = max(900, max(getattr(g, 'yMax', 0) for g in bounds) + 70)
            descent = min(-250, min(getattr(g, 'yMin', 0) for g in bounds) - 70)
            font['hhea'].ascent, font['hhea'].descent = ascent, descent
            font['OS/2'].sTypoAscender, font['OS/2'].sTypoDescender = ascent, descent
            font['OS/2'].usWinAscent, font['OS/2'].usWinDescent = ascent, -descent
            font['OS/2'].recalcAvgCharWidth(font)
            font['head'].fontRevision = 1.100
            replacements = {
                3: 'LeonardusLab:1.100:Regular', 5: 'Version 1.100; contemporary LTR Regular',
                10: 'Contemporary LTR reinterpretation. Seven normalized pilot forms and thirteen approved contemporary lowercase designs linked to reviewed BNE samples. Remaining forms are designed completions. Historical segmentation not certified. NOT authenticated handwriting or signature. No source images embedded.',
            }
            for name_id, value in replacements.items():
                font['name'].setName(value, name_id, 3, 1, 0x409)
                font['name'].setName(value, name_id, 1, 0, 0)
            output.parent.mkdir(parents=True, exist_ok=True)
            font.save(output)
    return {'file': str(output), 'status': 'compiled_regular_integration', 'version': '1.100',
            'family': 'Leonardus', 'license': 'OFL-1.1', 'codepoints': 119, 'glyphs': 121,
            'approved_lowercase': sorted(manifest['glyphs']), 'sha256': sha(output)}
