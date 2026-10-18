"""Prepare a local, offline guided review without approving evidence or font forms."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

try:
    import corpus_review as corpus
except ModuleNotFoundError:
    from examples import corpus_review as corpus

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = Path('data/guided_review_2026-10-14.json')
READINGS = {'', 'accepted', 'uncertain', 'rejected'}
FOLIOS = {'', 'confirmed', 'uncertain'}
CASES = {'', 'lowercase', 'uppercase', 'uncertain'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text_field(value, field):
    if not isinstance(value, str):
        raise ValueError(f'{field} must be text')
    return value


def safe_id(value, field):
    if not isinstance(value, str) or not corpus.SAFE_ID.fullmatch(value):
        raise ValueError(f'{field} must be a safe identifier')
    return value


def validate_plan(plan, root=ROOT, verify_images=False):
    """Check entire pinned batches and registry before selecting review samples."""
    root = Path(root).resolve()
    if not isinstance(plan, dict):
        raise ValueError('Review plan must be an object')
    safe_id(plan.get('review_id'), 'review_id')
    if plan.get('status') != 'pending_human_review':
        raise ValueError('A plan cannot promote candidates or claim approval')
    paths, hashes = plan.get('batches'), plan.get('batch_sha256')
    if (not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths)
            or len(set(paths)) != len(paths)
            or not isinstance(hashes, dict) or set(hashes) != set(paths)):
        raise ValueError('Batch paths and SHA-256 entries must be unique and complete')
    samples, sources = {}, {}
    for relative in paths:
        if (not isinstance(relative, str) or '\\' in relative or '..' in Path(relative).parts
                or Path(relative).is_absolute()):
            raise ValueError('Batch path must be relative to data/')
        path = corpus.within(root / relative, root / 'data')
        expected = hashes[relative]
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise ValueError('Invalid batch SHA-256')
        data = path.read_bytes()
        if digest(data) != expected:
            raise ValueError('Batch SHA-256 mismatch')
        batch = json.loads(data)
        if batch.get('status', 'candidate') != 'candidate' or batch.get('human_review', False) is not False:
            raise ValueError('Pinned batch checkpoints must retain their original candidate status')
        corpus.validate_batch(batch, root, verify_images=verify_images)
        corpus.validate_registry(batch, root / 'data/source_registry.csv', root / 'data/glyph_evidence.csv')
        for sample in batch['samples']:
            sample_id = sample['sample_id']
            if sample_id in samples:
                raise ValueError('Duplicate sample identifier across batches')
            samples[sample_id], sources[sample_id] = sample, batch['source']
    groups = plan.get('groups')
    if not isinstance(groups, list) or not groups:
        raise ValueError('At least one review group is required')
    group_ids, selected = set(), set()
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError('A review group must be an object')
        group_id = safe_id(group.get('id'), 'group id')
        if group_id in group_ids:
            raise ValueError('Duplicate group identifier')
        group_ids.add(group_id)
        for field in ('title', 'rationale'):
            text_field(group.get(field), field)
        letters, ids = group.get('letters'), group.get('sample_ids')
        if (not isinstance(letters, list) or not letters
                or any(not isinstance(letter, str) or letter not in corpus.NEW_LETTERS for letter in letters)
                or len(set(letters)) != len(letters)):
            raise ValueError('Group letters must be distinct lowercase candidates')
        if not isinstance(ids, list) or not 1 <= len(ids) <= 10:
            raise ValueError('A group must contain 1 to 10 samples')
        for sample_id in ids:
            safe_id(sample_id, 'sample_id')
            if sample_id not in samples:
                raise ValueError('Unknown sample identifier in review group')
            if sample_id in selected:
                raise ValueError('Duplicate sample selection')
            if samples[sample_id]['character'] not in letters:
                raise ValueError('Selected sample does not match group letters')
            selected.add(sample_id)
        for field, allowed in (('letter_questions', set(letters)), ('sample_notes', set(ids))):
            entries = group.get(field)
            if not isinstance(entries, dict) or not set(entries).issubset(allowed):
                raise ValueError(f'Invalid {field} keys')
            for value in entries.values():
                text_field(value, field)
    if not isinstance(plan.get('deferred'), list):
        raise ValueError('Deferred items must be a list')
    return samples, sources


def export_groups(plan):
    return [{'id': group['id'], 'sample_ids': group['sample_ids']} for group in plan['groups']]


def validate_decisions(document, plan, plan_sha256):
    """A draft records observations only; blanks and uncertainty remain legitimate."""
    fields = {'review_id', 'status', 'plan_sha256', 'groups', 'decisions'}
    if not isinstance(document, dict) or set(document) != fields:
        raise ValueError('A decision draft must contain only the documented fields')
    if document['status'] != 'review_draft' or document['review_id'] != plan['review_id']:
        raise ValueError('Draft status or review identifier mismatch')
    if document['plan_sha256'] != plan_sha256:
        raise ValueError('Review plan SHA-256 mismatch')
    if document['groups'] != export_groups(plan):
        raise ValueError('Draft groups disagree with the pinned plan')
    allowed = {sample_id for group in plan['groups'] for sample_id in group['sample_ids']}
    decisions, seen = document['decisions'], set()
    if not isinstance(decisions, list):
        raise ValueError('Decisions must be a list')
    for decision in decisions:
        if (not isinstance(decision, dict) or set(decision)
                != {'sample_id', 'letter_reading', 'folio_review', 'case_review', 'notes'}):
            raise ValueError('A sample decision must contain only the documented fields')
        sample_id = decision['sample_id']
        if not isinstance(sample_id, str) or sample_id not in allowed:
            raise ValueError('Unknown decision sample identifier')
        if sample_id in seen:
            raise ValueError('Duplicate decision sample identifier')
        seen.add(sample_id)
        for field, choices in (('letter_reading', READINGS), ('folio_review', FOLIOS), ('case_review', CASES)):
            value = decision[field]
            if not isinstance(value, str) or value not in choices:
                raise ValueError(f'Invalid {field}')
        text_field(decision['notes'], 'notes')
    if seen != allowed:
        raise ValueError('Draft must include every selected sample, with blanks if undecided')
    return document


def selector(field, label, choices, selected='', locked=False):
    options = ''.join(f'<option value="{value}"{" selected" if value == selected else ""}>'
                      f'{html.escape(caption)}</option>' for value, caption in [('', 'Da valutare'), *choices])
    disabled = ' disabled' if locked else ''
    return f'<label>{label}<select data-field="{field}"{disabled}>{options}</select></label>'


SCRIPT = r'''
const state = JSON.parse(document.getElementById('review-data').textContent);
const sections = [...document.querySelectorAll('.review-group')];
const decisions = state.decisions;
let current = 0;
function showGroup(index) {
  current = index;
  sections.forEach((section, i) => section.hidden = i !== current);
  document.getElementById('group-choice').value = String(current);
  document.getElementById('previous').disabled = current === 0;
  document.getElementById('next').disabled = current === sections.length - 1;
  updateProgress();
}
function updateProgress() {
  const complete = item => item.letter_reading !== '' && item.folio_review !== '' && item.case_review !== '';
  const total = decisions.filter(complete).length;
  const ids = new Set(state.groups[current].sample_ids);
  const groupDone = decisions.filter(item => ids.has(item.sample_id) && complete(item)).length;
  const groupSize = ids.size;
  document.getElementById('progress').textContent =
    `Gruppo ${current + 1}/${sections.length}: ${groupDone}/${groupSize} schede compilate; totale ${total}/${decisions.length}.`;
  const counts = { accepted: 0, uncertain: 0, rejected: 0, empty: 0 };
  decisions.forEach(item => counts[item.letter_reading || 'empty']++);
  document.getElementById('summary').textContent =
    `Letture compatibili: ${counts.accepted}; dubbie: ${counts.uncertain}; respinte: ${counts.rejected}; da valutare: ${counts.empty}.`;
}
document.querySelectorAll('article[data-sample]').forEach(card => {
  const decision = decisions.find(item => item.sample_id === card.dataset.sample);
  card.querySelectorAll('[data-field]').forEach(control => {
    control.addEventListener('input', () => {
      decision[control.dataset.field] = control.value;
      updateProgress();
    });
  });
});
document.getElementById('group-choice').addEventListener('change', event => showGroup(Number(event.target.value)));
document.getElementById('previous').addEventListener('click', () => showGroup(current - 1));
document.getElementById('next').addEventListener('click', () => showGroup(current + 1));
document.getElementById('export').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(state, null, 2) + '\n'], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'review-draft.json';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
const firstPending = state.groups.findIndex(group => group.sample_ids.some(id => {
  const item = decisions.find(decision => decision.sample_id === id);
  return item.letter_reading === '' || item.folio_review === '' || item.case_review === '';
}));
showGroup(firstPending < 0 ? 0 : firstPending);
'''


def render_review(plan, plan_sha256, root=ROOT, out=Path('build/guided-review')):
    """Validate all originals before writing exclusively derived local artifacts."""
    root = Path(root).resolve()
    permitted = root / 'build/guided-review'
    if permitted.resolve() != permitted:
        raise ValueError('Review output directory escapes repository')
    out = Path(out)
    out = (out if out.is_absolute() else root / out).resolve()
    if out != permitted.resolve():
        raise ValueError('Review output must be build/guided-review')
    if not isinstance(plan_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', plan_sha256):
        raise ValueError('Invalid plan SHA-256')
    samples, sources = validate_plan(plan, root, verify_images=True)
    recorded = corpus.recorded_reviews(root / 'data')
    ids = [sample_id for group in plan['groups'] for sample_id in group['sample_ids']]
    for sample_id in ids:
        for suffix in ('crop', 'context', 'original'):
            corpus.within(out / f'{sample_id}-{suffix}.png', out)
    corpus.within(out / 'index.html', out)
    out.mkdir(parents=True, exist_ok=True)
    escape = lambda value: html.escape(str(value), quote=True)
    sections = []
    for group in plan['groups']:
        cards = []
        for sample_id in group['sample_ids']:
            sample, source = samples[sample_id], sources[sample_id]
            prior = recorded.get(sample_id, {})
            with Image.open(root / 'data' / sample['source_local_path']) as image:
                original = image.convert('RGB')
            mirrored = ImageOps.mirror(original)
            crop = mirrored.crop(corpus.bounds(sample['mirror_crop']))
            crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.NEAREST).save(out / f'{sample_id}-crop.png')
            original.crop(corpus.bounds(sample['raw_crop'])).save(out / f'{sample_id}-original.png')
            context = mirrored.crop(corpus.bounds(sample['mirror_context']))
            x, y, w, h = sample['mirror_crop']
            cx, cy, _, _ = sample['mirror_context']
            ImageDraw.Draw(context).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1), outline='#d02020', width=2)
            context.save(out / f'{sample_id}-context.png')
            viewer = source['viewer_url'] + ('&' if '?' in source['viewer_url'] else '?') + f"page={sample['page']}"
            context_kind = {'prose': 'prosa', 'diagram_label': 'etichetta di diagramma'}.get(sample.get('context_kind'), 'tipo di contesto non registrato')
            details = []
            for field, caption in (('observed_form', 'Forma osservata'), ('case_status', 'Caso proposto')):
                if field in sample:
                    value = sample[field]
                    if field == 'case_status':
                        value = {'proposed_lowercase': 'minuscola proposta, da confermare',
                                 'unresolved_isolated_label': 'maiuscola/minuscola non stabilita per etichetta isolata'}.get(value, value)
                        if prior:
                            value = 'minuscola confermata nella revisione registrata'
                    details.append(f'<p>{caption}: {escape(value)}.</p>')
            if 'folio_status' in sample and not prior:
                details.append('<p><strong>Foliazione di lavoro DA REVISIONARE:</strong> '
                               'concordanza proposta, non confermata indipendentemente.</p>')
            if 'alternatives' in sample:
                details.append(f"<p>Alternative: {escape('; '.join(sample['alternatives']))}.</p>")
            controls = selector('letter_reading', 'Lettura proposta', [('accepted', 'Compatibile'), ('uncertain', 'Dubbia'), ('rejected', 'Respinta')], prior.get('letter_reading', ''), bool(prior))
            controls += selector('folio_review', 'Foliazione', [('confirmed', 'Confermata dal confronto'), ('uncertain', 'Dubbia')], prior.get('folio_review', ''), bool(prior))
            controls += selector('case_review', 'Minuscola o maiuscola', [('lowercase', 'Minuscola'), ('uppercase', 'Maiuscola'), ('uncertain', 'Dubbia')], prior.get('case_review', ''), bool(prior))
            disabled = ' disabled' if prior else ''
            controls += f'<label>Note sulla lettura, foliazione e forma<textarea data-field="notes" rows="3"{disabled} placeholder="Solo osservazioni sul campione; evitare dati personali.">{escape(prior.get("notes", ""))}</textarea></label>'
            status = ('Revisione umana registrata: lettura compatibile, foliazione confermata dal confronto, minuscola.'
                      if prior else 'Candidate non revisionata.')
            folio_caption = 'confermata dal confronto' if prior else 'da revisionare'
            cards.append(f'''<article data-sample="{escape(sample_id)}" id="{escape(sample_id)}">
<h3>{escape(sample_id)} — lettura proposta {escape(sample['character'])}</h3>
<p>{status} Folio proposto <strong>{escape(sample['folio'])} — {folio_caption}</strong>;
pagina del viewer {sample['page']}; immagine {escape(sample['source_image_id'])}; contesto: {escape(context_kind)}.</p>
<p>Token proposto: <strong>{escape(sample['token'])}</strong>; posizione 1-based: {escape(sample['position'] if sample['position'] is not None else 'non fissata')}.</p>
<p>Motivazione iniziale: {escape(sample['rationale'])}</p><p>Dubbi della selezione iniziale: {escape(sample['doubts'])}</p>
{''.join(details)}
<p>Domanda per la lettera: {escape(group['letter_questions'].get(sample['character'], 'Confrontare lettura, caso e contesto.'))}</p>
<p>Nota per questo campione: {escape(group['sample_notes'].get(sample_id, 'Nessuna nota aggiuntiva.'))}</p>
<figure><img src="{escape(sample_id)}-crop.png" alt="Bersaglio specchiato 3×"><figcaption>Bersaglio specchiato, 3×.</figcaption></figure>
<figure><img src="{escape(sample_id)}-context.png" alt="Contesto specchiato con bersaglio rosso"><figcaption>Contesto specchiato, 1:1; bersaglio rosso.</figcaption></figure>
<details><summary>Orientamento originale e provenienza</summary>
<img src="{escape(sample_id)}-original.png" alt="Bersaglio nell'orientamento originale 1:1">
<p>Coordinate [x, y, larghezza, altezza]: originale {escape(sample['raw_crop'])}; specchiato {escape(sample['mirror_crop'])};
contesto originale {escape(sample['raw_context'])}; contesto specchiato {escape(sample['mirror_context'])}.</p>
<p>SHA-256 originale: <code>{escape(sample['image_sha256'])}</code>.</p>
<p>{escape(source['attribution'])}. <a href="{escape(source['url'])}" target="_blank" rel="noopener noreferrer">Scheda BNE</a>;
<a href="{escape(viewer)}" target="_blank" rel="noopener noreferrer">Apri la pagina originale</a>.
Riproduzioni BNE: CC BY 4.0 o equivalente; trasformazioni per studio locale, senza avallo della BNE.</p></details>
<div class="controls">{controls}</div></article>''')
        sections.append(f'<section class="review-group" id="{escape(group["id"])}"><h2>{escape(group["title"])}</h2><p>{escape(group["rationale"])}</p>{"".join(cards)}</section>')
    draft = {'review_id': plan['review_id'], 'status': 'review_draft', 'plan_sha256': plan_sha256,
             'groups': export_groups(plan), 'decisions': [dict(sample_id=sample_id, **{
                 field: recorded.get(sample_id, {}).get(field, '')
                 for field in ('letter_reading', 'folio_review', 'case_review', 'notes')}) for sample_id in ids]}
    embedded = json.dumps(draft, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    choices = ''.join(f'<option value="{i}">{i+1}. {escape(group["title"])}</option>' for i, group in enumerate(plan['groups']))
    reviewed_count = sum(sample_id in recorded for sample_id in ids)
    navigation_note = ('Revisione guidata completata: tutte le schede hanno una decisione registrata.'
                       if reviewed_count == len(ids) else 'La pagina apre il primo gruppo ancora da valutare.')
    document = f'''<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>Revisione guidata — {escape(plan['review_id'])}</title>
<style>body{{font:18px/1.5 sans-serif;max-width:1150px;margin:1rem auto;padding:1rem;background:#faf9f5;color:#222}}
h1,h2,h3{{line-height:1.2}}article{{border:1px solid #aaa;padding:1rem;margin:1.5rem 0;background:white}}
img{{max-width:100%;height:auto;display:block}}figure{{margin:1rem 0}}figcaption{{font-size:.9rem}}
.controls{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}}
label{{display:block}}select,textarea,button{{font:inherit;max-width:100%;padding:.4rem}}textarea,select{{display:block;width:100%;box-sizing:border-box}}
nav{{position:sticky;top:0;background:#faf9f5;padding:.75rem;border-bottom:1px solid #888}}code{{overflow-wrap:anywhere}}[hidden]{{display:none!important}}
</style></head><body><h1>Revisione guidata delle minuscole</h1>
<p>{len(ids)} campioni selezionati in {len(plan['groups'])} gruppi, massimo 10 per gruppo.
Questa selezione non comprende l'intero corpus: {len(samples)-len(ids)} candidate dei batch restano fuori dal percorso.
Nessun campione è approvato automaticamente. Le scelte riguardano identificazione, foliazione e caso, non autenticità paleografica o approvazione del font.</p>
<p>{reviewed_count} schede hanno una revisione umana già registrata:
sono precompilate e bloccate. Per rettificarle occorre una nuova decisione esplicita.
{navigation_note}</p>
<p>Confrontare ogni bersaglio con il contesto e la fonte. Immagini specchiate orizzontalmente;
ingrandimento 3× nearest-neighbor, nessun contrasto aggiuntivo; il crop originale 1:1 è disponibile per orientamento.</p>
<p>Le nuove scelte restano soltanto in memoria nella pagina: ricaricando o chiudendo si perdono.
Usare «Esporta bozza JSON» per conservarle. Il file non aggiorna registri o font e può contenere campi vuoti o dubbi.
Una scheda è compilata quando le tre scelte sono indicate; anche «Dubbia» conta come compilazione, senza equivalere a conferma.</p>
<noscript>Abilitare JavaScript per navigazione, conteggi ed esportazione. Tutte le schede sono leggibili senza JavaScript.</noscript>
<nav aria-label="Gruppi di revisione"><label>Gruppo<select id="group-choice">{choices}</select></label>
<button id="previous" type="button">Precedente</button> <button id="next" type="button">Successivo</button>
<p id="progress" aria-live="polite"></p></nav>
{''.join(sections)}
<h2>Riepilogo delle annotazioni</h2><p id="summary" aria-live="polite"></p>
<button id="export" type="button">Esporta bozza JSON</button>
<p>Stato esportato: review_draft. Piano SHA-256: <code>{plan_sha256}</code>.
Non inserire informazioni personali nelle note. Nessun servizio esterno riceve le annotazioni.</p>
<script id="review-data" type="application/json">{embedded}</script><script>{SCRIPT}</script></body></html>'''
    (out / 'index.html').write_text(document, encoding='utf-8')
    return out / 'index.html'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=DEFAULT_PLAN)
    parser.add_argument('--check-only', action='store_true', help='Check pinned metadata without scans')
    parser.add_argument('--validate-decisions', type=Path, help='Check a saved draft; does not import decisions')
    args = parser.parse_args(argv)
    path = args.plan if args.plan.is_absolute() else ROOT / args.plan
    data = path.read_bytes()
    plan, plan_sha256 = json.loads(data), digest(data)
    samples, _ = validate_plan(plan)
    count = sum(len(group['sample_ids']) for group in plan['groups'])
    if args.validate_decisions:
        validate_decisions(json.loads(args.validate_decisions.read_text(encoding='utf-8')), plan, plan_sha256)
        print(f'Validated review draft for {count} selected samples; no evidence imported')
    elif args.check_only:
        recorded = corpus.recorded_reviews(ROOT / 'data')
        reviewed = sum(sid in recorded for group in plan['groups'] for sid in group['sample_ids'])
        print(f'Validated {count} selected samples in {len(plan["groups"])} groups; {len(samples)} batch samples checked; {reviewed} recorded reviews')
    else:
        print(render_review(plan, plan_sha256).relative_to(ROOT))


if __name__ == '__main__':
    main()
