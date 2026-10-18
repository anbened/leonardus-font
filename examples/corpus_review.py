"""Validate expansion metadata and render an offline, unapproved review dossier."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageOps
from leonardus.evidence import validated_samples

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BATCH = Path('data/lowercase_expansion_2026-10-14.json')
NEW_LETTERS = set('bcfghijkmpqstuvwxyz')
SAFE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]*\Z')
BNE_HOSTS = {'bnedigital.bne.es', 'www.bne.es', 'bne.es', 'catalogo.bne.es'}


def within(path, parent):
    """Resolve symlinks before enforcing a directory boundary."""
    path, parent = Path(path).resolve(), Path(parent).resolve()
    if not path.is_relative_to(parent) or path == parent:
        raise ValueError('Path escapes its permitted directory')
    return path


def source_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or parsed.hostname not in BNE_HOSTS
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise ValueError('Source links must use an official BNE HTTPS host')
    return value


def recorded_reviews(data_dir):
    """Read explicit group confirmations; a draft can never promote registry rows."""
    data_dir = Path(data_dir).resolve()
    records = {}
    for path in sorted(data_dir.glob('human_guided_review_*.json')):
        within(path, data_dir)
        receipt = json.loads(path.read_text(encoding='utf-8'))
        if receipt.get('status') != 'human_decisions_recorded':
            raise ValueError('A recorded human review receipt is required')
        plan_path = within(data_dir.parent / receipt['plan_path'], data_dir)
        plan_bytes = plan_path.read_bytes()
        if hashlib.sha256(plan_bytes).hexdigest() != receipt['plan_sha256']:
            raise ValueError('Recorded review plan SHA-256 mismatch')
        plan = json.loads(plan_bytes)
        for relative in plan['batches']:
            batch_path = within(data_dir.parent / relative, data_dir)
            if hashlib.sha256(batch_path.read_bytes()).hexdigest() != plan['batch_sha256'][relative]:
                raise ValueError('Recorded review batch SHA-256 mismatch')
        if receipt['review_id'] != plan['review_id'] or receipt['reviewer'] != 'Human review':
            raise ValueError('Recorded review identity mismatch')
        date = datetime.fromisoformat(receipt['recorded_at'])
        if date.tzinfo is None:
            raise ValueError('Recorded review date needs a timezone')
        groups = [g for g in plan['groups'] if g['id'] == receipt['group_id']]
        if len(groups) != 1:
            raise ValueError('Recorded review must identify one planned group')
        expected = set(groups[0]['sample_ids'])
        decisions = receipt['decisions']
        if (not isinstance(decisions, list) or len(decisions) != len(expected)
                or {d['sample_id'] for d in decisions} != expected):
            raise ValueError('Recorded review must cover exactly its planned group')
        for decision in decisions:
            if (set(decision) != {'sample_id', 'letter_reading', 'folio_review', 'case_review', 'notes'}
                    or decision['letter_reading'] != 'accepted'
                    or decision['folio_review'] != 'confirmed'
                    or decision['case_review'] != 'lowercase'
                    or not isinstance(decision['notes'], str)):
                raise ValueError('Receipt requires explicit compatible, confirmed, lowercase decisions')
            sample_id = decision['sample_id']
            if sample_id in records:
                raise ValueError('Duplicate recorded sample review')
            notes = (f'Lettura compatibile; foliazione confermata dal confronto; minuscola. '
                     f'Decisione registrata in data/{path.name}. '
                     'Non conferma il token completo, la segmentazione dei contorni, '
                     'l’autenticità paleografica o il disegno del font.')
            records[sample_id] = dict(decision, reviewer=receipt['reviewer'],
                                     reviewed_at=receipt['recorded_at'], review_notes=notes)
    return records


def rectangle(value, width, height):
    if (not isinstance(value, list) or len(value) != 4
            or any(type(item) is not int for item in value)):
        raise ValueError('Rectangles require four integer coordinates')
    x, y, w, h = value
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
        raise ValueError('Rectangle lies outside the source image')
    return value


def validate_batch(batch, root=ROOT, verify_images=False):
    """Metadata checks run without local scans; rendering also checks image bytes."""
    root = Path(root).resolve()
    if not isinstance(batch, dict) or not SAFE_ID.fullmatch(batch.get('batch_id', '')):
        raise ValueError('Invalid batch identifier')
    source = batch['source']
    for key in ('url', 'viewer_url'):
        source_url(source[key])
    if not isinstance(source.get('attribution'), str) or not source['attribution'].strip():
        raise ValueError('Source attribution is required')
    samples = batch['samples']
    if not isinstance(samples, list) or not samples:
        raise ValueError('A batch must contain expansion samples')
    seen, seen_crops, verified = set(), set(), set()
    for sample in samples:
        sample_id = sample['sample_id']
        if not isinstance(sample_id, str) or not SAFE_ID.fullmatch(sample_id) or sample_id in seen:
            raise ValueError('Sample identifiers must be unique and safe filenames')
        seen.add(sample_id)
        if sample['character'] not in NEW_LETTERS:
            raise ValueError('This dossier accepts only new lowercase candidates')
        if sample.get('status', 'candidate') != 'candidate':
            raise ValueError('A review dossier cannot promote a candidate')
        if type(sample['page']) is not int or sample['page'] <= 0:
            raise ValueError('A positive viewer page is required')
        if not isinstance(sample['folio'], str) or not re.fullmatch(r'\d+[rv]', sample['folio']):
            raise ValueError('Folio requires a recto or verso reference')
        if not isinstance(sample['source_image_id'], str) or not sample['source_image_id']:
            raise ValueError('Source image identifier is required')
        for key in ('token', 'rationale', 'doubts'):
            if not isinstance(sample[key], str):
                raise ValueError(f'{key} must be text')
        optional_choices = {
            'folio_status': {'working_mapping_pending_review', 'agent_concordance_pending_review'},
            'context_kind': {'prose', 'diagram_label'},
        }
        for key, choices in optional_choices.items():
            if key in sample and (not isinstance(sample[key], str) or sample[key] not in choices):
                raise ValueError(f'Invalid {key}')
        for key in ('observed_form', 'case_status'):
            if key in sample and not isinstance(sample[key], str):
                raise ValueError(f'{key} must be text')
        if 'alternatives' in sample and (not isinstance(sample['alternatives'], list)
                or any(not isinstance(value, str) for value in sample['alternatives'])):
            raise ValueError('alternatives must be a list of text')
        position = sample['position']
        if position is not None and (type(position) is not int or position < 1):
            raise ValueError('Position must be a positive 1-based integer or null')
        width, height = sample['image_width'], sample['image_height']
        if any(type(v) is not int or v <= 0 for v in (width, height)):
            raise ValueError('Image dimensions must be positive integers')
        digest = sample['image_sha256']
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError('Source SHA-256 must contain 64 lowercase hexadecimal digits')
        local_text = sample['source_local_path']
        local = Path(local_text)
        if local.is_absolute() or '..' in local.parts or '\\' in local_text:
            raise ValueError('Source image paths must be relative to data/scans')
        scans = root / 'data' / 'scans'
        if not scans.resolve().is_relative_to(root):
            raise ValueError('Scan directory escapes the repository')
        image_path = within(root / 'data' / local, scans)
        for kind in ('crop', 'context'):
            mirrored = rectangle(sample[f'mirror_{kind}'], width, height)
            raw = rectangle(sample[f'raw_{kind}'], width, height)
            x, y, w, h = mirrored
            if raw != [width - x - w, y, w, h]:
                raise ValueError('Raw and mirrored coordinates disagree')
        x, y, w, h = sample['mirror_crop']
        cx, cy, cw, ch = sample['mirror_context']
        if x < cx or y < cy or x + w > cx + cw or y + h > cy + ch:
            raise ValueError('Context must contain the complete target crop')
        crop_identity = (digest, tuple(sample['raw_crop']))
        if crop_identity in seen_crops:
            raise ValueError('Duplicate raw crop identity')
        seen_crops.add(crop_identity)
        identity = (image_path, digest, width, height)
        if verify_images and identity not in verified:
            if hashlib.sha256(image_path.read_bytes()).hexdigest() != digest:
                raise ValueError('Source image SHA-256 mismatch')
            with Image.open(image_path) as image:
                if image.size != (width, height):
                    raise ValueError('Source image dimensions mismatch')
            verified.add(identity)
    return batch


def validate_registry(batch, sources_csv, evidence_csv):
    """Match source checkpoints and receipt-backed reviews against the registry."""
    rows = validated_samples(sources_csv, evidence_csv, check_images=False)
    registry = {row['sample_id']: row for row in rows}
    reviews = recorded_reviews(Path(evidence_csv).parent)
    ids = {sample['sample_id'] for sample in batch['samples']}
    if len(ids) != len(batch['samples']):
        raise ValueError('Duplicate sample identifiers in the batch')
    paths = {sample['source_local_path'] for sample in batch['samples']}
    corresponding = {row['sample_id'] for row in rows
                     if row['target_character'] in NEW_LETTERS
                     and row['source_local_path'] in paths}
    if ids != corresponding:
        raise ValueError('Batch and evidence registry candidate lists disagree')
    fields = {'character': 'target_character', 'folio': 'folio',
              'source_local_path': 'source_local_path', 'source_image_id': 'source_image_id',
              'image_sha256': 'image_sha256', 'image_width': 'image_width',
              'image_height': 'image_height'}
    for sample in batch['samples']:
        row = registry.get(sample['sample_id'])
        if row is None:
            raise ValueError('Batch candidate is absent from the evidence registry')
        for batch_key, csv_key in fields.items():
            if str(sample[batch_key]) != row[csv_key]:
                raise ValueError(f'Batch and evidence registry disagree on {csv_key}')
        raw = [int(row[key]) for key in ('crop_x', 'crop_y', 'crop_width', 'crop_height')]
        if raw != sample['raw_crop'] or row['source_url'] != batch['source']['url']:
            raise ValueError('Batch and evidence registry crop/source disagree')
        if (row['source_kind'] != 'historical' or row['mirror_applied'] != 'true'
                or row['rotation_degrees'] != '0' or row['original_direction'] != 'rtl'):
            raise ValueError('Expansion source and transformations must remain unchanged')
        recorded = reviews.get(sample['sample_id'])
        if recorded:
            if (row['review_status'] != 'reviewed'
                    or any(row[key] != recorded[key] for key in ('reviewer', 'review_notes', 'reviewed_at'))):
                raise ValueError('Registry review disagrees with the recorded human decision')
        elif (row['review_status'] != 'candidate'
                or any(row[key] for key in ('reviewer', 'review_notes', 'reviewed_at'))):
            raise ValueError('Expansion rows must remain unreviewed historical candidates')
    return rows


def bounds(rect):
    x, y, w, h = rect
    return x, y, x + w, y + h


def render_dossier(batch, out, root=ROOT):
    """Only derived mirrored PNGs and review templates are written under build/."""
    root = Path(root).resolve()
    build = root / 'build'
    if not build.resolve().is_relative_to(root):
        raise ValueError('Build directory escapes the repository')
    out = within(out if Path(out).is_absolute() else root / out, build)
    validate_batch(batch, root, verify_images=True)
    reviews = recorded_reviews(root / 'data')
    for sample in batch['samples']:
        for suffix in ('crop', 'context'):
            within(out / f"{sample['sample_id']}-{suffix}.png", out)
    for filename in ('index.html', 'review.csv'):
        within(out / filename, out)
    out.mkdir(parents=True, exist_ok=True)
    cards = []
    escape = lambda value: html.escape(str(value), quote=True)
    samples = sorted(batch['samples'], key=lambda sample: (sample['character'], sample['sample_id']))
    previous = None
    for sample in samples:
        sample_id = sample['sample_id']
        with Image.open(root / 'data' / sample['source_local_path']) as original:
            mirrored = ImageOps.mirror(original.convert('RGB'))
        crop = mirrored.crop(bounds(sample['mirror_crop']))
        crop = crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.NEAREST)
        context = mirrored.crop(bounds(sample['mirror_context']))
        x, y, w, h = sample['mirror_crop']
        cx, cy, _, _ = sample['mirror_context']
        ImageDraw.Draw(context).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1),
                                          outline='#d02020', width=2)
        crop.save(out / f'{sample_id}-crop.png')
        context.save(out / f'{sample_id}-context.png')
        if sample['character'] != previous:
            previous = sample['character']
            cards.append(f'<h2 id="letter-{previous}">Proposta di lettura {previous}</h2>')
        viewer_link = source_url(batch['source']['viewer_url'])
        viewer_link += ('&' if '?' in viewer_link else '?') + f"page={sample['page']}"
        folio_label = 'Folio'
        if 'folio_status' in sample and sample_id not in reviews:
            folio_label = '<strong>Foliazione di lavoro DA REVISIONARE</strong>'
        metadata = []
        if 'context_kind' in sample:
            context_label = {'prose': 'prosa', 'diagram_label': 'etichetta di diagramma'}
            metadata.append(f"Contesto: {escape(context_label[sample['context_kind']])}.")
        if 'observed_form' in sample:
            metadata.append(f"Forma osservata: {escape(sample['observed_form'].rstrip('.'))}.")
        if 'alternatives' in sample:
            alternatives = '; '.join(sample['alternatives']) or 'nessuna annotata'
            caption = 'Alternative della selezione iniziale' if sample_id in reviews else 'Alternative da valutare'
            metadata.append(f'{caption}: {escape(alternatives)}.')
        if 'case_status' in sample:
            case_labels = {'proposed_lowercase': 'minuscola proposta, da confermare',
                           'unresolved_isolated_label': 'maiuscola/minuscola non stabilita per etichetta isolata'}
            case = ('minuscola confermata nella revisione registrata' if sample_id in reviews
                    else case_labels.get(sample['case_status'], sample['case_status']))
            caption = 'Caso confermato' if sample_id in reviews else 'Caso proposto'
            metadata.append(f"{caption}: {escape(case)}.")
        metadata_html = ''.join(f'<p>{item}</p>' for item in metadata)
        status = ('reviewed, lettura compatibile / foliazione confermata dal confronto / minuscola; '
                  'vedi ricevuta di revisione' if sample_id in reviews else 'candidate, non revisionato')
        cards.append(f'''<article id="{escape(sample_id)}">
<h2>{escape(sample_id)} — {escape(sample['character'])}</h2>
<p>Stato: {status}. {folio_label} {escape(sample['folio'])};
pagina del viewer {sample['page']}; immagine {escape(sample['source_image_id'])}.</p>
<p>Lettura proposta del token: <strong>{escape(sample['token'])}</strong>;
posizione 1-based: {escape(sample['position'] if sample['position'] is not None else 'non fissata')}.
<a href="{escape(viewer_link)}">Apri pagina della fonte</a>.</p>
<p>Motivazione: {escape(sample['rationale'])}</p>
<p>Dubbi: {escape(sample['doubts'])}</p>
{metadata_html}
<p>Coordinate [x, y, larghezza, altezza]: originale {escape(sample['raw_crop'])};
specchiato {escape(sample['mirror_crop'])}; contesto originale {escape(sample['raw_context'])};
contesto specchiato {escape(sample['mirror_context'])}.</p>
<img src="{escape(sample_id)}-crop.png" alt="Campione specchiato {escape(sample_id)}">
<img src="{escape(sample_id)}-context.png" alt="Contesto con bersaglio rosso {escape(sample_id)}">
<p>SHA-256 originale: <code>{escape(sample['image_sha256'])}</code></p>
</article>''')
    source = batch['source']
    navigation = ' · '.join(f'<a href="#letter-{letter}">{letter}</a>'
                            for letter in sorted({sample['character'] for sample in samples}))
    document = f'''<!doctype html><html lang="it"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revisione corpus — {escape(batch['batch_id'])}</title>
<style>body{{font:18px/1.5 sans-serif;max-width:1200px;margin:2rem auto;padding:1rem}}
article{{border-top:1px solid #888;padding:1rem 0}}img{{max-width:100%;display:block;margin:1rem 0}}
code{{overflow-wrap:anywhere}}h1,h2{{line-height:1.2}}</style>
<h1>Campioni da revisione — {escape(batch['batch_id'])}</h1>
<nav aria-label="Indice delle lettere">{navigation}</nav>
<p>Il batch conserva le proposte iniziali; le conferme successive sono indicate nelle schede.
Le revisioni delle letture non approvano contorni o nuove forme del font.
Confrontare ogni bersaglio con il contesto e con il manoscritto originale.</p>
<p>Annotare review.csv: accepted per una lettura confermata, uncertain per una lettura dubbia,
rejected per una lettura respinta; indicare revisore, data e motivazione.
Il file parte con decisioni vuote e non aggiorna automaticamente registri o font.</p>
<p>Immagini specchiate orizzontalmente. Campione ingrandito 3× con nearest-neighbor;
contesto a scala 1:1, bersaglio delimitato in rosso. Nessun contrasto aggiuntivo.</p>
<p>{escape(source['attribution'])}. <a href="{escape(source['url'])}">Scheda della fonte</a>;
<a href="{escape(source['viewer_url'])}">Viewer originale</a>.
Riproduzioni BNE: CC BY 4.0 o equivalente; queste trasformazioni non implicano avallo della BNE.</p>
{''.join(cards)}</html>'''
    (out / 'index.html').write_text(document, encoding='utf-8')
    review_path = out / 'review.csv'
    if not review_path.exists():
        with review_path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['sample_id', 'character', 'decision', 'reviewer', 'date', 'notes'])
            for sample in batch['samples']:
                writer.writerow([sample['sample_id'], sample['character'], '', '', '', ''])
    return out / 'index.html'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, default=DEFAULT_BATCH)
    parser.add_argument('--out', type=Path, default=Path('build/corpus-review'))
    parser.add_argument('--check-only', action='store_true', help='Validate metadata without local images')
    args = parser.parse_args(argv)
    batch_path = args.batch if args.batch.is_absolute() else ROOT / args.batch
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    validate_batch(batch)
    validate_registry(batch, ROOT / 'data/source_registry.csv', ROOT / 'data/glyph_evidence.csv')
    if args.check_only:
        reviews = recorded_reviews(ROOT / 'data')
        count = sum(sample['sample_id'] in reviews for sample in batch['samples'])
        print(f"Validated {len(batch['samples'])} batch samples; {count} recorded human reviews (metadata only)")
    else:
        output = render_dossier(batch, args.out)
        print(output.relative_to(ROOT))


if __name__ == '__main__':
    main()
