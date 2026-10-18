"""Validate manual segmentation proposals and prepare a separate, unapproved study."""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import math
import textwrap
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageOps
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from leonardus.fontbuild import _svg_to_glyph, _build_timestamp
from leonardus.lowercase import approved_lowercase

ET.register_namespace('', 'http://www.w3.org/2000/svg')

try:
    import guided_review as guided
except ModuleNotFoundError:
    from examples import guided_review as guided

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path('data/lowercase_design_2026-10-15.json')
LETTERS = set('bcfghimpqstuz')
FAMILY = 'Leonardus Lowercase Study 20261015'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def points(value, width, height, minimum):
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError('Annotation needs enough points')
    for point in value:
        if (not isinstance(point, list) or len(point) != 2
                or any(type(n) not in (int, float) or not math.isfinite(n) for n in point)
                or not 0 <= point[0] <= width - 1 or not 0 <= point[1] <= height - 1):
            raise ValueError('Annotation point outside native mirrored crop')
    if minimum == 3:
        area = sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(value, value[1:]+value[:1]))
        if abs(area) < 1:
            raise ValueError('Degenerate annotation polygon')
    elif len(value) != 2 or value[0] == value[1]:
        raise ValueError('Cut requires two distinct endpoints')


def validate(root=ROOT, images=False):
    root = Path(root).resolve()
    manifest = approved_lowercase(root)
    receipt_path = guided.corpus.within(root / manifest['design_review_receipt'], root / 'data')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    plan_path = guided.corpus.within(root / manifest['plan'], root / 'data')
    if sha(plan_path) != manifest['plan_sha256']:
        raise ValueError('Design plan hash mismatch')
    if sha(root / 'data/glyph_evidence.csv') != manifest['evidence_sha256']:
        raise ValueError('Evidence checkpoint changed')
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    samples, _ = guided.validate_plan(plan, root, verify_images=images)
    selected = {sid for group in plan['groups'] for sid in group['sample_ids']}
    reviews = guided.corpus.recorded_reviews(root / 'data')
    if not selected.issubset(reviews):
        raise ValueError('Every segmented sample needs a recorded reading review')
    annotations = {}
    for relative, digest in manifest['segmentation_sha256'].items():
        path = guided.corpus.within(root / relative, root / 'data/segmentation')
        if sha(path) != digest:
            raise ValueError('Segmentation file hash mismatch')
        data = json.loads(path.read_text(encoding='utf-8'))
        if data['status'] != 'unapproved_segmentation':
            raise ValueError('Segmentation cannot claim human approval')
        for item in data['samples']:
            sid = item['sample_id']
            if sid not in selected or sid in annotations:
                raise ValueError('Unknown or duplicate segmented sample')
            _, _, width, height = samples[sid]['mirror_crop']
            if not item['retained_polygons'] or not isinstance(item['notes'], str) or not item['notes'].strip():
                raise ValueError('Retained regions and explanatory notes are required')
            for key in ('retained_polygons', 'excluded_polygons', 'uncertain_polygons', 'cut_lines'):
                if not isinstance(item[key], list):
                    raise ValueError('Annotation regions must be lists')
                for shape in item[key]:
                    points(shape, width, height, 2 if key == 'cut_lines' else 3)
            annotations[sid] = item
    if set(annotations) != selected or set(manifest['glyphs']) != LETTERS:
        raise ValueError('Segmentation and design repertoire must match the selected corpus')
    for letter, record in manifest['glyphs'].items():
        expected = {sid for sid in selected if samples[sid]['character'] == letter}
        approved = letter in receipt['approved_designs']
        if (set(record['sample_ids']) != expected or len(record['sample_ids']) != len(expected)
                or record['classification'] != ('reviewed_design' if approved else 'unapproved_design')
                or record['segmentation_review'] != 'pending'
                or record['design_review'] != ('approved' if approved else 'pending')
                or record['limited_support'] != (len(expected) < 5)):
            raise ValueError('Design references or approval status disagree')
        for key in ('rationale', 'normalizations', 'review_questions'):
            if not record[key]:
                raise ValueError('Design rationale and review questions are required')
        for design in [record, *record.get('alternatives', []), *record.get('superseded_versions', [])]:
            path = guided.corpus.within(root / design['file'], root / 'glyphs/proposals/2026-10-15-lowercase')
            if sha(path) != design['sha256']:
                raise ValueError('Design SVG hash mismatch')
            glyph = _svg_to_glyph(path)
            glyph.recalcBounds(None)
            advance = design['advance']
            if (type(advance) is not int or not 150 <= advance <= 1000
                    or glyph.numberOfContours <= 0 or glyph.xMin < 0 or glyph.xMax >= advance
                    or glyph.yMin < -200 or glyph.yMax > 800):
                raise ValueError('Design exceeds cell, advance or vertical bounds')
        if approved and any(record[key] != receipt['approved_designs'][letter][key]
                            for key in ('file', 'sha256', 'advance')):
            raise ValueError('Approved design differs from the recorded approval')
    return manifest, samples, annotations


