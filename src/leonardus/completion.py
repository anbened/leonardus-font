"""Build the delegated, reasoned lowercase candidate without replacing checkpoints."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

from .fontbuild import _svg_to_glyph
from .lowercase import sha, within
from .regular import accent_features

MANIFEST = 'data/lowercase_completion_2026-10-15.json'
LETTERS = set('jkvwxy')


def validate_completion(root: Path) -> dict:
    root = Path(root).resolve()
    document = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (document['schema_version'] != 1 or document['version'] != '1.200'
            or document['status'] != 'delegated_design_candidate_for_user_trial'
            or document['base_version'] != '1.100'
            or document['family'] != 'Leonardus 1200'
            or document['postscript'] != 'Leonardus-1200-Regular'
            or document['human_visual_design_approval'] is not False
            or document['public_release_approved'] is not False
            or set(document['glyphs']) != LETTERS):
        raise ValueError('Expected delegated six-letter completion candidate, not human approval')
    base = within(root, document['base_font'], 'fonts')
    if sha(base) != document['base_font_sha256']:
        raise ValueError('Preserved base font changed')
    for key in ('authorization', 'segmentation_assessment', 'research_assessment'):
        path = within(root, document[key], 'data')
        if sha(path) != document[key+'_sha256']:
            raise ValueError('Completion research or authorization checkpoint changed')
    authority = json.loads((root/document['authorization']).read_text(encoding='utf-8'))
    if (authority['scope'] != '26_basic_lowercase'
            or authority['individual_human_visual_approval'] is not False
            or not authority['instruction_quote'].strip()):
        raise ValueError('Explicit 26-letter delegation required')
    for letter, record in document['glyphs'].items():
        path = within(root, record['file'], 'glyphs/regular/release-1.200')
        if (sha(path) != record['sha256'] or record['classification'] != 'reasoned_completion'
                or not record['rationale'].strip() or not record['parent_motifs']
                or type(record['advance']) is not int):
            raise ValueError('Completion source, classification or rationale differs')
        svg = ET.parse(path).getroot()
        if (svg.get('viewBox') != '0 0 1000 1000'
                or any(e.get('stroke') not in (None, 'none') for e in svg.iter())
                or any(not e.get('d', '').rstrip().upper().endswith('Z')
                       for e in svg.iter('{http://www.w3.org/2000/svg}path'))):
            raise ValueError('Completion SVG requires closed filled paths in the standard cell')
        glyph = _svg_to_glyph(path)
        glyph.recalcBounds(None)
        if (glyph.numberOfContours < 1 or not 0 <= glyph.xMin < glyph.xMax < record['advance']
                or not -200 <= glyph.yMin < glyph.yMax <= 800):
            raise ValueError(f'Completion bounds exceed the cell for {letter}')
    return document


def build_completion(output: Path, root: Path = Path('.')) -> dict:
    from .release import build_release

    root, output = Path(root).resolve(), Path(output).resolve()
    document = validate_completion(root)
    protected = {root/'fonts/Leonardus-Regular.ttf', root/'fonts/previous/Leonardus-Regular-1.000.ttf'}
    if output in {p.resolve() for p in protected}:
        raise ValueError('Cannot overwrite a preserved approved font')
    if output.exists():
        with TTFont(output) as previous:
            if previous['name'].getDebugName(6) != document['postscript']:
                raise ValueError('Cannot overwrite another font family or category')
    with TemporaryDirectory(prefix='leonardus-completion-') as temporary:
        base = Path(temporary)/'base.ttf'
        build_release(base, root, version='1.100')
        if sha(base) != document['base_font_sha256']:
            raise ValueError('Rebuilt 1.100 differs from the preserved checkpoint')
        with TTFont(base, recalcTimestamp=False) as font:
            font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
            cmap = font.getBestCmap()
            for letter, record in document['glyphs'].items():
                name = cmap[ord(letter)]
                glyph = _svg_to_glyph(root/record['file'])
                glyph.recalcBounds(None)
                font['glyf'][name] = glyph
                font['hmtx'][name] = (record['advance'], glyph.xMin)
            reverse = {name: cp for cp, name in cmap.items()}
            records = {}
            for name in font.getGlyphOrder():
                glyph = font['glyf'][name]
                glyph.recalcBounds(font['glyf'])
                records[name] = {'codepoint': reverse.get(name),
                                 'bounds': [getattr(glyph, k, 0) for k in ('xMin','yMin','xMax','yMax')]}
            for tag in ('GPOS', 'GSUB', 'GDEF'):
                if tag in font:
                    del font[tag]
            addOpenTypeFeaturesFromString(font, accent_features(records))
            font['OS/2'].recalcAvgCharWidth(font)
            font['head'].fontRevision = 1.200
            names = {
                1: document['family'], 2: 'Regular', 3: 'Leonardus:1.200:Regular',
                4: document['family']+' Regular',
                5: 'Version 1.200; reasoned lowercase candidate for user trial',
                6: document['postscript'],
                10: 'Contemporary LTR typeface. All 26 lowercase forms have explicit design rationale: 20 linked to human-reviewed readings and six reasoned contemporary completions. Delegated agent research is distinct from human visual review. NOT authenticated handwriting or signature. No source images embedded.',
            }
            for name_id, value in names.items():
                font['name'].setName(value, name_id, 3, 1, 0x409)
                font['name'].setName(value, name_id, 1, 0, 0)
            output.parent.mkdir(parents=True, exist_ok=True)
            font.save(output)
    return {'file': str(output), 'version': '1.200', 'family': document['family'],
            'status': document['status'], 'license': 'OFL-1.1', 'codepoints': 119,
            'glyphs': 121, 'changed_lowercase': sorted(LETTERS), 'sha256': sha(output)}
