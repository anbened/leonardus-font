"""Create an original-outline SVG comparison without manuscript reproductions."""
import argparse
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
import uharfbuzz as hb


def line(path, text, x, baseline, scale):
    with TTFont(path) as font:
        glyphs = font.getGlyphSet()
        shaper = hb.Font(hb.Face(path.read_bytes()))
        shaper.scale = (1000, 1000)
        hb.ot_font_set_funcs(shaper)
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(shaper, buffer)
        result, cursor = [], 0
        for info, position in zip(buffer.glyph_infos, buffer.glyph_positions):
            if info.codepoint == 0:
                raise ValueError('Missing comparison glyph')
            pen = SVGPathPen(glyphs)
            glyphs[font.getGlyphName(info.codepoint)].draw(pen)
            commands = pen.getCommands()
            if commands:
                result.append(f'<path transform="translate({x+(cursor+position.x_offset)*scale:.3f} {baseline-position.y_offset*scale:.3f}) scale({scale} {-scale})" d="{commands}"/>')
            cursor += position.x_advance
        return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,default=Path('fonts/Leonardus-Regular.ttf'))
    parser.add_argument('--font',type=Path,default=Path('fonts/Leonardus-1200-Regular.ttf'))
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 870">',
             '<rect width="1200" height="870" fill="#faf8f2"/>',
             '<g font-family="sans-serif" fill="#263b32">',
             '<text x="35" y="45" font-size="26">Leonardus 1.200 — sei completamenti ragionati</text>',
             '<text x="35" y="78" font-size="17">Confronto fra contorni originali del progetto. Nessuna riproduzione del manoscritto.</text>']
    for n, char in enumerate('jkvwxy'):
        parts.append(f'<text x="{90+n*180}" y="120" font-size="21">{char}</text>')
    for label, font, baseline in [('1.100',args.base,250),('1.200',args.font,460)]:
        parts.append(f'<text x="35" y="{baseline-100}" font-size="17">{label}</text>')
        for n, char in enumerate('jkvwxy'):
            parts.append(line(font,char,90+n*180,baseline,.19))
    parts.append('<path d="M35 525H1165" stroke="#b7c3b7" fill="none"/>')
    for text, baseline in [('jazz kiwi voci web xilofono yacht',610),('abcdefghijklmnopqrstuvwxyz',715)]:
        parts.append(line(args.font,text,55,baseline,.073))
    parts.append('<text x="35" y="790" font-size="18">Le altre venti minuscole conservano i contorni della 1.100.</text>')
    parts.append('<text x="35" y="825" font-size="17">Sei scelte contemporanee motivate; non sei nuove attestazioni storiche.</text></g></svg>')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text('\n'.join(parts)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
