"""Build separate OPQR comparison fonts and local proofs; never integrate proposals."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, ImageOps

from leonardus.fontbuild import _svg_to_glyph
from leonardus.lowercase import within
from leonardus.regular import accent_features

try:
    from regular_specimen import ProofRenderer
except ModuleNotFoundError:
    from examples.regular_specimen import ProofRenderer

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'data/opqr_variant_study_2026-10-15.json'
WORDS = ['corpo', 'porre', 'proprio', 'percorso', 'ruota', 'quadro',
         'quattro', 'acqua', 'quercia', 'proporzione']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(root=ROOT):
    root = Path(root).resolve()
    document = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (document['status'] != 'unapproved_design_variants_for_comparison'
            or document['scope'] != 'opqr_only'
            or document['human_visual_design_approval'] is not False
            or document['integration_approved'] is not False
            or document['authenticity_claim'] is not False
            or not document['instruction_quote'].strip()
            or set(document['variants']) != {'A', 'B'}):
        raise ValueError('Expected separate, unapproved OPQR studies')
    for key, directory in [('base_font', 'fonts'), ('evidence', 'data')]:
        path = within(root, document[key], directory)
        if sha(path) != document[key+'_sha256']:
            raise ValueError('Preserved font or historical evidence changed')
    with (root/document['evidence']).open(encoding='utf-8', newline='') as stream:
        evidence = {r['sample_id']: r for r in csv.DictReader(stream)}
    seen = set()
    for item in document['source_contexts']:
        sid = item['sample_id']
        row = evidence[sid]
        expected_crop = [int(row[k]) for k in ('crop_x', 'crop_y', 'crop_width', 'crop_height')]
        width, height = int(row['image_width']), int(row['image_height'])
        x, y, w, h = expected_crop
        cx, cy, cw, ch = item['mirror_context']
        if (sid in seen or row['review_status'] != 'reviewed'
                or row['target_character'] != item['character'] or item['character'] not in 'opqr'
                or row['folio'] != item['folio'] or row['source_image_id'] != item['source_image_id']
                or row['image_sha256'] != item['image_sha256']
                or item['raw_crop'] != expected_crop
                or item['mirror_crop'] != [width-x-w, y, w, h]
                or not 0 <= cx <= width-x-w or not 0 <= cy <= y
                or not width-x <= cx+cw <= width or not y+h <= cy+ch <= height):
            raise ValueError('Source identity or crop coordinates changed')
        seen.add(sid)
    if len(seen) != 22:
        raise ValueError('Expected all 22 reviewed OPQR source localizations')
    for variant, group in document['variants'].items():
        if (group['family'] != f'Leonardus OPQR {variant}'
                or group['postscript'] != f'Leonardus-OPQR-{variant}-Regular'
                or set(group['glyphs']) != set('opqr')):
            raise ValueError('Study must keep distinct family names and four bases')
        for char, record in group['glyphs'].items():
            path = within(root, record['file'], 'glyphs/proposals/2026-10-15-opqr')
            if (sha(path) != record['sha256']
                    or record['classification'] != 'unapproved_source_compared_design'
                    or not record['design_choice'].strip()
                    or not record['reference_sample_ids']
                    or any(s not in seen or evidence[s]['target_character'] != char
                           or s in document['excluded_primary_geometry']
                           for s in record['reference_sample_ids'])):
                raise ValueError('Proposal provenance or source checkpoint changed')
            svg = ET.parse(path).getroot()
            if (svg.get('viewBox') != '0 0 1000 1000'
                    or any(e.get('stroke') not in (None, 'none') for e in svg.iter())
                    or any(not e.get('d', '').rstrip().upper().endswith('Z')
                           for e in svg.iter('{http://www.w3.org/2000/svg}path'))):
                raise ValueError('Expected standard-cell closed filled contours')
            glyph = _svg_to_glyph(path)
            glyph.recalcBounds(None)
            if (glyph.numberOfContours < 1
                    or not 0 <= glyph.xMin < glyph.xMax < record['advance']
                    or not -200 <= glyph.yMin < glyph.yMax <= 800):
                raise ValueError('Proposal exceeds the agreed design cell')
    return document


def build_font(variant, output, root=ROOT):
    root, output = Path(root).resolve(), Path(output).resolve()
    document = validate(root)
    if variant not in document['variants']:
        raise ValueError('Choose A or B')
    if output.is_relative_to(root/'fonts') or output.is_relative_to(root/'glyphs'):
        raise ValueError('Study cannot overwrite distributed fonts or design sources')
    group = document['variants'][variant]
    if output.exists():
        with TTFont(output) as previous:
            if previous['name'].getDebugName(6) != group['postscript']:
                raise ValueError('Cannot overwrite another family')
    with TTFont(root/document['base_font'], recalcTimestamp=False) as font:
        font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
        cmap = font.getBestCmap()
        for char, record in group['glyphs'].items():
            name = cmap[ord(char)]
            if font['hmtx'][name][0] != record['advance']:
                raise ValueError('Comparison must preserve the base advances')
            glyph = _svg_to_glyph(root/record['file'])
            glyph.recalcBounds(None)
            font['glyf'][name] = glyph
            font['hmtx'][name] = (record['advance'], glyph.xMin)
        records = {}
        reverse = {name: cp for cp, name in cmap.items()}
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
        font['head'].fontRevision = 1.201
        names = {
            1: group['family'], 3: f'Leonardus:OPQR:20261015:{variant}',
            4: group['family']+' Regular', 5: 'Version 1.201; unapproved OPQR study',
            6: group['postscript'],
            10: 'Contemporary LTR study; four proposed forms compared with historical references. Not human-approved or authenticated handwriting.',
        }
        for name_id, value in names.items():
            font['name'].setName(value, name_id, 3, 1, 0x409)
            font['name'].setName(value, name_id, 1, 0, 0)
        output.parent.mkdir(parents=True, exist_ok=True)
        font.save(output)
    return {'variant': variant, 'font_sha256': sha(output),
            'family': group['family'], 'status': document['status']}


def words_proof(out, base):
    image = Image.new('RGB', (1500, 1750), '#faf8f2')
    draw = ImageDraw.Draw(image)
    caption = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 24) if Path(
        'C:/Windows/Fonts/segoeui.ttf').exists() else ImageFont.truetype('DejaVuSans.ttf', 24)
    draw.text((30, 18), 'OPQR | font compilati a confronto dentro parole reali', font=caption, fill='#263b32')
    for i, (path, label) in enumerate(zip(
            [base, out/'Leonardus-OPQR-A.ttf', out/'Leonardus-OPQR-B.ttf'],
            ['1.200 attuale', 'A - equilibrio di lettura', 'B - varianti esplorative'])):
        x = 25+i*500
        draw.text((x, 65), label, font=caption, fill='#263b32')
        ProofRenderer(path, 125).line(image, (x, 225), 'o p q r')
        renderer = ProofRenderer(path, 60)
        for n, word in enumerate(WORDS):
            renderer.line(image, (x, 350+n*125), word)
        ProofRenderer(path, 26).line(image, (x, 1600), 'o p q r   |   ò o\u0300')
        if i:
            draw.line((x-12, 65, x-12, 1620), fill='#bdc6b6', width=1)
    draw.text((30, 1670), 'A/B: proposte da valutare. Nessuna integrazione o autenticazione storica.', font=caption, fill='#263b32')
    image.save(out/'words-comparison.png')
    proofs = {}
    for pt in (12, 18, 36, 72):
        page = Image.new('RGB', (1800, 1100), '#faf8f2')
        draw = ImageDraw.Draw(page)
        draw.text((25, 20), f'OPQR | {pt} pt a 96 DPI | contorni compilati, HarfBuzz + FreeType',
                  font=caption, fill='#263b32')
        records = []
        ppem = round(pt*96/72)
        for i, path in enumerate([base, out/'Leonardus-OPQR-A.ttf', out/'Leonardus-OPQR-B.ttf']):
            x = 25+i*600
            draw.text((x, 70), ['1.200', 'A', 'B'][i], font=caption, fill='#263b32')
            renderer = ProofRenderer(path, ppem)
            for n, word in enumerate(['corpo', 'porre', 'proprio', 'quattro', 'acqua', 'quercia']):
                records.append(renderer.line(page, (x, 180+n*max(70, round(ppem*1.6))), word))
        page.save(out/f'proof-{pt}pt.png')
        proofs[str(pt)] = {'ppem': ppem, 'lines': records}
    (out/'proof-verification.json').write_text(json.dumps(proofs, indent=2)+'\n',
                                             encoding='utf-8', newline='\n')


def source_sheets(document, out, originals):
    index = {sha(p): p for p in Path(originals).glob('*.jpg')}
    label = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20) if Path(
        'C:/Windows/Fonts/segoeui.ttf').exists() else ImageFont.truetype('DejaVuSans.ttf', 20)
    for char in 'opqr':
        rows = [r for r in document['source_contexts'] if r['character'] == char]
        sheet = Image.new('RGB', (1200, 100+len(rows)*240), '#faf8f0')
        draw = ImageDraw.Draw(sheet)
        draw.text((20, 14), f'{char} | BNE Madrid I, MSS/8937 | campioni e contesti specchiati LTR', font=label, fill='black')
        draw.text((20, 46), 'Localizzazione rossa, non contorno. Studio locale; letture e riserve conservate.', font=label, fill='#444444')
        for n, item in enumerate(rows):
            path = index[item['image_sha256']]
            with Image.open(path) as source:
                if source.size != (1578, 2174):
                    raise ValueError('Original dimensions differ')
                mirrored = ImageOps.mirror(source.convert('RGB'))
            top = 90+240*n
            draw.text((20, top), f"{item['sample_id']} | folio {item['folio']}", font=label, fill='black')
            x, y, w, h = item['mirror_crop']
            cx, cy, cw, ch = item['mirror_context']
            for crop, at, maxw in [(mirrored.crop((x, y, x+w, y+h)), (30, top+35), 170),
                                   (mirrored.crop((cx, cy, cx+cw, cy+ch)), (230, top+35), 940)]:
                if at[0] == 230:
                    ImageDraw.Draw(crop).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1), outline='#bd2929')
                scale = min(maxw/crop.width, 190/crop.height)
                sheet.paste(crop.resize((round(crop.width*scale), round(crop.height*scale)),
                                       Image.Resampling.NEAREST), at)
        sheet.save(out/f'historical-{char}.png')
    return len(document['source_contexts'])


def comparison_page(document, out, images):
    words = ''.join(f'<div class="wordname">{word}</div><div class="triplet">'+''.join(
        f'<div class="sample {family}">{word}</div>' for family in ('base', 'a', 'b'))+'</div>' for word in WORDS)
    research = ''
    for char, note in document['observations'].items():
        refs = ', '.join(note['primary'])
        research += f'<section><h3>{char}</h3><p>{html.escape(note["observed"])}</p><p><b>A:</b> {html.escape(note["A"])}</p><p><b>B:</b> {html.escape(note["B"])}</p><p>{html.escape(note["limits"])}</p><small>{html.escape(refs)}</small>'
        if images:
            research += f'<details><summary>Mostra campioni e contesto di {char}</summary><img src="historical-{char}.png" alt="Campioni BNE Madrid I della {char}, specchiati e ingranditi; coordinate e folii nel registro"/></details>'
        research += '</section>'
    page = '''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Leonardus - studio o p q r</title><style>
@font-face{font-family:StudyBase;src:url('Leonardus-1200-Regular.ttf')}@font-face{font-family:StudyA;src:url('Leonardus-OPQR-A.ttf')}@font-face{font-family:StudyB;src:url('Leonardus-OPQR-B.ttf')}
*{box-sizing:border-box}body{margin:0;background:#f7f4ec;color:#263b32;font:16px/1.5 system-ui,sans-serif}main{max-width:1450px;padding:24px;margin:auto}h1{font-size:32px;margin-bottom:8px}p{max-width:1000px}h2{margin-top:36px}.tag{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#637363}
.triplet{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.sample{font-size:var(--size,36pt);line-height:1.55;overflow-wrap:anywhere;padding:5px 8px}.base{font-family:StudyBase}.a{font-family:StudyA}.b{font-family:StudyB}.columns{position:sticky;top:0;background:#f7f4ec;z-index:2;border-bottom:1px solid #aebaa9;padding:12px 0}.columns b{padding:0 8px}.wordname{font-size:12px;color:#657463;border-top:1px solid #d7dccf;padding-top:8px}.controls{display:flex;gap:18px;align-items:center;flex-wrap:wrap;margin:22px 0}button,textarea{font:inherit;border:1px solid #afbaaa;background:#fffdf6;color:inherit;border-radius:6px;padding:9px}textarea{width:100%;min-height:85px}section{background:#fffdf6;border:1px solid #d5ddcf;padding:20px;margin:14px 0}section h3{margin:0;font-size:26px}small{display:block;overflow-wrap:anywhere;color:#647362}details{margin-top:15px}summary{cursor:pointer}img{width:100%;height:auto;margin-top:12px}a{color:#365e43}.note{color:#596b5d;font-size:14px}.status{font-size:14px}
@media(max-width:650px){main{padding:14px}.triplet{gap:4px}.sample{padding:4px;font-size:min(var(--size,36pt),30pt)}.columns{font-size:13px}}@media print{.controls,textarea,details{display:none}.columns{position:static}.sample{font-size:25pt}}
</style><main><div class="tag">Leonardus | studio separato, non approvato</div><h1>o, p, q, r: dal campione alla parola</h1>
<p>La 1.200 a sinistra, due proposte al centro e a destra. Le parole servono a valutare la lettura moderna: non sono trascrizioni certificate dei manoscritti. La serie A cerca equilibrio; la B esplora gesti e varianti più marcati. Ogni scelta può essere valutata per singola lettera.</p>
<div class="controls"><label>Corpo <input id="size" type="range" min="12" max="60" value="36"><output id="sizeLabel">36 pt</output></label><button id="reset">Ripristina il testo di prova</button><a href="words-comparison.png">Tavola delle parole</a></div><p class="status" id="status" role="status">Caricamento dei tre font…</p>
<div class="columns triplet"><b>1.200 attuale</b><b>A · equilibrio di lettura</b><b>B · esplorativa</b></div>
<div class="triplet"><div class="sample base">o p q r</div><div class="sample a">o p q r</div><div class="sample b">o p q r</div></div>
WORDS
<h2>Prova una frase tua</h2><textarea id="text" aria-label="Testo da confrontare" spellcheck="false">Il corpo ruota; l'acqua scorre. Proporre quattro percorsi.</textarea><p id="unsupported" role="status" class="note"></p><div class="triplet"><div id="t0" class="sample base"></div><div id="t1" class="sample a"></div><div id="t2" class="sample b"></div></div>
<h2>Che cosa sostengono i campioni</h2><p class="note">22 localizzazioni, BNE Madrid I, folii 1r–4r; 1578 × 2174 pixel. I contesti sono specchiati orizzontalmente e ingranditi senza ricostruzione o contrasto. Le immagini restano locali e non sono incluse in Git. Le zone dubbie conservano i limiti delle revisioni precedenti.</p>
RESEARCH
<p class="note">Contorni originali Leonardus, OFL 1.1. Studio contemporaneo LTR: nessuna nuova approvazione umana, integrazione nel font installato o attestazione di autenticità. Immagini di studio: Biblioteca Nacional de España, MSS/8937; attribuzione e modifiche dichiarate nel registro del progetto. La pagina non invia il testo digitato.</p></main>
<script>
const box=document.querySelector('#text'),range=document.querySelector('#size');const initial=box.value;
const known=new Set(KNOWN);
function update(){document.documentElement.style.setProperty('--size',range.value+'pt');document.querySelector('#sizeLabel').textContent=range.value+' pt';for(const id of ['t0','t1','t2'])document.getElementById(id).textContent=box.value;const missing=[...new Set([...box.value].filter(c=>!known.has(c.codePointAt(0))&&!['\\n','\\r','\\t'].includes(c)))];document.querySelector('#unsupported').textContent=missing.length?'Caratteri fuori repertorio: '+missing.join(' '):'';}
range.addEventListener('input',update);box.addEventListener('input',update);document.querySelector('#reset').onclick=()=>{box.value=initial;update();};
Promise.all(['StudyBase','StudyA','StudyB'].map(name=>document.fonts.load('36px '+name))).then(fonts=>{if(fonts.some(f=>!f.length))throw Error();document.querySelector('#status').textContent='Tre font caricati. La famiglia installata Leonardus 1200 resta invariata.';}).catch(()=>document.querySelector('#status').textContent='Font non caricati: usare il server locale dalla cartella completa dello studio.');update();
</script></html>'''
    with TTFont(out/'Leonardus-1200-Regular.ttf') as font:
        known = sorted(font.getBestCmap())
    (out/'index.html').write_text(page.replace('WORDS', words).replace('RESEARCH', research).replace(
        'KNOWN', json.dumps(known)), encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--originals', type=Path)
    args = parser.parse_args()
    out = within(ROOT, args.out, 'build')
    if out.exists():
        raise ValueError('Use a new study directory; existing comparisons are preserved')
    document = validate()
    out.mkdir(parents=True)
    (out/'Leonardus-1200-Regular.ttf').write_bytes((ROOT/document['base_font']).read_bytes())
    results = [build_font(v, out/f'Leonardus-OPQR-{v}.ttf') for v in 'AB']
    count = source_sheets(document, out, args.originals) if args.originals else 0
    words_proof(out, ROOT/document['base_font'])
    comparison_page(document, out, bool(count))
    result = {'status': document['status'], 'originals_verified': count, 'fonts': results}
    (out/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
