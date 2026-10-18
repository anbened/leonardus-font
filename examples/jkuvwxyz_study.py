"""Compare eight unapproved capital reinterpretations with Regular 1.260 and source contexts."""
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
MANIFEST = 'data/jkuvwxyz_variant_study_2026-10-16.json'
LETTERS = 'JKUVWXYZ'
WORDS = {'J': ['Jazz Junior', 'Jazz e nuovi ritmi.'],
         'K': ['Kilo Karate', 'Kilo e misura.'],
         'U': ['Uomo Universo', 'Uomo e universo.'],
         'V': ['Vinci Volo', 'Vinci studia il volo.'],
         'W': ['Weekend Whisky', 'Weekend di lettura.'],
         'X': ['Xilofono Xenon', 'Xilofono e ritmo.'],
         'Y': ['Yogurt Yoga', 'Yogurt dopo yoga.'],
         'Z': ['Zefiro Zaino', 'Zefiro muove le vele.']}
DEPENDENCIES = {'U': 'Ù'}



def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(root=ROOT):
    root = Path(root).resolve()
    doc = json.loads((root/MANIFEST).read_text(encoding='utf-8'))
    if (doc['schema_version'] != 1 or doc['scope'] != 'JKUVWXYZ_only'
            or doc['status'] != 'unapproved_contemporary_capital_studies'
            or any(doc[k] is not False for k in ('human_visual_design_approval',
                       'integration_approved', 'authenticity_claim', 'evidence_registry_changed',
                       'new_images_acquired'))
            or doc['new_reviewed_capital_readings'] != 0 or set(doc['variants']) != set('AB')):
        raise ValueError('Expected separate unapproved contemporary capital studies')
    for key, directory in [('base_font', 'fonts'), ('evidence', 'data'), ('prior_study', 'data')]:
        if sha(within(root, doc[key], directory)) != doc[key+'_sha256']:
            raise ValueError('Preserved font or evidence checkpoint changed')
    with (root/doc['evidence']).open(encoding='utf-8', newline='') as stream:
        evidence = {r['sample_id']: r for r in csv.DictReader(stream)}
    prior = json.loads((root/doc['prior_study']).read_text(encoding='utf-8'))
    contexts = {r['id']: r for r in doc['source_contexts']}
    if len(contexts) != 13 or len(doc['source_contexts']) != 13:
        raise ValueError('Expected six candidate localizations, three K observations and four reviewed lowercase comparisons')
    for item in contexts.values():
        x, y, w, h = item['mirror_crop']; cx, cy, cw, ch = item['mirror_context']
        if (not (0 <= cx <= x and 0 <= cy <= y and x+w <= cx+cw <= 1578
                 and y+h <= cy+ch <= 2174) or min(w,h) <= 0
                or item['raw_crop'] != [1578-x-w, y, w, h]
                or not item['folio'] or item['source_id'] != 'BNE_MADRID_I'
                or len(item['image_sha256']) != 64
                or not item['description'].strip()):
            raise ValueError('Invalid folio-level source localization')
        if item['kind'] in ('reviewed_lowercase_comparison_not_capital_evidence',
                            'candidate_lowercase_comparison_not_capital_evidence'):
            row = evidence[item['id']]
            expected_status = 'reviewed' if item['kind'].startswith('reviewed_') else 'candidate'
            raw = [int(row[k]) for k in ('crop_x', 'crop_y', 'crop_width', 'crop_height')]
            if (row['review_status'] != item['review_status'] or item['review_status'] != expected_status
                    or row['target_character'] != item['character'].lower()
                    or row['folio'] != item['folio'] or raw != item['raw_crop']
                    or row['source_image_id'] != item['source_image_id']
                    or row['image_sha256'] != item['image_sha256']):
                raise ValueError('Lowercase references must retain status, localization and case')
        elif (item['kind'] != 'case_unresolved_formal_observation'
                or item['review_status'] != 'agent_observation_not_human_reviewed'
                or item['character'] != 'K'
                or not any(t['id'] == item['id'] and t['kind'] == 'capital_or_case_unresolved_not_lowercase_evidence'
                           and t['review_status'] == 'not_lowercase_evidence'
                           and t['mirror_crop'] == item['mirror_crop'] and t['folio'] == item['folio']
                           and t['viewer_page'] == item['viewer_page']
                           and t['image_sha256'] == item['image_sha256'] for t in prior['source_contexts'])):
            raise ValueError('Formal K observations cannot become reviewed capital readings')
    with TTFont(root/doc['base_font']) as base:
        for variant, group in doc['variants'].items():
            if (group['family'] != f'Leonardus JKUVWXYZ {variant}'
                    or group['postscript'] != f'Leonardus-JKUVWXYZ-{variant}-Regular'
                    or set(group['glyphs']) != set(LETTERS)):
                raise ValueError('Expected separate families and only eight capital bases')
            for char, record in group['glyphs'].items():
                path = within(root, record['file'], 'glyphs/proposals/2026-10-16-jkuvwxyz')
                expected = {r['id'] for r in contexts.values() if r['character'] == char}
                if (sha(path) != record['sha256']
                        or record['classification'] != 'unapproved_contemporary_reinterpretation'
                        or record['historical_capital_attestation'] is not False
                        or not record['design_choice'].strip() or not record['parent_motifs']
                        or set(record['reference_context_ids']) != expected
                        or record['advance'] != base['hmtx'][base.getBestCmap()[ord(char)]][0]):
                    raise ValueError('Design, source category or advance differs')
                svg = ET.parse(path).getroot()
                if (svg.get('viewBox') != '0 0 1000 1000'
                        or any(e.get('stroke') not in (None, 'none') for e in svg.iter())
                        or any(not e.get('d', '').rstrip().upper().endswith('Z')
                               for e in svg.iter('{http://www.w3.org/2000/svg}path'))):
                    raise ValueError('Expected closed filled paths in the standard cell')
                glyph = _svg_to_glyph(path); glyph.recalcBounds(None)
                if (glyph.numberOfContours < 1 or not 0 <= glyph.xMin < glyph.xMax < record['advance']
                        or not -120 <= glyph.yMin < glyph.yMax <= 680):
                    raise ValueError('Proposal exceeds the design cell')
    return doc


