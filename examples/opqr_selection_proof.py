"""Compare the selected mixed OPQR integration with the preserved 1.200 font."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from leonardus.lowercase import within
from leonardus.opqr import validate_integration

try:
    from regular_specimen import ProofRenderer, caption
except ModuleNotFoundError:
    from examples.regular_specimen import ProofRenderer, caption

ROOT = Path(__file__).resolve().parents[1]
WORDS = ['corpo', 'porre', 'proprio', 'percorso', 'ruota', 'quadro',
         'quattro', 'acqua', 'quercia', 'proporzione']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    document = validate_integration(ROOT)
    out = within(ROOT, args.out, 'build')
    if out.exists():
        raise ValueError('Preserve previous proofs; use a new output path')
    image = Image.new('RGB', (1400, 1710), '#faf8f2')
    draw = ImageDraw.Draw(image)
    draw.text((25, 20), 'Leonardus 1.210 | selezione o B, p A, q B, r B', font=caption(27), fill='#263b32')
    for x, path, label in [(25, ROOT/document['base_font'], '1.200 precedente'),
                           (725, ROOT/'fonts/Leonardus-1210-Regular.ttf', '1.210 - combinazione scelta')]:
        draw.text((x, 75), label, font=caption(24), fill='#263b32')
        ProofRenderer(path, 125).line(image, (x, 225), 'o p q r')
        renderer = ProofRenderer(path, 60)
        for n, word in enumerate(WORDS):
            renderer.line(image, (x, 350+115*n), word)
        ProofRenderer(path, 36).line(image, (x, 1535), 'o ò o\u0300   r p q   v y r')
    draw.line((700, 70, 700, 1580), fill='#bdc6b6')
    draw.text((25, 1630), 'Quattro disegni scelti; altre forme conservate. Nessuna nuova attestazione storica.',
              font=caption(23), fill='#263b32')
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(out.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
