"""Check actual unhinted ink overlap for every pair of the 52 basic letters."""
import argparse
import json
from pathlib import Path

import freetype
from fontTools.ttLib import TTFont


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font',type=Path,default=Path('dist/regular/Leonardus-Alpha0200-Regular.ttf'))
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--ppem',type=int,default=128)
    args=parser.parse_args()
    if args.ppem < 1:parser.error('--ppem must be positive')
    with TTFont(args.font) as font:
        cmap=font.getBestCmap()
        face=freetype.Face(str(args.font));face.set_pixel_sizes(0,args.ppem)
        letters='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        ink={};adv={}
        for char in letters:
            name=cmap[ord(char)]
            face.load_glyph(font.getGlyphID(name),freetype.FT_LOAD_RENDER|freetype.FT_LOAD_NO_HINTING)
            slot=face.glyph;bitmap=slot.bitmap;pixels=bytes(bitmap.buffer)
            ink[char]={(x+slot.bitmap_left,y-slot.bitmap_top) for y in range(bitmap.rows)
                       for x in range(bitmap.width) if pixels[y*bitmap.pitch+x]>127}
            adv[char]=round(font['hmtx'][name][0]*args.ppem/1000)
    collisions=[]
    for left in letters:
        for right in letters:
            overlap=ink[left]&{(x+adv[left],y) for x,y in ink[right]}
            if overlap:collisions.append([left+right,len(overlap)])
    result={'ppem':args.ppem,'threshold':127,'tested_pairs':len(letters)**2,'ink_collisions':collisions,
            'scope':f'Actual unhinted grayscale ink >127 at {args.ppem}px/em; no claim of optical spacing quality, all sizes, or kerning necessity'}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
    if collisions:raise SystemExit(1)


if __name__=='__main__':main()