def build_font(variant, output, root=ROOT, character=None):
    root = Path(root).resolve(); doc = validate(root)
    if variant not in ('A', 'B') or (character is not None and (len(character) != 1 or character not in LETTERS)):
        raise ValueError('Choose A or B and optionally one study letter')
    output = within(root, output, 'build'); group = doc['variants'][variant]
    selected = character or LETTERS
    family = group['family'] + (f' {character}' if character else '')
    postscript = group['postscript'].replace('-Regular', f'-{character}-Regular') if character else group['postscript']
    if output.exists():
        with TTFont(output) as old:
            if old['name'].getDebugName(6) != postscript:
                raise ValueError('Cannot overwrite another font family')
    with TTFont(root/doc['base_font'], recalcTimestamp=False) as font:
        font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
        cmap = font.getBestCmap()
        for char in selected:
            record = group['glyphs'][char]; name = cmap[ord(char)]
            glyph = _svg_to_glyph(root/record['file']); glyph.recalcBounds(None)
            font['glyf'][name] = glyph; font['hmtx'][name] = (record['advance'], glyph.xMin)
            for accent in DEPENDENCIES.get(char, ''):
                composite = font['glyf'][cmap[ord(accent)]]
                if len(composite.components) != 2 or composite.components[0].glyphName != name:
                    raise ValueError('Unexpected capital/accent dependency')
                composite.components[1].x = round((glyph.xMin+glyph.xMax)/2+20)
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
        font['OS/2'].recalcAvgCharWidth(font); font['head'].fontRevision = 1.261
        names = {1: family, 3: 'Leonardus:Capitals:20261016:'+variant+selected,
                 4: family+' Regular', 5: 'Version 1.261; unapproved Capitals study', 6: postscript,
                 10: 'Eight unapproved contemporary capital reinterpretations compared with unresolved technical candidates, K observations and reviewed lowercase references. J and W are designed completions. No newly reviewed capital reading, integration approval or authenticity claim. No source images embedded.'}
        for number, value in names.items():
            font['name'].setName(value, number, 3, 1, 0x409)
            font['name'].setName(value, number, 1, 0, 0)
        output.parent.mkdir(parents=True, exist_ok=True); font.save(output)
    return {'variant': variant, 'letters': selected, 'sha256': sha(output), 'family': family}


