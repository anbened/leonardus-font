"""Render compiled Regular outlines through HarfBuzz + FreeType, without fallback."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import unicodedata
from pathlib import Path

import freetype
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from leonardus.cli import audit_font
from leonardus.preview import require_coverage

ROOT = Path(__file__).resolve().parents[1]
TEXT = [
    "La scienza è figlia dell'esperienza.",
    "Leonardus: disegno contemporaneo da sinistra a destra.",
    "È una prova: città, perché, qualità, più, così, però.",
    "À È É Ì Ò Ù — à è é ì ò ù — € 1.234,56; 12 ottobre 2026.",
]
BODY = ("Osservare, annotare e confrontare rende il lavoro verificabile. "
        "Le lettere conservano un ritmo comune; le forme mancanti sono completamenti "
        "contemporanei dichiarati. Questo testo prova maiuscole, minuscole, accenti e numeri: "
        "la città è più chiara, perché ogni dettaglio può essere riletto. ")


def caption(size):
    for path in ('C:/Windows/Fonts/segoeui.ttf','DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(path,size)
        except OSError:
            pass
    raise ValueError('A readable caption font is required')


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    buf.language = 'it'
    hb.shape(font,buf)
    if any(i.codepoint == 0 for i in buf.glyph_infos):
        raise ValueError('Shaping produced .notdef')
    return [(i.codepoint,i.cluster,p.x_advance,p.y_advance,p.x_offset,p.y_offset)
            for i,p in zip(buf.glyph_infos,buf.glyph_positions)]


class ProofRenderer:
    def __init__(self, path, ppem):
        self.path,self.ppem = Path(path),ppem
        self.font = hb.Font(hb.Face(self.path.read_bytes()))
        self.font.scale = (1000,1000)
        hb.ot_font_set_funcs(self.font)
        self.face = freetype.Face(str(self.path))
        self.face.set_pixel_sizes(0,ppem)

    def width(self,text):
        return sum(p[2] for p in shape(self.font,text))*self.ppem/1000

    def line(self,image,position,text):
        require_coverage(self.path,text)
        left,baseline = position
        cursor = 0
        boxes = []
        shaped = shape(self.font,text)
        for gid,cluster,advance,yadvance,xoffset,yoffset in shaped:
            self.face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = self.face.glyph
            bitmap = slot.bitmap
            if bitmap.width and bitmap.rows:
                pixels = bytes(bitmap.buffer)
                mask = Image.frombytes('L',(bitmap.width,bitmap.rows),pixels,'raw','L',abs(bitmap.pitch))
                x = round(left+(cursor+xoffset)*self.ppem/1000)+slot.bitmap_left
                y = round(baseline-yoffset*self.ppem/1000)-slot.bitmap_top
                box = [x,y,x+bitmap.width,y+bitmap.rows]
                if x<0 or y<0 or box[2]>image.width or box[3]>image.height:
                    raise ValueError(f'Proof ink exceeds canvas: {text} {box}')
                image.paste('#252b2d',(x,y),mask)
                boxes.append(box)
            cursor += advance
        box=([min(b[0] for b in boxes),min(b[1] for b in boxes),
              max(b[2] for b in boxes),max(b[3] for b in boxes)] if boxes else None)
        return {'text':text,'width_px':cursor*self.ppem/1000,'shaped_glyph_count':len(shaped),'ink_box':box}

    def wrap(self,text,width):
        lines=[]
        current=''
        for word in text.split():
            candidate=(current+' '+word).strip()
            if current and self.width(candidate)>width:
                lines.append(current)
                current=word
            else:
                current=candidate
        if current:
            lines.append(current)
        if any(self.width(line)>width for line in lines):
            raise ValueError('Unbreakable word exceeds proof column')
        return lines


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font',type=Path,default=ROOT/'dist/regular/Leonardus-Alpha0200-Regular.ttf')
    parser.add_argument('--out',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--release',action='store_true',help='Use approved Regular captions; Office QA remains separate')
    mode.add_argument('--candidate',action='store_true',help='Use versioned candidate captions with the actual approval scope')
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    receipt={'font_sha256':hashlib.sha256(args.font.read_bytes()).hexdigest(),
             'status':('delegated_candidate_for_user_trial' if args.candidate else
                       'approved_release_forms' if args.release else 'regular_alpha_pending_full_visual_Office_QA'),'dpi':96,
             'renderer':'HarfBuzz shaping + FreeType unhinted grayscale; compiled TTF; no fallback',
             'versions':{'python':platform.python_version(),'harfbuzz':hb.__version__,
                         'freetype':list(freetype.version())},'pages':{}}
    for pt in (12,18,36,72):
        ppem=round(pt*96/72)
        renderer=ProofRenderer(args.font,ppem)
        height=max(1800,ppem*36+400)
        sheet=Image.new('RGB',(1800,height),'#fbf8f1')
        draw=ImageDraw.Draw(sheet)
        with TTFont(args.font) as font:
            version = f'{font["head"].fontRevision:.3f}'
        if version in {'1.210','1.211'}:
            receipt['status']='selected_opqr_integration_candidate'
            receipt['approved_design_selection']={'o':'B','p':'A','q':'B','r':'B'}
            if version == '1.211':
                receipt['status']='pq_spacing_correction_candidate'
        if version == '1.220':
            receipt['status']='selected_aemnu_integration_candidate'
            receipt['approved_design_selection']={'a':'A','e':'A','m':'B','n':'B','u':'B'}
            receipt['retained_opqr_selection']={'o':'B','p':'A','q':'B','r':'B'}
        if version == '1.230':
            receipt['status']='selected_jkvwxy_completion_candidate'
            receipt['approved_design_selection']={'j':'A','k':'B','v':'B','w':'B','x':'B','y':'B'}
        if version == '1.240':
            receipt['status']='selected_capitals_integration_candidate'
            receipt['approved_design_selection']={'L':'B','A':'B','M':'B','N':'A','R':'B','S':'B'}
        if version == '1.250':
            receipt['status']='selected_cdegpt_integration_candidate'
            receipt['approved_design_selection']={'C':'B','D':'B','E':'A','G':'B','P':'B','T':'B'}
        if version == '1.260':
            receipt['status']='selected_bfhioq_integration_candidate'
            receipt['approved_design_selection']={'B': 'B', 'F': 'B', 'H': 'B', 'I': 'A', 'O': 'B', 'Q': 'B'}
        if version == '1.270':
            receipt['status']='selected_jkuvwxyz_integration_candidate'
            receipt['approved_design_selection']={'J': 'B', 'K': 'B', 'U': 'B', 'V': 'B', 'W': 'B', 'X': 'B', 'Y': 'B', 'Z': 'B'}
        if version in {'1.200', '1.210', '1.211', '1.220', '1.230', '1.240', '1.250', '1.260', '1.270'} and not args.candidate:
            raise ValueError('Use --candidate for a versioned trial candidate')
        label=f'LEONARDUS REGULAR {version}' if args.release or args.candidate else 'LEONARDUS ALPHA 0.200'
        draw.text((45,20),f'{label} | {pt} pt a 96 DPI ({ppem} px/em)',font=caption(27),fill='#172638')
        subtitle=('Candidata LTR 1.270: J/K/U/V/W/X/Y/Z B; ciclo delle 26 maiuscole completato. Prova Office pendente.'
                  if args.candidate and version == '1.270' else
                  'Candidata LTR 1.260: B/F/H/O/Q B, I A; forme precedenti conservate. Prova Office pendente.'
                  if args.candidate and version == '1.260' else
                  'Candidata LTR 1.250: C/D/G/P/T B, E A; forme precedenti conservate. Prova Office pendente.'
                  if args.candidate and version == '1.250' else
                  'Candidata LTR 1.240: L/A/M/R/S B, N A; minuscole conservate. Prova Office pendente.'
                  if args.candidate and version == '1.240' else
                  'Candidata LTR 1.230: j A, k/v/w/x/y B; sei completamenti moderni scelti. Prova Office pendente.'
                  if args.candidate and version == '1.230' else
                  'Candidata LTR 1.220: a/e A, m/n/u B; OPQR e spaziatura p/q conservati. Prova Office pendente.'
                  if args.candidate and version == '1.220' else
                  'Candidata LTR 1.211: spaziatura p/q riequilibrata; forme scelte B/A/B/B conservate. Prova Office pendente.'
                  if args.candidate and version == '1.211' else
                  'Candidata LTR 1.210: disegni OPQR scelti B/A/B/B; altre forme conservate. Prova Office 1.210 pendente.'
                  if args.candidate and version == '1.210' else
                  'Candidata LTR: 26 minuscole ragionate; sei completamenti contemporanei. Prova utente e Office 1.200 pendenti.'
                  if args.candidate else
                  'Regular contemporaneo LTR. Sette forme V3 e tredici nuovi disegni approvati.'
                  if args.release and version == '1.100' else
                  'Regular contemporaneo LTR. Sette forme V3 normalizzate; completamenti progettati.')
        if not args.release and not args.candidate:
            subtitle+=' Prova Office pendente.'
        draw.text((45,64),subtitle,font=caption(19),fill='#172638')
        baseline=max(140,105+ppem) if args.release or args.candidate else 140
        lines=[]
        leading=max(30,round(ppem*1.35))
        for text in TEXT[:4]:
            for line in renderer.wrap(text,1700):
                lines.append(renderer.line(sheet,(45,baseline),line))
                baseline+=leading
        baseline+=25
        for text in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz',
                     '0123456789  ( [ { + - = % & @ # / \\ } ] )',
                     '“Virgolette” ‘singole’ — trattino – puntini…',
                     'À È É Ì Ò Ù  à è é ì ò ù'):
            for line in renderer.wrap(text,1700):
                lines.append(renderer.line(sheet,(45,baseline),line));baseline+=leading
        baseline+=25
        draw.text((45,baseline),'NFC / NFD: precomposti e scomposti; b + grave/acuto verifica mark senza composito',font=caption(19),fill='#172638')
        baseline+=leading+15
        for text in ('à è é ì ò ù À È É Ì Ò Ù',unicodedata.normalize('NFD','à è é ì ò ù À È É Ì Ò Ù'),
                     'b\u0300 b\u0301 i\u0301'):
            for line in renderer.wrap(text,1700):
                lines.append(renderer.line(sheet,(45,baseline),line));baseline+=leading
        baseline+=20
        for line in renderer.wrap(BODY,1700)[:max(1,(height-120-baseline)//leading)]:
            lines.append(renderer.line(sheet,(45,baseline),line));baseline+=leading
        footer=('Candidata da provare; font originale OFL 1.1. Nessuna autenticazione storica.' if args.candidate else
                'Disegno approvato; font originale OFL 1.1. Nessuna autenticazione storica.' if args.release else
                'Alpha per prova privata; licenza finale e accettazione del disegno completo ancora aperte. Nessuna autenticazione.')
        draw.text((45,height-50),footer,font=caption(18),fill='#172638')
        filename=f'specimen-{pt}pt.png'
        sheet.save(args.out/filename)
        receipt['pages'][filename]={'pt':pt,'ppem':ppem,'lines':lines,
                                    'sha256':hashlib.sha256((args.out/filename).read_bytes()).hexdigest()}
    # Exact character atlas includes every noncombining mapped codepoint.
    with TTFont(args.font) as font:
        cmap=font.getBestCmap()
    atlas=Image.new('RGB',(1800,1750),'white')
    draw=ImageDraw.Draw(atlas)
    draw.text((30,15),'COPERTURA COMPILATA | 119 codepoint; gli spazi sono vuoti, i combinanti hanno advance zero',font=caption(24),fill='#172638')
    renderer=ProofRenderer(args.font,75)
    for i,cp in enumerate(sorted(cmap)):
        x=30+(i%12)*145;y=65+(i//12)*155
        draw.rectangle((x,y,x+135,y+145),outline='#d2d8df')
        text=chr(cp) if cp not in (0x300,0x301) else 'b'+chr(cp)
        renderer.line(atlas,(x+12,y+100),text)
        draw.text((x+7,y+115),f'U+{cp:04X}',font=caption(15),fill='#172638')
    atlas.save(args.out/'charset-atlas.png')
    receipt['atlas_sha256']=hashlib.sha256((args.out/'charset-atlas.png').read_bytes()).hexdigest()
    receipt['audit']=audit_font(args.font)
    (args.out/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'out':str(args.out),'font_sha256':receipt['font_sha256'],'sizes':[12,18,36,72]}))


if __name__=='__main__':
    main()
