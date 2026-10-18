"""Build unapproved A/E/M/N/U studies and comparisons; preserve installed releases."""
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
from PIL import Image, ImageDraw, ImageOps

from leonardus.fontbuild import _svg_to_glyph
from leonardus.lowercase import within
from leonardus.regular import accent_features

try:
    from regular_specimen import ProofRenderer, caption
except ModuleNotFoundError:
    from examples.regular_specimen import ProofRenderer, caption

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'data/aemnu_variant_study_2026-10-15.json'
LETTERS = 'aemnu'
WORDS = {'a': ['casa carta', 'acqua parola'], 'e': ['vedere tenere', 'essere leggere'],
         'm': ['mano amore', 'mamma comune'], 'n': ['anno nome', 'non andare'],
         'u': ['luna futuro', 'tutto lungo']}
DEPENDENCIES = {'a': 'à', 'e': 'èé', 'u': 'ù'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(root=ROOT):
    root = Path(root).resolve()
    doc = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (doc['schema_version'] != 1 or doc['scope'] != 'aemnu_only'
            or doc['status'] != 'unapproved_design_variants_for_comparison'
            or any(doc[k] is not False for k in ('human_visual_design_approval',
                       'integration_approved', 'authenticity_claim'))
            or doc['detail_search']['new_higher_detail_source_acquired'] is not False
            or doc['detail_search']['arundel_lead']['used_for_glyph_design'] is not False
            or not doc['instruction_quote'].strip() or set(doc['variants']) != set('AB')):
        raise ValueError('Expected separate unapproved AEMNU variants')
    for key, directory in [('base_font', 'fonts'), ('evidence', 'data')]:
        if sha(within(root, doc[key], directory)) != doc[key+'_sha256']:
            raise ValueError('Preserved font or evidence changed')
    with (root/doc['evidence']).open(encoding='utf-8', newline='') as stream:
        evidence = {r['sample_id']: r for r in csv.DictReader(stream)}
    seen = set()
    for item in doc['source_contexts']:
        sid = item['sample_id']; row = evidence[sid]
        crop = [int(row[k]) for k in ('crop_x', 'crop_y', 'crop_width', 'crop_height')]
        width, height = int(row['image_width']), int(row['image_height'])
        x, y, w, h = crop; cx, cy, cw, ch = item['mirror_context']
        if (sid in seen or row['review_status'] != 'reviewed'
                or row['target_character'] != item['character'] or item['character'] not in LETTERS
                or row['folio'] != item['folio'] or row['source_image_id'] != item['source_image_id']
                or row['image_sha256'] != item['image_sha256'] or crop != item['raw_crop']
                or item['mirror_crop'] != [width-x-w, y, w, h]
                or not 0 <= cx <= width-x-w or not 0 <= cy <= y
                or not width-x <= cx+cw <= width or not y+h <= cy+ch <= height):
            raise ValueError('Source localization differs from the evidence registry')
        seen.add(sid)
    if len(seen) != 27:
        raise ValueError('Expected all 27 existing reviewed localizations')
    with TTFont(root/doc['base_font']) as base:
        for variant, group in doc['variants'].items():
            if (group['family'] != f'Leonardus AEMNU {variant}'
                    or group['postscript'] != f'Leonardus-AEMNU-{variant}-Regular'
                    or set(group['glyphs']) != set(LETTERS)):
                raise ValueError('Study must keep distinct names and five bases')
            for char, record in group['glyphs'].items():
                path = within(root, record['file'], 'glyphs/proposals/2026-10-15-aemnu')
                if (sha(path) != record['sha256']
                        or record['classification'] != 'unapproved_source_compared_design'
                        or not record['design_choice'].strip() or not record['reference_sample_ids']
                        or any(s not in seen or evidence[s]['target_character'] != char
                               or s in doc['excluded_primary_geometry'] for s in record['reference_sample_ids'])
                        or record['advance'] != base['hmtx'][base.getBestCmap()[ord(char)]][0]):
                    raise ValueError('Proposal provenance, scope or advance changed')
                svg = ET.parse(path).getroot()
                if (svg.get('viewBox') != '0 0 1000 1000'
                        or any(e.get('stroke') not in (None, 'none') for e in svg.iter())
                        or any(not e.get('d', '').rstrip().upper().endswith('Z')
                               for e in svg.iter('{http://www.w3.org/2000/svg}path'))):
                    raise ValueError('Expected closed filled standard-cell SVG')
                glyph = _svg_to_glyph(path); glyph.recalcBounds(None)
                if (glyph.numberOfContours < 1 or not 0 <= glyph.xMin < glyph.xMax < record['advance']
                        or not -50 <= glyph.yMin < glyph.yMax <= 550):
                    raise ValueError('Proposal exceeds the lowercase design cell')
    return doc


def build_font(variant, output, root=ROOT, character=None):
    root = Path(root).resolve(); doc = validate(root)
    if variant not in 'AB' or len(variant) != 1 or (character is not None and character not in LETTERS):
        raise ValueError('Choose A or B and optionally one study letter')
    output = within(root, output, 'build')
    group = doc['variants'][variant]
    selected = character or LETTERS
    family = group['family'] + (f' {character}' if character else '')
    postscript = group['postscript'].replace('-Regular', f'-{character}-Regular') if character else group['postscript']
    if output.exists():
        with TTFont(output) as previous:
            if previous['name'].getDebugName(6) != postscript:
                raise ValueError('Cannot overwrite another family')
    with TTFont(root/doc['base_font'], recalcTimestamp=False) as font:
        font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
        cmap = font.getBestCmap()
        for char in selected:
            record = group['glyphs'][char]; name = cmap[ord(char)]
            glyph = _svg_to_glyph(root/record['file']); glyph.recalcBounds(None)
            font['glyf'][name] = glyph
            font['hmtx'][name] = (record['advance'], glyph.xMin)
            for accent in DEPENDENCIES.get(char, ''):
                composite = font['glyf'][cmap[ord(accent)]]
                if len(composite.components) != 2 or composite.components[0].glyphName != name:
                    raise ValueError('Unexpected base/accent dependency')
                composite.components[1].x = round((glyph.xMin+glyph.xMax)/2+35)
                composite.components[1].y = glyph.yMax+60
                composite.recalcBounds(font['glyf'])
                font['hmtx'][cmap[ord(accent)]] = (record['advance'], composite.xMin)
        reverse = {n: cp for cp, n in cmap.items()}; records = {}
        for name in font.getGlyphOrder():
            glyph = font['glyf'][name]; glyph.recalcBounds(font['glyf'])
            records[name] = {'codepoint': reverse.get(name), 'bounds': [
                getattr(glyph, k, 0) for k in ('xMin', 'yMin', 'xMax', 'yMax')]}
        for tag in ('GPOS', 'GSUB', 'GDEF'):
            if tag in font: del font[tag]
        addOpenTypeFeaturesFromString(font, accent_features(records))
        font['OS/2'].recalcAvgCharWidth(font); font['head'].fontRevision = 1.212
        names = {1: family, 3: 'Leonardus:AEMNU:20261015:'+variant+selected,
                 4: family+' Regular', 5: 'Version 1.212; unapproved AEMNU study', 6: postscript,
                 10: 'Contemporary independent AEMNU proposals compared with 27 existing BNE localizations. No new higher-detail target samples acquired. Not approved for integration; no new historical reading or authenticity claim.'}
        for number, value in names.items():
            font['name'].setName(value, number, 3, 1, 0x409)
            font['name'].setName(value, number, 1, 0, 0)
        output.parent.mkdir(parents=True, exist_ok=True); font.save(output)
    return {'variant': variant, 'letters': selected, 'sha256': sha(output), 'family': family}


def source_sheets(doc, out, originals):
    originals = Path(originals)
    for char in LETTERS:
        rows = [r for r in doc['source_contexts'] if r['character'] == char]
        sheet = Image.new('RGB', (1200, 100+len(rows)*235), '#faf8f0'); draw = ImageDraw.Draw(sheet)
        draw.text((20, 15), f'{char} | BNE MSS/8937 | campioni e contesti specchiati', font=caption(22), fill='#263b32')
        draw.text((20, 49), 'Ingrandimento dei pixel esistenti; riquadro rosso = localizzazione, non contorno.', font=caption(20), fill='#596b5d')
        for i, item in enumerate(rows):
            path = originals/(item['image_sha256']+'.jpg')
            if sha(path) != item['image_sha256']: raise ValueError('Original image differs')
            with Image.open(path) as source:
                mirrored = ImageOps.mirror(source.convert('RGB'))
            x, y, w, h = item['mirror_crop']; cx, cy, cw, ch = item['mirror_context']; top = 95+i*235
            draw.text((20, top), item['sample_id']+' | folio '+item['folio'], font=caption(20), fill='#263b32')
            context = mirrored.crop((cx, cy, cx+cw, cy+ch))
            ImageDraw.Draw(context).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1), outline='#bd2929')
            for crop, at, maxw in [(mirrored.crop((x, y, x+w, y+h)), (20, top+35), 160), (context, (220, top+35), 950)]:
                scale = min(maxw/crop.width, 180/crop.height)
                sheet.paste(crop.resize((round(crop.width*scale), round(crop.height*scale)), Image.Resampling.NEAREST), at)
        sheet.save(out/f'historical-{char}.png')
    return len(doc['source_contexts'])