def source_sheets(doc, out, originals):
    for char in LETTERS:
        rows = [r for r in doc['source_contexts'] if r['character'] == char]
        if not rows: continue
        sheet = Image.new('RGB', (1200, 125+len(rows)*245), '#faf8f0'); draw = ImageDraw.Draw(sheet)
        draw.text((20, 15), f'{char} | BNE MSS/8937 | iniziali, etichette e minuscole di confronto', font=caption(22), fill='#263b32')
        draw.text((20, 49), 'Specchiati e ingranditi; rosso = localizzazione, non contorno. Foliazione di lavoro.', font=caption(20), fill='#596b5d')
        for i, item in enumerate(rows):
            path = Path(originals)/(item['image_sha256']+'.jpg')
            if sha(path) != item['image_sha256']: raise ValueError('Original image differs')
            with Image.open(path) as source: mirrored = ImageOps.mirror(source.convert('RGB'))
            x, y, w, h = item['mirror_crop']; cx, cy, cw, ch = item['mirror_context']; top = 100+i*245
            draw.text((20, top), item['id']+' | '+item['folio']+' | '+item['review_status'], font=caption(20), fill='#263b32')
            context = mirrored.crop((cx, cy, cx+cw, cy+ch))
            ImageDraw.Draw(context).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1), outline='#bd2929')
            for crop, at, maxw in [(mirrored.crop((x, y, x+w, y+h)), (20, top+35), 170), (context, (240, top+35), 930)]:
                scale = min(maxw/crop.width, 185/crop.height)
                sheet.paste(crop.resize((round(crop.width*scale), round(crop.height*scale)), Image.Resampling.NEAREST), at)
        sheet.save(out/f'historical-{char}.png')
    return len(doc['source_contexts'])


def words_proof(out, base):
    image = Image.new('RGB', (1650, 2560), '#faf8f2'); draw = ImageDraw.Draw(image)
    draw.text((25, 20), 'J K U V W X Y Z | cambia soltanto la maiuscola indicata', font=caption(27), fill='#263b32')
    for i, label in enumerate(['1.260 attuale', 'A - equilibrio di lettura', 'B - esplorativa']):
        draw.text((25+i*550, 80), label, font=caption(26), fill='#263b32')
    for n, char in enumerate(LETTERS):
        top = 140+n*285
        for i, path in enumerate([base, out/f'{char}-A.ttf', out/f'{char}-B.ttf']):
            x = 25+i*550
            ProofRenderer(path, 125).line(image, (x, top+80), char+' '+char+char)
            for j, word in enumerate(WORDS[char]): ProofRenderer(path, 48).line(image, (x, top+160+j*75), word)
        draw.line((25, top+255, 1620, top+255), fill='#ccd1c4')
    draw.text((25, 2480), 'Reinterpretazioni moderne non approvate. Parole moderne, non trascrizioni storiche.', font=caption(23), fill='#596b5d')
    image.save(out/'words-comparison.png')
    for pt in (12, 18, 36, 72):
        page = Image.new('RGB', (2300, 1950), '#faf8f2'); draw = ImageDraw.Draw(page)
        draw.text((25, 20), f'Capitals | {pt} pt a 96 DPI | HarfBuzz + FreeType', font=caption(25), fill='#263b32')
        for n, char in enumerate(LETTERS):
            for i, path in enumerate([base, out/f'{char}-A.ttf', out/f'{char}-B.ttf']):
                if n == 0: draw.text((25+i*765, 75), ['1.260', 'A', 'B'][i], font=caption(23), fill='#263b32')
                ProofRenderer(path, round(pt*96/72)).line(page, (25+i*765, 190+n*210), WORDS[char][0] if pt == 72 else WORDS[char][1])
        page.save(out/f'proof-{pt}pt.png')


