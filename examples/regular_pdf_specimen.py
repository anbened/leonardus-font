"""A4 vector proofs from compiled glyphs, shaped at actual point sizes.

Uses pinned ReportLab plus the project's fontTools/HarfBuzz. No font embedding,
installation or claim of Office PDF export; outlines are painted as PDF paths.
"""
from pathlib import Path
import os
import unicodedata
import argparse

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('SOURCE_DATE_EPOCH', '0')
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4


class PDFPen(BasePen):
    def __init__(self,glyph_set,path):
        super().__init__(glyph_set)
        self.path=path
    def _moveTo(self,p):self.path.moveTo(*p)
    def _lineTo(self,p):self.path.lineTo(*p)
    def _curveToOne(self,a,b,c):self.path.curveTo(*a,*b,*c)
    def _closePath(self):self.path.close()


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--font', type=Path, default=ROOT/'fonts/Leonardus-Regular.ttf')
parser.add_argument('--out', type=Path, default=ROOT/'build/Leonardus-Specimen.pdf')
args=parser.parse_args()
ttf=args.font
font=TTFont(ttf)
glyphs=font.getGlyphSet();order=font.getGlyphOrder()
shaper=hb.Font(hb.Face(ttf.read_bytes()));shaper.scale=(1000,1000);hb.ot_font_set_funcs(shaper)


def positions(text):
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(shaper,buf)
    return list(zip(buf.glyph_infos,buf.glyph_positions))


def width(text,pt):return sum(p.x_advance for i,p in positions(text))*pt/1000


def wrap(text,pt):
    lines=[];line=''
    for word in text.split():
        if width(word,pt)>A4[0]-90:
            if line:lines.append(line);line=''
            for char in word:
                if line and width(line+char,pt)>A4[0]-90:
                    lines.append(line);line=''
                line+=char
            continue
        proposed=(line+' '+word).strip()
        if line and width(proposed,pt)>A4[0]-90:
            lines.append(line);line=word
        else:line=proposed
    if line:lines.append(line)
    return lines


output=args.out
if output.exists():
    raise FileExistsError('Choose a new specimen output path')
output.parent.mkdir(parents=True, exist_ok=True)
canvas=Canvas(str(output),pagesize=A4,invariant=1)
version=f'{font["head"].fontRevision:.3f}'
label=f'Leonardus Regular {version}'
canvas.setTitle(label+' specimen a dimensioni reali')
canvas.setAuthor('Leonardus Lab')
for pt in (12,18,36,72):
    canvas.setFillColorRGB(.1,.15,.2)
    canvas.setFont('Helvetica',15);canvas.drawString(45,797,f'{label}   {pt} pt reali')
    canvas.setFont('Helvetica',9);canvas.drawString(45,777,'Contorni del TTF compilato, shaping HarfBuzz, nessun font incorporato.')
    canvas.drawString(45,761,('Candidata contemporanea LTR per prova utente; font originale OFL 1.1.'
                            if version == '1.200' else
                            'Regular contemporaneo LTR. Disegno approvato; font originale OFL 1.1.'))
    texts=['La scienza è figlia dell’esperienza.',
           'È una prova italiana: città, perché, qualità, più, così, però.',
           'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz','0123456789  € 1.234,56',
           'à è é ì ò ù À È É Ì Ò Ù',unicodedata.normalize('NFD','à è é ì ò ù À È É Ì Ò Ù'),
           'b\u0300 b\u0301 i\u0301']
    if version == '1.200':
        texts[0]='jazz kiwi voci web xilofono yacht'
    if pt==72:
        texts=(['jazz kiwi','voci web','xilofono yacht','scienza stesso']
               if version == '1.200' else ['Leonardus','È una prova','È À ì é ù','scienza stesso'])
    y=710
    for text in texts:
        for line in wrap(text,pt):
            if y-pt*.25<80:raise ValueError('PDF page overflow')
            x=45
            for info,pos in positions(line):
                if info.codepoint==0:raise ValueError('Missing PDF glyph')
                bound=font['glyf'][order[info.codepoint]]
                if (hasattr(bound,'xMax') and
                    x+(pos.x_offset+bound.xMax)*pt/1000>A4[0]-35):
                    raise ValueError('PDF ink exceeds right margin')
                canvas.saveState();canvas.translate(x+pos.x_offset*pt/1000,y+pos.y_offset*pt/1000)
                canvas.scale(pt/1000,pt/1000)
                path=canvas.beginPath();pen=PDFPen(glyphs,path);glyphs[order[info.codepoint]].draw(pen)
                canvas.drawPath(path,fill=1,stroke=0,fillMode=1);canvas.restoreState()
                x+=pos.x_advance*pt/1000
            y-=pt*1.4
        y-=12
    canvas.setFont('Helvetica',9)
    footer=('26 minuscole ragionate; sei completamenti contemporanei. Nessuna autenticazione storica.'
            if version == '1.200' else
            'Sette forme pilota e tredici nuovi disegni approvati. Nessuna autenticazione storica.'
            if version == '1.100' else
            'Sette forme normalizzate da evidenze; altri disegni contemporanei. Nessuna autenticazione.')
    canvas.drawString(45,45,footer)
    canvas.showPage()
canvas.save()
print(output)
