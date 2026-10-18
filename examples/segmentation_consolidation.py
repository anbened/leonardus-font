"""Audit frozen segmentations and render small local batches without approvals."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import textwrap
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

try:
    import segmentation_review as review
except ModuleNotFoundError:
    from examples import segmentation_review as review

ROOT = Path(__file__).resolve().parents[1]
PLAN = Path('data/segmentation_consolidation_2026-10-15.json')
DECISIONS = {'compatible_with_reservations', 'needs_wider_context', 'uncertain', 'needs_correction'}


def annotation_sha(item):
    return hashlib.sha256(json.dumps(item, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def recorded_decisions(root, annotations):
    """A separate receipt records boundaries, never promotes frozen annotations."""
    root = Path(root)
    plan_path = root/PLAN
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    if plan['status'] != 'pending_human_review':
        raise ValueError('Consolidation plan cannot claim human approval')
    for path, digest in plan['source_sha256'].items():
        source = review.guided.corpus.within(root/path, root/'data')
        if review.sha(source) != digest:
            raise ValueError('Consolidation source checkpoint changed')
    planned = {r['sample_id']: r for r in plan['samples']}
    if (len(planned) != len(plan['samples']) or set(planned) != set(annotations)
            or any(r['human_decision'] is not None for r in plan['samples'])
            or any(planned[sid]['annotation_sha256'] != annotation_sha(item)
                   for sid, item in annotations.items())):
        raise ValueError('Plan selection or annotation checkpoint differs')
    decisions = {}
    for path in sorted((root/'data').glob('human_segmentation_consolidation_*.json')):
        receipt = json.loads(path.read_text(encoding='utf-8'))
        if (receipt['status'] != 'human_segmentation_decisions_recorded'
                or receipt['review_id'] != plan['review_id']
                or receipt['scope'] != 'segmentation_boundaries_only'
                or receipt['plan_sha256'] != review.sha(plan_path)
                or receipt['reviewer'] != 'Human review'
                or receipt['reading_changes'] is not False
                or receipt['design_changes'] is not False
                or receipt['authenticity_claim'] is not False
                or not receipt['quote'].strip() or not receipt['question'].strip()
                or datetime.fromisoformat(receipt['recorded_at']).tzinfo is None):
            raise ValueError('Human receipt scope or checkpoint differs')
        shown = review.guided.corpus.within(root/receipt['shown_sheet'], root/'build')
        if shown.exists() and review.sha(shown) != receipt['shown_sheet_sha256']:
            raise ValueError('Shown review sheet changed')
        for row in receipt['decisions']:
            sid = row['sample_id']
            if (sid not in planned or sid in decisions or row['decision'] not in DECISIONS
                    or row['annotation_sha256'] != annotation_sha(annotations[sid])
                    or row['uncertain_regions_approved'] is not False):
                raise ValueError('Decision has unknown sample, duplicate or unsupported approval')
            decisions[sid] = row['decision']
    return decisions


def original_index(directory):
    directory = Path(directory)
    return {hashlib.sha256(p.read_bytes()).hexdigest(): p
            for p in directory.rglob('*')
            if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png'}}


def delegated_decisions(root, samples, annotations, human):
    """Agent judgments under explicit delegation remain separate from human inspection."""
    root = Path(root)
    path = root/'data/agent_segmentation_review_2026-10-15.json'
    if not path.exists():
        return {}
    document = json.loads(path.read_text(encoding='utf-8'))
    authority = root/'data/completion_authorization_2026-10-15.json'
    authorization = json.loads(authority.read_text(encoding='utf-8'))
    if (document['status'] != 'agent_boundary_assessments_recorded'
            or document['reviewer'] != 'Agent under user delegation'
            or document['human_visual_review'] is not False
            or document['plan_sha256'] != review.sha(root/PLAN)
            or document['authorization_sha256'] != review.sha(authority)
            or authorization['scope'] != '26_basic_lowercase'
            or authorization['individual_human_visual_approval'] is not False
            or not authorization['instruction_quote'].strip()
            or document['reading_changes'] is not False
            or document['design_changes'] is not False
            or document['authenticity_claim'] is not False):
        raise ValueError('Delegated assessment scope or attribution differs')
    result = {}
    for row in document['decisions']:
        sid = row['sample_id']
        if (sid not in annotations or sid in human or sid in result
                or row['annotation_sha256'] != annotation_sha(annotations[sid])
                or row['image_sha256'] != samples[sid]['image_sha256']
                or row['decision'] not in {'compatible_with_reservations', 'uncertain'}
                or row['uncertain_regions_approved'] is not False
                or not row['reason'].strip()):
            raise ValueError('Delegated decision changed provenance or promotes uncertainty')
        result[sid] = row
    if set(result) != set(annotations)-set(human):
        raise ValueError('Delegated assessment must cover exactly the remaining samples')
    return result


def verified_image(sample, originals):
    path = originals.get(sample['image_sha256'])
    if path is None:
        return None
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sample['image_sha256']:
        raise ValueError('Original image hash changed')
    with Image.open(io.BytesIO(data)) as image:
        if image.size != (sample['image_width'], sample['image_height']):
            raise ValueError('Original image dimensions differ')
        return image.convert('RGB')


def views(original, sample, item):
    mirrored = ImageOps.mirror(original)
    bounds = review.guided.corpus.bounds
    target = mirrored.crop(bounds(sample['mirror_crop']))
    layer = Image.new('RGBA', target.size)
    draw = ImageDraw.Draw(layer)
    mask = Image.new('L', target.size)
    mask_draw = ImageDraw.Draw(mask)
    for key, color in [('retained_polygons', (0, 150, 90, 75)),
                       ('excluded_polygons', (210, 25, 40, 100)),
                       ('uncertain_polygons', (255, 165, 0, 100))]:
        for polygon in item[key]:
            polygon = [tuple(p) for p in polygon]
            draw.polygon(polygon, fill=color)
            if key != 'uncertain_polygons':
                mask_draw.polygon(polygon, fill=255 if key == 'retained_polygons' else 0)
    for line in item['cut_lines']:
        draw.line([tuple(p) for p in line], fill=(30, 100, 240, 255), width=1)
    retained = target.convert('RGBA')
    retained.putalpha(mask)
    context = mirrored.crop(bounds(sample['mirror_context']))
    x, y, w, h = sample['mirror_crop']
    cx, cy, _, _ = sample['mirror_context']
    ImageDraw.Draw(context).rectangle((x-cx, y-cy, x-cx+w-1, y-cy+h-1),
                                     outline='#d02020', width=1)
    return [original.crop(bounds(sample['raw_crop'])), target,
            Image.alpha_composite(target.convert('RGBA'), layer), retained, context]


def sheet(records, samples, annotations, originals, output, total):
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 21) if Path(
        'C:/Windows/Fonts/segoeui.ttf').exists() else ImageFont.load_default(size=21)
    canvas = Image.new('RGB', (1700, 140 + 430*len(records)), '#faf8f2')
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 12), f'SEGMENTAZIONI PROPOSTE — {len(records)}/{total} schede con originali verificati; nessuna nuova decisione', font=font, fill='#26343b')
    draw.text((20, 47), 'Verde: mantenuto; rosso: escluso; arancio: incerto; blu: taglio. Nessuna autenticazione.', font=font, fill='#26343b')
    for n, sid in enumerate(records):
        sample, item = samples[sid], annotations[sid]
        original = verified_image(sample, originals)
        if original is None:
            raise ValueError('Selected original is unavailable')
        y = 100 + n*430
        draw.text((20, y), f'{sid} | folio {sample["folio"]} | pagina BNE {sample["page"]}', font=font, fill='#26343b')
        for x, label, view, scale in zip(
                [20, 230, 440, 650, 900],
                ['Originale RTL', 'Specchiato', 'Proposta', 'Mantenuto', 'Contesto'],
                views(original, sample, item), [6, 6, 6, 6, 2]):
            scale = max(1, min(scale, (200 if x < 900 else 780)//view.width, 245//view.height))
            draw.text((x, y+36), f'{label} {scale}x', font=font, fill='#26343b')
            resized = view.resize((view.width*scale, view.height*scale), Image.Resampling.NEAREST)
            canvas.paste(resized, (x, y+75), resized if resized.mode == 'RGBA' else None)
        for j, line in enumerate(textwrap.wrap(item['notes'], 140)[:4]):
            draw.text((20, y+321+j*24), line, font=font, fill='#26343b')
    draw.text((20, canvas.height-35), 'Imágenes procedentes de los fondos de la Biblioteca Nacional de España; MSS/8937; crop, specchiatura e annotazioni dichiarati.', font=font, fill='#26343b')
    buffer = io.BytesIO()
    canvas.save(buffer, format='PNG')
    data = buffer.getvalue()
    output = output.with_stem(output.stem+'-'+hashlib.sha256(data).hexdigest()[:12])
    review.guided.corpus.within(output, output.parent)
    output.write_bytes(data)
    return output


def revised_records(document, samples, annotations, root):
    if (document['status'] != 'candidate_segmentation_revisions'
            or document['source_plan'] != PLAN.as_posix()
            or document['source_plan_sha256'] != review.sha(Path(root)/PLAN)):
        raise ValueError('Revision must remain a candidate linked to the source plan')
    revised_samples, revised_annotations, selected = dict(samples), dict(annotations), []
    for row in document['samples']:
        sid = row['sample_id']
        if (sid not in annotations or sid in selected or row['human_decision'] is not None
                or row['based_on_annotation_sha256'] != annotation_sha(annotations[sid])
                or row['image_sha256'] != samples[sid]['image_sha256']
                or row['annotation']['sample_id'] != sid):
            raise ValueError('Revision source, identity or approval differs')
        x, y, w, h = row['mirror_crop']
        source = samples[sid]
        if (any(type(n) is not int for n in (x, y, w, h)) or min(x, y) < 0 or min(w, h) < 1
                or x+w > source['image_width'] or y+h > source['image_height']
                or row['raw_crop'] != [source['image_width']-x-w, y, w, h]):
            raise ValueError('Revision crop does not match original coordinates')
        for key, minimum in [('retained_polygons', 3), ('excluded_polygons', 3),
                             ('uncertain_polygons', 3), ('cut_lines', 2)]:
            for polygon in row['annotation'][key]:
                review.points(polygon, w, h, minimum)
        if not row['annotation']['retained_polygons'] or not row['annotation']['notes'].strip():
            raise ValueError('Revision needs retained regions and notes')
        cx, cy, cw, ch = source['mirror_context']
        left, top = max(0, min(cx, x-12)), max(0, min(cy, y-12))
        right, bottom = min(source['image_width'], max(cx+cw, x+w+12)), min(source['image_height'], max(cy+ch, y+h+12))
        context = [left, top, right-left, bottom-top]
        revised_samples[sid] = dict(source, mirror_crop=row['mirror_crop'], raw_crop=row['raw_crop'],
                                    mirror_context=context)
        revised_annotations[sid] = row['annotation']
        selected.append(sid)
    if not selected:
        raise ValueError('Revision selection is empty')
    return revised_samples, revised_annotations, selected


def recorded_revisions(root, samples, annotations):
    root = Path(root)
    decisions = {}
    for path in sorted((root/'data').glob('human_segmentation_revision_*.json')):
        receipt = json.loads(path.read_text(encoding='utf-8'))
        revision = review.guided.corpus.within(root/receipt['revision_path'], root/'data')
        if (receipt['status'] != 'human_segmentation_revision_decisions_recorded'
                or receipt['scope'] != 'segmentation_boundaries_only'
                or receipt['revision_sha256'] != review.sha(revision)
                or receipt['reviewer'] != 'Human review'
                or receipt['reading_changes'] is not False or receipt['design_changes'] is not False
                or receipt['authenticity_claim'] is not False
                or not receipt['quote'].strip() or not receipt['question'].strip()
                or datetime.fromisoformat(receipt['recorded_at']).tzinfo is None):
            raise ValueError('Revision receipt scope or checkpoint differs')
        document = json.loads(revision.read_text(encoding='utf-8'))
        _, revised, ids = revised_records(document, samples, annotations, root)
        shown = review.guided.corpus.within(root/receipt['shown_sheet'], root/'build')
        if shown.exists() and review.sha(shown) != receipt['shown_sheet_sha256']:
            raise ValueError('Shown revision sheet changed')
        if {r['sample_id'] for r in receipt['decisions']} != set(ids):
            raise ValueError('Revision receipt selection differs')
        for row in receipt['decisions']:
            sid = row['sample_id']
            if (sid in decisions or row['decision'] not in DECISIONS
                    or row['annotation_sha256'] != annotation_sha(revised[sid])
                    or row['uncertain_regions_approved'] is not False):
                raise ValueError('Revision decision differs from the proposal or expands approval')
            decisions[sid] = {'decision': row['decision'], 'revision_path': receipt['revision_path'],
                              'annotation_sha256': row['annotation_sha256']}
    return decisions


def prepare(root=ROOT, originals=None, letter=None, revisions=None):
    root = Path(root).resolve()
    manifest, samples, annotations = review.validate(root)
    decisions = recorded_decisions(root, annotations)
    revision_decisions = recorded_revisions(root, samples, annotations)
    delegated = delegated_decisions(root, samples, annotations, decisions)
    index = original_index(originals or root/'data/scans')
    if letter is not None and letter not in manifest['glyphs']:
        raise ValueError('Letter must belong to the thirteen approved designs')
    out = root/'build/segmentation-consolidation'
    if out.resolve() != out:
        raise ValueError('Review output cannot resolve through symlinks')
    out.mkdir(parents=True, exist_ok=True)
    review.guided.corpus.within(out/'audit.json', out)
    if letter is not None:
        review.guided.corpus.within(out/f'review-{letter}.png', out)
    audit = {'status': 'partially_reviewed' if decisions else 'pending_human_segmentation_review',
             'scope': 'Structural checks, image availability and separately recorded boundary decisions',
             'source_sha256': {p: review.sha(root/p) for p in
                               [str(review.MANIFEST), *manifest['segmentation_sha256']]},
             'samples': []}
    for sid, item in annotations.items():
        sample = samples[sid]
        image = verified_image(sample, index)
        audit['samples'].append({'sample_id': sid, 'character': sample['character'],
                                 'folio': sample['folio'], 'page': sample['page'],
                                 'image_sha256': sample['image_sha256'],
                                 'annotation_sha256': annotation_sha(item),
                                 'original_verified': image is not None,
                                 'uncertain_regions': len(item['uncertain_polygons']),
                                 'cut_lines': len(item['cut_lines']),
                                 'original_decision': decisions.get(sid),
                                 'revision': revision_decisions.get(sid),
                                 'human_decision': revision_decisions.get(sid, {}).get('decision', decisions.get(sid)),
                                 'agent_assessment': delegated.get(sid),
                                 'effective_decision': (delegated[sid]['decision'] if sid in delegated else
                                                        revision_decisions.get(sid, {}).get('decision', decisions.get(sid)))})
    audit['assessment_complete'] = all(r['effective_decision'] is not None for r in audit['samples'])
    (out/'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    rendered = None
    if letter is not None:
        selected = [r['sample_id'] for r in audit['samples']
                    if r['character'] == letter and r['original_verified']]
        if not selected:
            raise ValueError('No verified originals for the requested letter')
        total = len(manifest['glyphs'][letter]['sample_ids'])
        rendered = sheet(selected, samples, annotations, index, out/f'review-{letter}.png', total)
    elif revisions is not None:
        path = review.guided.corpus.within(root/revisions, root/'data')
        document = json.loads(path.read_text(encoding='utf-8'))
        revised_samples, revised_annotations, selected = revised_records(document, samples, annotations, root)
        if any(verified_image(revised_samples[sid], index) is None for sid in selected):
            raise ValueError('A revision original is unavailable')
        rendered = sheet(selected, revised_samples, revised_annotations, index,
                         out/'review-revisions.png', len(selected))
    return {'samples': len(annotations),
            'originals_verified': sum(r['original_verified'] for r in audit['samples']),
            'human_decisions': len(set(decisions) | set(revision_decisions)),
            'delegated_agent_decisions': len(delegated),
            'assessed_samples': len(set(decisions) | set(revision_decisions) | set(delegated)),
            'confirmed_revisions': len(revision_decisions), 'output': out.relative_to(root).as_posix(),
            'review_sheet': rendered.relative_to(root).as_posix() if rendered else None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--originals', type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--letter')
    selection.add_argument('--revisions', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(originals=args.originals, letter=args.letter, revisions=args.revisions)))
