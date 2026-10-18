"""Compare the exact mixed CDEGPT selection with the preserved Regular 1.240."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from leonardus.cdegpt import validate_integration
from leonardus.lowercase import within

try:
    from regular_specimen import ProofRenderer, caption
except ModuleNotFoundError:
    from examples.regular_specimen import ProofRenderer, caption

ROOT = Path(__file__).resolve().parents[1]
WORDS = ['Codice Carta', 'Disegno Duca', 'Esperienza Europa', 'Genio Geometria',
         'Pittura Progetto', 'Tempo Toscana', 'Conoscere le idee', 'Pittura e pensiero',
         'CODICE E TEMPO', 'PROGETTO E ARTE', 'E È E\u0300 É E\u0301', 'La Natura e il Genio']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); document = validate_integration(ROOT)
    out = within(ROOT, args.out, 'build')
    if out.exists(): raise ValueError('Preserve previous proofs; use a new output path')
    image = Image.new('RGB', (1600, 2010), '#faf8f2'); draw = ImageDraw.Draw(image)
    draw.text((25, 20), 'Leonardus 1.250 | C B, D B, E A, G B, P B, T B', font=caption(27), fill='#263b32')
    for x, path, label in [(25, ROOT/document['base_font'], '1.240 precedente'),
                           (825, ROOT/'fonts/Leonardus-1250-Regular.ttf', '1.250 - combinazione scelta')]:
        draw.text((x, 75), label, font=caption(24), fill='#263b32')
        ProofRenderer(path, 125).line(image, (x, 225), 'C D E G P T')
        for n, word in enumerate(WORDS): ProofRenderer(path, 60).line(image, (x, 345+110*n), word)
        ProofRenderer(path, 50).line(image, (x, 1730), 'CC DD EE GG PP TT')
        ProofRenderer(path, 36).line(image, (x, 1830), 'Ca Co  Di Do  Es Eu  Ge Gi  Pi Pr  Te To')
    draw.line((800, 70, 800, 1870), fill='#bdc6b6')
    draw.text((25, 1930), 'Sei maiuscole contemporanee scelte; minuscole e advance conservati. OFL 1.1.',
              font=caption(23), fill='#263b32')
    out.parent.mkdir(parents=True, exist_ok=True); image.save(out)
    for pt in (12, 18, 36, 72):
        ppem = round(pt*96/72); step = max(38, round(ppem*1.65))
        sheet = Image.new('RGB', (1700, 160+step*len(WORDS)), '#faf8f2'); draw = ImageDraw.Draw(sheet)
        draw.text((20, 15), f'Parole | {pt} pt / 96 DPI | 1.240 e 1.250', font=caption(22), fill='#263b32')
        for x, path, label in [(20, ROOT/document['base_font'], '1.240'),
                               (870, ROOT/'fonts/Leonardus-1250-Regular.ttf', '1.250')]:
            draw.text((x, 55), label, font=caption(20), fill='#263b32')
            for n, word in enumerate(WORDS): ProofRenderer(path, ppem).line(sheet, (x, max(120,100+ppem)+n*step), word)
        sheet.save(out.with_name(out.stem+f'-{pt}pt.png'))
    print(out.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
