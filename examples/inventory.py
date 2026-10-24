"""Hash the complete distributable tree; reject changed or unlisted files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from check_privacy import distributable_paths

ROOT = Path(__file__).resolve().parents[1]
SELF = {'MANIFEST.json', 'CONTENTS.txt'}
FONT_SHA256 = '1f65d26ece4c8a0fe9c275fcdedfa037fab88a9687b0cd89a941d131eb899632'
CANDIDATE_SHA256 = '0d10af2c358d9a4884e41d910cbcb789f1648073f43f048ac20eee0d5afe1201'


def file_records():
    records = {}
    for name in distributable_paths():
        if name in SELF:
            continue
        data = (ROOT / name).read_bytes()
        records[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                         'license': 'OFL-1.1' if name.startswith(('fonts/', 'glyphs/')) or name == 'OFL.txt' else 'MIT'}
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    manifest = ROOT / 'MANIFEST.json'
    current = file_records()
    names = sorted(set(current) | SELF)
    contents = '\n'.join(names) + '\n'
    if args.check:
        recorded = json.loads(manifest.read_text(encoding='utf-8'))
        if recorded['files'] != current or (ROOT / 'CONTENTS.txt').read_text(encoding='utf-8') != contents:
            raise SystemExit('Inventory differs: regenerate after reviewing intentional changes')
        print(json.dumps({'inventory_matches': True, 'files': len(names)}))
    else:
        recorded = {'project': 'Leonardus', 'version': '1.270', 'status': 'review_candidate',
                    'accepted_font_version': '1.100', 'accepted_font_sha256': FONT_SHA256,
                    'candidate_font_sha256': CANDIDATE_SHA256,
                    'candidate_font_file': 'fonts/Leonardus-Regular-1.270.ttf',
                    'public_release_approved': False,
                    'self_hashes_excluded': sorted(SELF), 'transformations': [
                        'Independent publication edition with new Git history; reader-facing README, installation guide, credits, documentation index, current-version HTML trial and preview added; preserved TTF, evidence and approval records unchanged',
                        'Selected source tree without prior Git history, original conversations or Office assets',
                        'Reviewer fields and decision attribution labels made generic; original quotes, dates and source coordinates preserved',
                        'Approval receipts contain only decisions needed by the compiler; release receipt hash updated coherently',
                        'Legacy metadata URL points to this project documentation; final TTF bytes unchanged',
                        'New specimens drawn from compiled font contours, without reading old PDF or Office content',
                        'Additional privacy checks, tests, inventory and CI; development dependencies for PDF generation and inspection',
                        'New lowercase candidates appended with unreviewed status; original evidence records and accepted font preserved; source images and visual review dossier remain ignored',
                        'Guided review plan pins candidate batches; exported annotations remain drafts and ignored; research follow-up records leads without promoting evidence or changing the accepted font',
                        'Explicit group m/t human review recorded separately and applied only to ten evidence review fields; source checkpoints and accepted font remain unchanged',
                        'Remaining six guided groups explicitly confirmed: 61 selected samples reviewed in total; only evidence review fields changed, with source checkpoints and accepted font preserved',
                        'Manual segmentation hypotheses and independent lowercase SVG proposals added with pending design review; manuscript images and uniquely named study fonts remain ignored; accepted font unchanged',
                        'Twelve primary lowercase designs approved with file hashes and advances pinned in a separate receipt; s revised with a designed lower curve and pending confirmation; segmentation and accepted Regular unchanged',
                        'All thirteen lowercase designs approved and integrated in Regular 1.100; dotless i and accented i/u follow approved bases; Regular 1.000 preserved and reproducible; historical segmentations remain hypotheses',
                        'Windows GDI selection verified byte-identical to Regular 1.100; Office application tests started but incomplete, with no native rendering or save/reopen success claimed; local test artifacts remain ignored',
                        'Native Word and PowerPoint 1.100 checks completed on four pages/slides at 12/18/36/72pt with save/reopen and native PDF exports; all 88 nonempty embedded glyph outlines match the current font, including sixteen revised forms; Office artifacts remain ignored',
                        'Prepublication review aligns documentation with 1.100, expands selective font/name/design screening and checks reachable history, Actions logs and GitHub security settings without changing font bytes or publication approval',
                        'All 61 segmentations assessed: 29 individual human reviews retained and 32 agent assessments under explicit user delegation; recovered originals remain ignored and historical readings unchanged',
                        'Regular 1.200 adds six reasoned contemporary completions with separate sources, derivation records and family name for trial; 1.100 and 1.000 checkpoints preserved; no new human visual design approval claimed',
                        'Separate unapproved OPQR A/B design studies compare 22 existing reviewed source localizations; eight SVG proposals and a font-outline word proof added; installed/distributed Regular and evidence registry unchanged; manuscript comparisons remain local',
                        'Human selection o B, p A, q B, r B integrated as a distinct Regular 1.210 candidate; o-grave composite and combining anchors realigned; all advances and prior checkpoints preserved; no new reading, boundary, authenticity or public-release approval inferred',
                        'Regular 1.211 changes only p/q horizontal origins and advances under explicit instruction; selected shapes preserved point-for-point up to translation; other glyphs and historical evidence unchanged; all 52-letter pairs checked at five raster sizes and word proofs inspected',
                        'Separate unapproved AEMNU A/B studies add ten original SVG proposals tied to 27 existing reviewed localizations, isolated-letter word comparisons and a documented unsuccessful search for newly acquired higher-detail targets; installed/distributed 1.211 and evidence registry remain unchanged; manuscript reproductions stay local',
                        'Human selection a A, e A, m B, n B, u B integrated as Regular 1.220; four accent composites and combining anchors realigned; prior OPQR shapes, p/q spacing and every advance preserved; evidence and all earlier font checkpoints unchanged; no new historical readings or higher-detail acquisition claimed',
                        'Separate unapproved JKVWXY A/B completion studies add twelve original SVG proposals compared with six existing candidate localizations and three K contexts without evidence promotion; additional e-Leo consultations remain research leads; isolated word comparisons and mixed previews preserve installed/distributed 1.220 and every advance; facsimiles remain local',
                        'Explicit human selection j A, k B, v B, w B, x B, y B integrated as Regular 1.230; six selected contours exact, every advance and previous AEMNU/OPQR/pq designs preserved; combining anchors updated; historical registry and reasoned-completion classifications retained; Windows installation and fresh-process GDI selection verified',
                        'Separate unapproved LAMNRS capital studies add twelve original SVG proposals compared with seven unresolved formal observations and four registered lowercase references; no new capital attestation or evidence promotion; isolated word/phrase and mixed comparisons preserve Regular 1.230, lowercase designs and all advances; source reproductions remain local',
                        'Explicit human selection L B, A B, M B, N A, R B, S B integrated as Regular 1.240; S B overrides the earlier agent preference; six selected contours exact, A-grave and combining anchors updated, every lowercase outline and advance preserved; capital classifications remain designed; current-user Windows installation and fresh-process GDI byte selection verified',
                        'Separate unapproved CDEGPT capital studies add twelve original SVG proposals, four unresolved formal observations and eight registered lowercase comparisons; corrected E and T context identifications documented; isolated word/phrase and mixed comparisons preserve installed Regular 1.240 and all prior selected forms; no new capital attestation or source-image distribution',
                        'Explicit human selection C B, D B, E A, G B, P B, T B integrated as Regular 1.250; E A, G B and P B override the earlier agent preferences; selected contours exact, E-grave/E-acute and combining anchors updated, earlier capitals, lowercase outlines and all advances preserved; historical classifications and evidence unchanged; current-user installation and fresh-process GDI byte selection verified',
                        'Separate unapproved BFHIOQ capital studies add twelve original SVG proposals compared with four unresolved initials and twelve existing reviewed lowercase references; words, phrases and mixed previews preserve installed/distributed Regular 1.250, all previously selected outlines and advances; no new capital attestation or manuscript-image distribution',
                        'Explicit human selection B B, F B, H B, I A, O B, Q B integrated as Regular 1.260; H B overrides the prior H A suggestion; six exact selected contours, I/O-grave composites and combining anchors updated; earlier twelve selected capitals, lowercase shapes and all advances preserved; current-user installation and fresh-process GDI byte selection verified',
                        'Separate unapproved JKUVWXYZ capital studies add sixteen original SVG proposals and compare six existing candidates, three case-unresolved K observations and four reviewed lowercase references without promotion; J and W remain declared modern completions; isolated words and mixed previews preserve installed Regular 1.260 and all advances; source images remain local',
                        'Explicit all-B JKUVWXYZ selection integrated as Regular 1.270; J/W/Y/Z B override prior A suggestions; eight exact contours and U-grave/combining anchors updated, eighteen earlier capitals, lowercase forms and every advance preserved; all 26 capitals match four disjoint human selections, with E/I/N A and 23 B; historical candidate states and declared J/W completions retained; current-user installation and fresh-process GDI byte selection verified',
                        'Native Word and PowerPoint 1.270 save/reopen checked at four point sizes; Word PDF outlines matched and protected PowerPoint PDF content confirmed by the project owner; reproducible A4 print specimen added without Office assets or manuscript images; physical print remains untested',
                        'Approved metadata-only naming of Regular 1.270 as family Leonardus and style Regular; version retained internally, all non-name tables and drawing preserved except the required head checksum; previous named integration checkpoint and native Office evidence retained, final download and Windows installation point to the newly named TTF',
                        'Leonardus Specchio RTL 1.270 added as a reproducible mirror-image derivation of Regular 1.270 under a distinct family name; outlines and mark anchors reflected, Bidi_Mirrored glyphs left to bidi mirroring, advances and repertoire preserved; no new design, reading or approval, and Regular 1.270 and every checkpoint unchanged',
                    ], 'files': current}
        manifest.write_text(json.dumps(recorded, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        (ROOT / 'CONTENTS.txt').write_text(contents, encoding='utf-8', newline='\n')
        print(json.dumps({'inventory_written': True, 'files': len(names)}))
