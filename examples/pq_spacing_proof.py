"""Render before/after spacing words and measure exact and body-band gaps."""
import argparse
import json
from pathlib import Path

import freetype
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

from leonardus.lowercase import within
from leonardus.metrics import validate_spacing

try:
    from regular_specimen import ProofRenderer, caption
except ModuleNotFoundError:
    from examples.regular_specimen import ProofRenderer, caption

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ['no', 'op', 'pq', 'qr', 'rs', 'po', 'pr', 'pp', 'qu', 'qp', 'aq', 'qq']
WORDS = ['nopqrs', 'po pr pp pq', 'qp qu qr', 'popolo', 'proprio', 'pappa',
         'appunto', 'quadro', 'quattro', 'acqua', 'quota', 'equilibrio']


def pair_gaps(path):
    with TTFont(path) as font:
        cmap = font.getBestCmap()
        face = freetype.Face(str(path))
        face.set_pixel_sizes(0, 256)
        body = {}
        for char in set(''.join(PAIRS)):
            face.load_glyph(font.getGlyphID(cmap[ord(char)]),
                            freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = face.glyph
            bitmap, data = slot.bitmap, bytes(slot.bitmap.buffer)
            body[char] = [x+slot.bitmap_left for y in range(bitmap.rows)
                          for x in range(bitmap.width)
                          if 0 <= slot.bitmap_top-y <= 400*256/1000
                          and data[y*bitmap.pitch+x] > 127]
        result = {}
        for pair in PAIRS:
            left, right = pair
            advance = font['hmtx'][cmap[ord(left)]][0]
            result[pair] = {
                'outline_bbox_gap_units': advance-font['glyf'][cmap[ord(left)]].xMax
                                          +font['glyf'][cmap[ord(right)]].xMin,
                'projected_body_gap_units': round(advance+(min(body[right])-max(body[left]))*1000/256, 2),
            }
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    document = validate_spacing(ROOT)
    out = within(ROOT, args.out, 'build')
    if out.exists():
        raise ValueError('Use a new output directory to preserve earlier proofs')
    out.mkdir(parents=True)
    fonts = [ROOT/document['base_font'], ROOT/'fonts/Leonardus-1211-Regular.ttf']
    image = Image.new('RGB', (1500, 1950), '#faf8f2')
    draw = ImageDraw.Draw(image)
    draw.text((25, 20), 'Spaziatura p/q | stessi disegni, prima e dopo', font=caption(29), fill='#263b32')
    for i, path in enumerate(fonts):
        x = 25+i*750
        draw.text((x, 80), ['1.210 precedente', '1.211 - p/q riequilibrate'][i], font=caption(25), fill='#263b32')
        renderer = ProofRenderer(path, 70)
        for n, word in enumerate(WORDS):
            renderer.line(image, (x, 200+n*130), word)
    draw.line((750, 75, 750, 1770), fill='#bdc6b6')
    draw.text((25, 1820), 'Traslazioni p +4, q -54; advance p 400, q 405. Nessun cambiamento di forma.',
              font=caption(24), fill='#263b32')
    image.save(out/'words-comparison.png')
    for pt in (12, 18, 36, 72):
        page = Image.new('RGB', (1800, 1100), '#faf8f2')
        draw = ImageDraw.Draw(page)
        draw.text((25, 20), f'Spaziatura p/q | {pt} pt a 96 DPI | HarfBuzz + FreeType', font=caption(25), fill='#263b32')
        ppem = round(pt*96/72)
        for i, path in enumerate(fonts):
            x = 25+i*900
            draw.text((x, 80), ['1.210', '1.211'][i], font=caption(24), fill='#263b32')
            renderer = ProofRenderer(path, ppem)
            for n, text in enumerate(['nopqrs', 'popolo proprio', 'pappa appunto', 'quadro quattro', 'acqua quota', 'equilibrio']):
                renderer.line(page, (x, 190+n*max(80, round(ppem*1.6))), text)
        page.save(out/f'words-{pt}pt.png')
    result = {'before': pair_gaps(fonts[0]), 'after': pair_gaps(fonts[1]),
              'scope': 'BBox gaps are exact font units. Body projections use raster ink >127 at 256 ppem between baseline and y=400. These measurements accompany word inspection; they do not certify optical uniformity.'}
    (out/'pair-gaps.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