def output_dir(root):
    path = Path(root).resolve() / 'build/segmentation-review'
    if path.resolve() != path:
        raise ValueError('Study output cannot resolve through symlinks')
    return path


def paths(path):
    return ''.join(ET.tostring(e, encoding='unicode') for e in ET.parse(path).getroot()
                   if e.tag.rsplit('}', 1)[-1] == 'path')


def study_font(manifest, root=ROOT, short_s=False):
    """Copy project font into ignored build/ with a distinct experimental family."""
    root = Path(root).resolve()
    out = output_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    destination = out / ('Leonardus-Lowercase-Study-ShortS.ttf' if short_s else 'Leonardus-Lowercase-Study.ttf')
    guided.corpus.within(destination, out)
    with TTFont(root / manifest['base_font'], recalcTimestamp=False) as font:
        cmap = font.getBestCmap()
        for letter, record in manifest['glyphs'].items():
            if short_s and letter == 's':
                record = record['alternatives'][0]
            name = cmap[ord(letter)]
            glyph = _svg_to_glyph(root / record['file'])
            glyph.recalcBounds(None)
            font['glyf'][name] = glyph
            font['hmtx'][name] = (record['advance'], glyph.xMin)
        names = {1: FAMILY, 2: 'Regular', 3: 'Leonardus:LowercaseStudy:0.300',
                 4: FAMILY + ' Regular', 5: 'Version 0.300; unapproved study',
                 6: 'Leonardus-LowercaseStudy-20261015',
                 10: 'Contemporary design study: thirteen primary designs approved for integration. Historical segmentations pending. Remaining project outlines from Regular 1.000. Not authenticated handwriting.'}
        if short_s:
            for key in (1, 3, 4, 6):
                names[key] += '-ShortS'
            names[10] = ('Contemporary design study: thirteen primary designs approved; '
                         'unselected short s alternative. Segmentation and font integration '
                         'pending. Not authenticated handwriting.')
        for record in font['name'].names:
            if record.nameID in names:
                record.string = names[record.nameID].encode(record.getEncoding())
        if 'DSIG' in font:
            del font['DSIG']
        font['head'].fontRevision = .3
        font['head'].created = font['head'].modified = _build_timestamp()
        font.save(destination)
    return destination