def words_proof(out, base):
    image = Image.new('RGB', (1650, 1670), '#faf8f2'); draw = ImageDraw.Draw(image)
    draw.text((25, 20), 'A E M N U | confronto nella parola: cambia una sola lettera per riga', font=caption(27), fill='#263b32')
    for i, label in enumerate(['1.211 attuale', 'A - equilibrio di lettura', 'B - esplorativa']):
        draw.text((25+i*550, 80), label, font=caption(26), fill='#263b32')
    for n, char in enumerate(LETTERS):
        top = 145+n*285
        for i, path in enumerate([base, out/f'{char}-A.ttf', out/f'{char}-B.ttf']):
            x = 25+i*550
            ProofRenderer(path, 125).line(image, (x, top+80), char+' '+char+char)
            renderer = ProofRenderer(path, 59)
            for j, word in enumerate(WORDS[char]): renderer.line(image, (x, top+160+j*75), word)
        draw.line((25, top+255, 1620, top+255), fill='#ccd1c4')
    draw.text((25, 1605), 'Studi non approvati; stessi advance. Le tavole storiche restano locali.', font=caption(24), fill='#596b5d')
    image.save(out/'words-comparison.png')
    for pt in (12, 18, 36, 72):
        page = Image.new('RGB', (2100, 1300), '#faf8f2'); draw = ImageDraw.Draw(page)
        draw.text((25, 20), f'AEMNU | {pt} pt a 96 DPI | HarfBuzz + FreeType', font=caption(25), fill='#263b32')
        for n, char in enumerate(LETTERS):
            for i, path in enumerate([base, out/f'{char}-A.ttf', out/f'{char}-B.ttf']):
                if n == 0: draw.text((25+i*700, 75), ['1.211', 'A', 'B'][i], font=caption(23), fill='#263b32')
                ProofRenderer(path, round(pt*96/72)).line(page, (25+i*700, 190+n*210), WORDS[char][1])
        page.save(out/f'proof-{pt}pt.png')