def comparison_page(doc, out, images):
    def face(family, filename):
        return f"@font-face{{font-family:{family};src:url('{filename}?v={sha(out/filename)}')}}"
    faces = face('Current', 'Leonardus-1260-Regular.ttf')
    for variant in 'AB':
        faces += face('All'+variant, f'Leonardus-JKUVWXYZ-{variant}.ttf')
        for char in LETTERS: faces += face(char+variant, f'{char}-{variant}.ttf')
    sections = ''
    for char in LETTERS:
        note = doc['observations'][char]
        cells = ''.join(f'<div class="sample" style="font-family:{family}">{char} {char}{char}<br>{"<br>".join(WORDS[char])}</div>' for family in ('Current', char+'A', char+'B'))
        research = f'<p class="note">{html.escape(note["basis"])}</p><details><summary>Campioni e valutazione di {char}</summary><p>{html.escape(note["observed"])}</p><p><b>A:</b> {html.escape(note["A"])}</p><p><b>B:</b> {html.escape(note["B"])}</p>'
        if images and any(r['character'] == char for r in doc['source_contexts']): research += f'<img loading="lazy" src="historical-{char}.png" alt="Confronti storici non risolti per {char}, specchiati e ingranditi">'
        sections += f'<section id="letter-{char}"><h2>{char}</h2><div class="triplet">{cells}</div>{research}</details></section>'
    with TTFont(out/'Leonardus-1260-Regular.ttf') as font: known = sorted(font.getBestCmap())
    controls = ''.join(f'<label>{c} <select data-letter="{c}" aria-label="Variante per {c}"><option value="Current">1.260</option><option>A</option><option>B</option></select></label>' for c in LETTERS)
    page = '''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Leonardus - studio J K U V W X Y Z</title><style>
FACES
*{box-sizing:border-box}body{margin:0;background:#f7f4ec;color:#263b32;font:16px/1.5 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1{font-size:34px;margin:12px 0}h2{font-size:28px;margin:0 0 12px}.eyebrow{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#637363}.intro{max-width:1100px}.controls{display:flex;gap:22px;align-items:center;flex-wrap:wrap;padding:15px 0}.triplet{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.columns{position:sticky;top:0;background:#f7f4ec;border-bottom:1px solid #bfc9b7;padding:14px 0;z-index:2}.columns b{padding:0 10px}.sample{font-size:var(--size,36pt);line-height:1.65;overflow-wrap:anywhere;padding:8px}.note{font-size:14px;color:#5b6a59}section{scroll-margin-top:80px;border:1px solid #ccd4c5;background:#fffdf6;border-radius:8px;padding:20px;margin:18px 0}summary{cursor:pointer;color:#3d6041}details{border-top:1px solid #dce1d5;padding-top:13px;margin-top:15px}img{max-width:100%;height:auto}textarea{font:inherit;width:100%;min-height:90px;padding:14px;background:#fffdf6;border:1px solid #afbaaa;border-radius:6px}button,select{font:inherit;padding:7px;background:#fffdf6;border:1px solid #afbaaa;border-radius:6px}a{color:#365e43}.base{font-family:Current}.allA{font-family:AllA}.allB{font-family:AllB}@media(max-width:700px){main{padding:15px}.triplet{gap:5px}.sample{font-size:min(var(--size),26pt);padding:3px}.columns{font-size:13px}}@media print{.controls,textarea,details{display:none}.columns{position:static}section{break-inside:avoid}.sample{font-size:25pt}}
</style><main><div class="eyebrow">Leonardus | sedici studi da confrontare</div><h1>J, K, U, V, W, X, Y, Z: maiuscole a confronto</h1><p class="intro">La Regular <b>1.260</b> resta il riferimento. <b>A</b> cerca equilibrio di lettura; <b>B</b> esplora asole, chiusure e ritorni più marcati. In ogni riga cambia soltanto la lettera indicata: le scelte possono essere miste. Le minuscole e le diciotto maiuscole già scelte nella 1.260 sono identiche in tutte le colonne.</p><p class="note intro"><b>Stato della ricerca:</b> Tredici confronti da riproduzioni BNE già disponibili: sei localizzazioni candidate, tre osservazioni K di caso irrisolto e quattro minuscole revisionate. Nessuna nuova lettura maiuscola confermata o nuova acquisizione. J non usa la candidata ambigua come geometria primaria; W è una sintesi contemporanea senza campione diretto. Questo studio conserva il confronto con la 1.260. La scelta successiva adotta tutte le otto B: <a href="/specimen/Leonardus-1270-Trial.html">prova la 1.270 integrata</a>. J/W/Y/Z B prevalgono sui suggerimenti A.</p><nav><a href="#letter-J">J</a> · <a href="#letter-K">K</a> · <a href="#letter-U">U</a> · <a href="#letter-V">V</a> · <a href="#letter-W">W</a> · <a href="#letter-X">X</a> · <a href="#letter-Y">Y</a> · <a href="#letter-Z">Z</a> · <a href="#mixed">Componi la scelta</a></nav><div class="controls"><label>Corpo <input id="size" type="range" min="12" max="60" value="36"><output id="sizeLabel">36 pt</output></label><button id="reset">Ripristina testo</button><a href="words-comparison.png">Tavola delle parole</a></div><p id="status" role="status">Caricamento dei font di confronto…</p><div class="columns triplet"><b>1.260 attuale</b><b>A · equilibrio di lettura</b><b>B · esplorativa</b></div>
SECTIONS
<h2>Prova le due serie complete</h2><textarea id="text" aria-label="Testo da confrontare" spellcheck="false">Jazz e Karate. Uomo e Universo. Vinci studia il Volo. Weekend di lettura. Xilofono, Yogurt e Zefiro. JAZZ, KARATE, UOMO, VOLO, WEEKEND, XENON, YOGA, ZEFIRO. I J j; U V W; X Y Z 2. Ù Ù Ú.</textarea><p id="unsupported" role="status" class="note"></p><div class="triplet"><div id="t0" class="sample base"></div><div id="t1" class="sample allA"></div><div id="t2" class="sample allB"></div></div><section id="mixed"><h2>Componi la scelta</h2><p>Puoi mantenere la 1.260 o scegliere A/B per ogni lettera. Questa anteprima non installa né approva il font.</p><div class="controls">CONTROLS<button id="suggestion">Prova la combinazione proposta</button></div><p class="note">Proposta: J A · K B · U B · V B · W A · X B · Y A · Z A. J/W/Y/Z A privilegiano la lettura; K/U/V/X B esplorano raccordi più gestuali. Puoi mantenere la versione attuale per qualsiasi lettera. La successiva scelta umana adotta tutte le otto B. È un parere di disegno, non una certificazione storica.</p><p id="selection" class="note"></p><div id="mixedText" class="sample base"></div></section><details><summary>Fonti, limiti e riproducibilità</summary><p>Imágenes procedentes de los fondos de la Biblioteca Nacional de España, MSS/8937, folii di lavoro 2r, 2v, 3r, 4r, 4v, 5r, 18v, 153v. Confronti online e-Leo, Biblioteca Leonardiana. Ritaglio, specchiatura e ingrandimento dichiarati; nessun avallo. Le immagini restano locali, escluse da Git. Contorni originali Leonardus, OFL 1.1.</p><p>Le candidate non diventano letture confermate. La J alfabetica e la W sono completamenti moderni; la separazione U/V, la forcella Y e la traversa Z B sono progettate. Le parole straniere di prova sono reali e moderne, non trascrizioni di Leonardo. I riquadri localizzano segni e includono talvolta tratti adiacenti: non sono contorni certificati. Nessuna deduzione sull’ordine, pressione o velocità dei tratti. <a href="/docs/JKUVWXYZ_VARIANT_STUDY.md">Registro dello studio</a>.</p></details></main><script>
const box=document.querySelector('#text'),range=document.querySelector('#size'),initial=box.value,known=new Set(KNOWN),letters='JKUVWXYZ';
function update(){document.documentElement.style.setProperty('--size',range.value+'pt');document.querySelector('#sizeLabel').textContent=range.value+' pt';for(const id of ['t0','t1','t2'])document.getElementById(id).textContent=box.value;const missing=[...new Set([...box.value].filter(c=>!known.has(c.codePointAt(0))&&!['\\n','\\r','\\t'].includes(c)))];document.querySelector('#unsupported').textContent=missing.length?'Caratteri fuori repertorio: '+missing.join(' '):'';const choices=Object.fromEntries([...document.querySelectorAll('select[data-letter]')].map(s=>[s.dataset.letter,s.value]));document.querySelector('#selection').textContent=letters.split('').map(c=>c+' '+(choices[c]==='Current'?'1.260':choices[c])).join(' · ');const target=document.querySelector('#mixedText');target.replaceChildren();let run=null,previous='Current';for(const c of box.value){const key=c==='Ù'?'U':c;const family=/\\p{Mark}/u.test(c)?previous:(choices[key]&&choices[key]!=='Current'?key+choices[key]:'Current');if(!run||family!==previous){run=document.createElement('span');run.style.fontFamily=family;target.append(run);}run.textContent+=c;previous=family;}}
range.addEventListener('input',update);box.addEventListener('input',update);for(const s of document.querySelectorAll('select'))s.addEventListener('change',update);document.querySelector('#reset').onclick=()=>{box.value=initial;update();};document.querySelector('#suggestion').onclick=()=>{const proposed=SUGGESTED;for(const s of document.querySelectorAll('select[data-letter]'))s.value=proposed[s.dataset.letter];update();};Promise.all(['Current','AllA','AllB',...letters.split('').flatMap(c=>[c+'A',c+'B'])].map(name=>document.fonts.load('36px '+name))).then(fonts=>{if(fonts.some(f=>!f.length))throw Error();document.querySelector('#status').textContent='Tutti i 19 font caricati. Otto confronti indipendenti, Ù e accenti combinanti inclusi e anteprima della scelta mista.';}).catch(()=>document.querySelector('#status').textContent='Caricamento incompleto: servire la cartella completa via localhost.');update();
</script></html>'''
    (out/'index.html').write_text(page.replace('FACES', faces).replace('SECTIONS', sections).replace('CONTROLS', controls).replace('KNOWN', json.dumps(known)).replace('SUGGESTED', json.dumps(doc['recommendation'])), encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--originals', type=Path)
    args = parser.parse_args(); out = within(ROOT, args.out, 'build')
    if out.exists(): raise ValueError('Use a new directory to preserve earlier comparisons')
    doc = validate(); out.mkdir(parents=True)
    base = ROOT/doc['base_font']; (out/'Leonardus-1260-Regular.ttf').write_bytes(base.read_bytes())
    results = []
    for variant in 'AB':
        results.append(build_font(variant, out/f'Leonardus-JKUVWXYZ-{variant}.ttf'))
        for char in LETTERS: results.append(build_font(variant, out/f'{char}-{variant}.ttf', character=char))
    count = source_sheets(doc, out, args.originals) if args.originals else 0
    words_proof(out, base); comparison_page(doc, out, bool(count))
    result = {'status': doc['status'], 'source_contexts_verified': count, 'fonts': results}
    (out/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