def specimen(manifest, root=ROOT):
    """Self-contained project vectors only: suitable for GitHub without reproductions."""
    root = Path(root)
    rows = []
    for index, (letter, record) in enumerate(sorted(manifest['glyphs'].items())):
        top = 150 + index * 230
        old = root / f'glyphs/regular/alpha-0.200/uni{ord(letter):04X}.svg'
        rows.append(f'<text x="30" y="{top+80}" font-size="50">{letter}</text>')
        for x, drawing in [(130, paths(old)), (430, paths(root / record['file']))]:
            rows.append(f'<g transform="translate({x} {top}) scale(.18)">{drawing}</g>')
            rows.append(f'<path d="M{x} {top+144}h190" stroke="#bac4ca" fill="none"/>')
        status = 'disegno approvato'
        rows.append(f'<text x="720" y="{top+60}" font-size="21">{len(record["sample_ids"])} letture revisionate; {status}</text>')
        for line_index, line in enumerate(textwrap.wrap(record['rationale'], 45)[:4]):
            rows.append(f'<text x="720" y="{top+95+line_index*24}" font-size="18">{html.escape(line)}</text>')
        if record.get('alternatives'):
            rows.append(f'<g transform="translate(1200 {top}) scale(.18)">{paths(root / record["alternatives"][0]["file"])}</g>')
            rows.append(f'<text x="1190" y="{top+190}" font-size="18">Alternativa corta progettata</text>')
    height = 170 + 230 * len(manifest['glyphs'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="{height}" viewBox="0 0 1500 {height}">'
            '<rect width="100%" height="100%" fill="#faf8f2"/>'
            '<g fill="#26343b" font-family="sans-serif"><text x="30" y="45" font-size="30">Leonardus: 13 disegni approvati per integrazione</text>'
            '<text x="130" y="105" font-size="23">Regular 1.000</text><text x="430" y="105" font-size="23">Proposta</text>'
            '<text x="720" y="105" font-size="21">Riferimenti e interpretazione contemporanea</text>'
            + ''.join(rows) + '</g></svg>')


def s_specimen(manifest, root=ROOT):
    """Compare the previous and revised s using compiled study glyphs and shaping."""
    import uharfbuzz as hb
    try:
        from regular_specimen import shape
    except ModuleNotFoundError:
        from examples.regular_specimen import shape

    primary = study_font(manifest, root)
    rows = []
    for x, previous in ((50, True), (790, False)):
        with TTFont(primary, recalcTimestamp=False) as font:
            if previous:
                record = manifest['glyphs']['s']['superseded_versions'][0]
                name = font.getBestCmap()[ord('s')]
                glyph = _svg_to_glyph(Path(root) / record['file'])
                glyph.recalcBounds(None)
                font['glyf'][name] = glyph
                font['hmtx'][name] = (record['advance'], glyph.xMin)
            buffer = io.BytesIO()
            font.save(buffer)
            shaping_font = hb.Font(hb.Face(buffer.getvalue()))
            shaping_font.scale = (1000, 1000)
            hb.ot_font_set_funcs(shaping_font)
            glyphs, order = font.getGlyphSet(), font.getGlyphOrder()
            label = 'Proposta precedente' if previous else 'Nuova s con curva inferiore'
            rows.append(f'<text x="{x}" y="85" font-size="25">{label}</text>')
            for baseline, text, size in ((300, 's', 230), (455, 'scienza', 130),
                                         (625, 'stesso', 130), (795, 'sasso', 130)):
                cursor = x
                rows.append(f'<path d="M{x} {baseline}h650" stroke="#d8ddd9" fill="none"/>')
                for gid, _, advance, _, dx, dy in shape(shaping_font, text):
                    pen = SVGPathPen(glyphs)
                    glyphs[order[gid]].draw(pen)
                    rows.append(f'<path transform="translate({cursor+dx*size/1000:.3f} {baseline-dy*size/1000:.3f}) scale({size/1000} {-size/1000})" d="{pen.getCommands()}"/>')
                    cursor += advance * size / 1000
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="900" viewBox="0 0 1500 900">'
            '<rect width="1500" height="900" fill="#faf8f2"/><g fill="#26343b" font-family="sans-serif">'
            '<text x="50" y="36" font-size="22">Leonardus — revisione s del 15 ottobre 2026; nuova forma approvata</text>'
            + ''.join(rows)
            + '<text x="50" y="870" font-size="20">Curva inferiore progettata per leggibilità; s approvata. Confronto di disegno sulla base della Regular 1.000.</text></g></svg>')