def comparison_page(doc, out, images):
    def face(family, filename):
        return f"@font-face{{font-family:{family};src:url('{filename}?v={sha(out/filename)}')}}"

    faces = face('Current', 'Leonardus-1211-Regular.ttf')
    for variant in 'AB':
        faces += face('All'+variant, f'Leonardus-AEMNU-{variant}.ttf')
        for char in LETTERS: faces += face(char+variant, f'{char}-{variant}.ttf')
    sections = ''
    for char in LETTERS:
        note = doc['observations'][char]
        cells = ''.join(f'<div class="sample" style="font-family:{family}">{char} {char}{char}<br>{"<br>".join(WORDS[char])}</div>' for family in ('Current',char+'A',char+'B'))
        research = f'<details><summary>Campioni e ragionamento per {char}</summary><p>{html.escape(note["observed"])}</p><p><b>A:</b> {html.escape(note["A"])}</p><p><b>B:</b> {html.escape(note["B"])}</p><p class="note">Riferimenti: {html.escape(", ".join(note["primary"]))}. Peso, raccordi e proporzioni sono scelte contemporanee.</p>'
        if images: research += f'<img loading="lazy" src="historical-{char}.png" alt="Localizzazioni storiche della {char}, BNE, specchiate e ingrandite; nessuna nuova risoluzione">'
        sections += f'<section id="letter-{char}"><h2>{char}</h2><div class="triplet">{cells}</div>{research}</details></section>'
    with TTFont(out/'Leonardus-1211-Regular.ttf') as font: known = sorted(font.getBestCmap())
    page = '''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Leonardus - studio a e m n u</title><style>
FACES
*{box-sizing:border-box}body{margin:0;background:#f7f4ec;color:#263b32;font:16px/1.5 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1{font-size:34px;margin:12px 0}h2{font-size:28px;margin:0 0 12px}.eyebrow{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#637363}.intro{max-width:1050px}.controls{display:flex;gap:22px;align-items:center;flex-wrap:wrap;padding:15px 0}.triplet{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.columns{position:sticky;top:0;background:#f7f4ec;border-bottom:1px solid #bfc9b7;padding:14px 0;z-index:2}.columns b{padding:0 10px}.sample{font-size:var(--size,36pt);line-height:1.65;overflow-wrap:anywhere;padding:8px}.note{font-size:14px;color:#5b6a59}section{border:1px solid #ccd4c5;background:#fffdf6;border-radius:8px;padding:20px;margin:18px 0}summary{cursor:pointer;color:#3d6041}details{border-top:1px solid #dce1d5;padding-top:13px;margin-top:15px}img{max-width:100%;height:auto}textarea{font:inherit;width:100%;min-height:100px;padding:14px;background:#fffdf6;border:1px solid #afbaaa;border-radius:6px}button{font:inherit;padding:8px 12px;background:#fffdf6;border:1px solid #afbaaa;border-radius:6px}a{color:#365e43}.base{font-family:Current}.allA{font-family:AllA}.allB{font-family:AllB}@media(max-width:700px){main{padding:15px}.triplet{gap:5px}.sample{font-size:min(var(--size),26pt);padding:3px}.columns{font-size:13px}}@media print{.controls,textarea,details{display:none}.columns{position:static}section{break-inside:avoid}.sample{font-size:25pt}}
</style><main><div class="eyebrow">Leonardus | dieci proposte da scegliere</div><h1>a, e, m, n, u: dal campione alla parola</h1><p class="intro">Confronto con la Regular <b>1.211</b>. Per ciascuna lettera, <b>A</b> cerca equilibrio di lettura; <b>B</b> esplora capanne, spalle e raccordi più marcati. Nelle cinque sezioni cambia soltanto la lettera indicata: puoi scegliere combinazioni miste.</p><p class="note intro"><b>Esito della ricerca del dettaglio:</b> il PDF BNE verificato non offre più risoluzione del JPEG. I confronti usano 27 localizzazioni già documentate, con contesti più ampi; l’ingrandimento non aggiunge pixel. Arundel è una pista ad alta risoluzione, non usata per questi disegni. Il font installato resta Leonardus 1211.</p><div class="controls"><label>Corpo <input id="size" type="range" min="12" max="60" value="36"><output id="sizeLabel">36 pt</output></label><button id="reset">Ripristina testo</button><a href="words-comparison.png">Tavola delle parole</a></div><p id="status" role="status">Caricamento dei font di confronto…</p><div class="columns triplet"><b>1.211 attuale</b><b>A · equilibrio di lettura</b><b>B · esplorativa</b></div>
SECTIONS
<h2>Prova le due serie complete</h2><p class="note">Qui cambiano insieme tutte e cinque le lettere. È un controllo del ritmo complessivo; le scelte per lettera restano indipendenti.</p><textarea id="text" aria-label="Testo da confrontare" spellcheck="false">Una mano leggera tiene una penna. La natura muta, mentre una mente umana ne cerca la misura.</textarea><p id="unsupported" role="status" class="note"></p><div class="triplet"><div id="t0" class="sample base"></div><div id="t1" class="sample allA"></div><div id="t2" class="sample allB"></div></div><details><summary>Limiti, fonti e stato delle proposte</summary><p>Le letture già revisionate conservano le loro riserve. M08 e u08 restano escluse come geometrie principali. Le parole sono esempi moderni, non trascrizioni certificate. Le varianti non attestano pressione o ordine dei tratti e non hanno approvazione umana.</p><p>Imágenes procedentes de los fondos de la Biblioteca Nacional de España, MSS/8937, folii 1r–4r. Ritaglio, specchiatura e ingrandimento dichiarati; nessun avallo BNE. Le riproduzioni restano locali e sono escluse da Git. Contorni originali Leonardus, OFL 1.1.</p><a href="/docs/AEMNU_VARIANT_STUDY.md">Registro dello studio</a></details></main><script>
const box=document.querySelector('#text'),range=document.querySelector('#size'),initial=box.value,known=new Set(KNOWN);
function update(){document.documentElement.style.setProperty('--size',range.value+'pt');document.querySelector('#sizeLabel').textContent=range.value+' pt';for(const id of ['t0','t1','t2'])document.getElementById(id).textContent=box.value;const missing=[...new Set([...box.value].filter(c=>!known.has(c.codePointAt(0))&&!['\\n','\\r','\\t'].includes(c)))];document.querySelector('#unsupported').textContent=missing.length?'Caratteri fuori repertorio: '+missing.join(' '):'';}
range.addEventListener('input',update);box.addEventListener('input',update);document.querySelector('#reset').onclick=()=>{box.value=initial;update();};Promise.all(['Current','AllA','AllB',...['a','e','m','n','u'].flatMap(c=>[c+'A',c+'B'])].map(name=>document.fonts.load('36px '+name))).then(fonts=>{if(fonts.some(f=>!f.length))throw Error();document.querySelector('#status').textContent='Tutti i font caricati. Cinque confronti indipendenti e due serie complete.';}).catch(()=>document.querySelector('#status').textContent='Caricamento incompleto: servire la cartella completa via localhost.');update();
</script></html>'''
    (out/'index.html').write_text(page.replace('FACES', faces).replace('SECTIONS', sections).replace('KNOWN', json.dumps(known)), encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--originals', type=Path)
    args = parser.parse_args(); out = within(ROOT, args.out, 'build')
    if out.exists(): raise ValueError('Use a new directory to preserve earlier comparisons')
    doc = validate(); out.mkdir(parents=True)
    base = ROOT/doc['base_font']; (out/'Leonardus-1211-Regular.ttf').write_bytes(base.read_bytes())
    results = []
    for variant in 'AB':
        results.append(build_font(variant, out/f'Leonardus-AEMNU-{variant}.ttf'))
        for char in LETTERS: results.append(build_font(variant, out/f'{char}-{variant}.ttf', character=char))
    count = source_sheets(doc, out, args.originals) if args.originals else 0
    words_proof(out, base); comparison_page(doc, out, bool(count))
    result = {'status': doc['status'], 'originals_verified': count, 'new_higher_detail_targets_acquired': False, 'fonts': results}
    (out/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