def render(root=ROOT):
    root = Path(root).resolve()
    manifest, samples, annotations = validate(root, images=True)
    out = output_dir(root)
    # Check all intended destinations before writing derived assets.
    for sid in annotations:
        for suffix in ('target', 'overlay', 'retained', 'context'):
            guided.corpus.within(out / f'{sid}-{suffix}.png', out)
    for name in ('index.html', 'comparison.svg', 's-revision.svg', 'Leonardus-Lowercase-Study.ttf', 'Leonardus-Lowercase-Study-ShortS.ttf'):
        guided.corpus.within(out / name, out)
    out.mkdir(parents=True, exist_ok=True)
    sections = []
    esc = lambda value: html.escape(str(value), quote=True)
    for letter, record in sorted(manifest['glyphs'].items()):
        cards = []
        for sid in record['sample_ids']:
            sample, item = samples[sid], annotations[sid]
            with Image.open(root / 'data' / sample['source_local_path']) as image:
                original = image.convert('RGB')
            mirrored = ImageOps.mirror(original)
            target = mirrored.crop(guided.corpus.bounds(sample['mirror_crop']))
            overlay = target.convert('RGBA')
            layer = Image.new('RGBA', target.size)
            draw = ImageDraw.Draw(layer)
            mask = Image.new('L', target.size)
            mask_draw = ImageDraw.Draw(mask)
            for key, color in [('retained_polygons', (0, 150, 90, 75)), ('excluded_polygons', (210, 25, 40, 100)), ('uncertain_polygons', (255, 165, 0, 100))]:
                for polygon in item[key]:
                    polygon = [tuple(p) for p in polygon]
                    draw.polygon(polygon, fill=color)
                    if key != 'uncertain_polygons':
                        mask_draw.polygon(polygon, fill=255 if key == 'retained_polygons' else 0)
            for line in item['cut_lines']:
                draw.line([tuple(p) for p in line], fill=(30, 100, 240, 255), width=1)
            overlay = Image.alpha_composite(overlay, layer)
            retained = target.convert('RGBA')
            retained.putalpha(mask)
            for suffix, image in [('target', target), ('overlay', overlay), ('retained', retained)]:
                image.resize((target.width*4, target.height*4), Image.Resampling.NEAREST).save(out / f'{sid}-{suffix}.png')
            context = mirrored.crop(guided.corpus.bounds(sample['mirror_context']))
            x, y, w, h = sample['mirror_crop']
            cx, cy, _, _ = sample['mirror_context']
            ImageDraw.Draw(context).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1), outline='#d02020', width=2)
            context.save(out / f'{sid}-context.png')
            figures = ''.join(f'<figure><img src="{sid}-{suffix}.png" alt="{caption}"><figcaption>{caption}</figcaption></figure>'
                              for suffix, caption in [('target', 'Bersaglio specchiato 4×'), ('overlay', 'Annotazione proposta 4×'), ('retained', 'Regione mantenuta, senza binarizzazione'), ('context', 'Contesto specchiato 1:1')])
            cards.append(f'<article><h3>{sid}</h3><p>Folio {esc(sample["folio"])}; pagina BNE {sample["page"]}; lettura revisionata, segmentazione da revisionare.</p><p>{esc(item["notes"])}</p><div class="figures">{figures}</div><details><summary>Coordinate locali e provenienza</summary><pre>{esc(json.dumps(item, ensure_ascii=False, indent=2))}</pre><p>SHA256 originale: {sample["image_sha256"]}; crop specchiato {sample["mirror_crop"]}.</p></details></article>')
        alternative = ''.join(f'<figure><svg viewBox="0 0 1000 1000">{paths(root / alt["file"])}</svg><figcaption>{esc(alt["label"])}</figcaption></figure>' for alt in [*record.get('superseded_versions', []), *record.get('alternatives', [])])
        status = 'disegno approvato'
        sections.append(f'<section id="letter-{letter}"><h2>{letter} — {status}</h2><p>{esc(record["rationale"])}</p><p>Normalizzazioni: {esc("; ".join(record["normalizations"]))}</p><p>Questioni di provenienza e integrazione: {esc("; ".join(record["review_questions"]))}</p><div class="figures"><figure><svg viewBox="0 0 1000 1000">{paths(root / record["file"])}</svg><figcaption>Disegno indipendente, baseline 800; {status}</figcaption></figure>{alternative}</div>{"".join(cards)}</section>')
    study_font(manifest, root)
    study_font(manifest, root, short_s=True)
    (out / 'comparison.svg').write_text(specimen(manifest, root), encoding='utf-8')
    (out / 's-revision.svg').write_text(s_specimen(manifest, root), encoding='utf-8')
    navigation = ' · '.join(f'<a href="#letter-{c}">{c}</a>' for c in sorted(manifest['glyphs']))
    document = f'''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Leonardus — segmentazioni e disegni approvati</title>
<style>@font-face{{font-family:Study;src:url(Leonardus-Lowercase-Study.ttf)}}@font-face{{font-family:StudyShort;src:url(Leonardus-Lowercase-Study-ShortS.ttf)}}body{{font:18px/1.5 sans-serif;max-width:1200px;margin:auto;padding:24px;background:#faf8f2}}article{{border-top:1px solid #aaa;padding:12px}}.figures{{display:flex;flex-wrap:wrap;gap:18px}}figure{{margin:10px;max-width:45%}}img{{max-width:100%;image-rendering:pixelated}}figure svg{{width:180px;height:180px}}pre{{white-space:pre-wrap}}.proof{{font-family:Study;font-size:44px}}.short{{font-family:StudyShort}}nav{{position:sticky;top:0;background:#faf8f2;padding:8px}}</style>
<h1>Segmentazioni e disegni approvati</h1><p>61 campioni con letture revisionate; 13 disegni approvati per integrazione, compresa la s con curva inferiore. Le segmentazioni restano da revisionare. Nessuna autenticazione storica. Questo dossier conserva lo studio sulla base della Regular 1.000; la Regular 1.100 integra anche accenti e ancore.</p><nav>{navigation}</nav>
<p>Verde: regione mantenuta proposta; rosso: esclusione; arancio: confine incerto; blu: taglio proposto. Coordinate native locali al crop specchiato. Le regioni sono annotazioni manuali, non maschere certificate del tratto. La vista mantenuta conserva anche la carta interna alla regione: nessuna binarizzazione o ricostruzione dell'inchiostro.</p>
<p>Originali invariati. Imágenes procedentes de los fondos de la Biblioteca Nacional de España, MSS/8937; CC BY 4.0 o equivalente, ritaglio/specchiatura/annotazioni dichiarati, nessun avallo BNE. Le immagini di studio restano locali.</p>
<p><a href="comparison.svg">Confronto vettoriale con la Regular</a>; <a href="s-revision.svg">s precedente e nuova s nel testo</a>. TTF di studio separato, con famiglia distinta, usato soltanto in questa pagina. Lo studio conserva layout e accenti della 1.000; il font distribuito 1.100 integra le nuove basi, i compositi e le ancore verificate.</p>
<h2>Prova nel contesto — disegno sperimentale</h2><p class="proof">bambino macchina panni ghiaccio quaderno<br>stanza lungo foglio città famiglia<br>moto tutto uguale scienza zio</p>
<p>S rivista con curva inferiore / alternativa corta non selezionata:</p><p class="proof">scienza stanza stesso sasso</p><p class="proof short">scienza stanza stesso sasso</p>
<p>Le scelte dei tredici disegni sono registrate e non richiedono di essere ripetute. Le delimitazioni dei campioni restano ipotesi da revisionare separatamente.</p>{''.join(sections)}</html>'''
    (out / 'index.html').write_text(document, encoding='utf-8')
    return out / 'index.html'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--specimen-only', action='store_true')
    args = parser.parse_args()
    manifest, _, annotations = validate()
    if args.check_only:
        approved = sum(r['design_review'] == 'approved' for r in manifest['glyphs'].values())
        print(f'Validated {len(annotations)} proposed segmentations, {approved} approved designs for integration')
    elif args.specimen_only:
        print(specimen(manifest))
    else:
        print(render())
