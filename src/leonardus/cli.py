"""Font engineering and local manual-evidence commands."""
import argparse
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from .fontbuild import build_font
from .preview import make_preview
from .prepare import prepare_scan
from .charset import audit_charset
from .comparison import make_comparison
from .evidence import register_source, annotate_sample, review_sample, validate_evidence
from .proposal import build_proposal
from .specimen import make_specimens
from .regular import build_regular
from .release import build_release


def audit_font(path: Path):
    with TTFont(str(path)) as f:
        c = f.getBestCmap()
        glyf = f["glyf"]
        off_curve = 0
        simple = 0
        for name in glyf.keys():
            g = glyf[name]
            if g.numberOfContours > 0:
                simple += 1
                coords, end_pts, flags = g.getCoordinates(glyf)
                off_curve += sum(not (flag & 1) for flag in flags)
        bounds = {name: [getattr(glyf[name], key, 0) for key in ("xMin", "yMin", "xMax", "yMax")]
                  for name in f.getGlyphOrder()}
        vertical = {"hhea": [f["hhea"].ascent, f["hhea"].descent],
                    "typo": [f["OS/2"].sTypoAscender, f["OS/2"].sTypoDescender],
                    "win": [f["OS/2"].usWinAscent, -f["OS/2"].usWinDescent]}
        contained = all(b[3] <= min(v[0] for v in vertical.values())
                        and b[1] >= max(v[1] for v in vertical.values()) for b in bounds.values())
        return {"font": str(path), "glyphs": len(f.getGlyphOrder()),
                "mapped_codepoints": len(c), "simple_glyphs": simple,
                "off_curve_control_points": off_curve,
                "has_true_type_outlines": "glyf" in f,
                "codepoints": [f"U+{code:04X}" for code in sorted(c)],
                "family": f["name"].getDebugName(1), "postscript_name": f["name"].getDebugName(6),
                "glyph_bounds": bounds, "vertical_metrics": vertical,
                "bounds_within_vertical_metrics": contained,
                "contours": {name: glyf[name].numberOfContours for name in f.getGlyphOrder()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Leonardus Lab: reproducible typography pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Compile filled SVG outlines into a TTF font")
    b.add_argument("--glyphs", type=Path, default=Path("glyphs/demo"))
    b.add_argument("--out", type=Path, default=Path("dist/Leonardus-EngineeringDemo.ttf"))
    b.add_argument("--family", default="Leonardus Lab Demo")
    bp = sub.add_parser("build-proposal", help="Compile the explicitly unapproved seven-letter V3 pilot")
    bp.add_argument("--glyphs", type=Path, default=Path("glyphs/proposals/2026-10-11-v3"))
    bp.add_argument("--out", type=Path, default=Path("dist/pilot/Leonardus-ProposalV3-Unapproved.ttf"))
    bp.add_argument("--sources", type=Path, default=Path("data/source_registry.csv"))
    bp.add_argument("--evidence", type=Path, default=Path("data/glyph_evidence.csv"))
    br = sub.add_parser("build-regular", help="Compile the versioned contemporary Regular alpha after M2")
    br.add_argument("--glyphs", type=Path, default=Path("glyphs/regular/alpha-0.200"))
    br.add_argument("--out", type=Path, default=Path("dist/regular/Leonardus-Alpha0200-Regular.ttf"))
    release = sub.add_parser("build-release", help="Compile versioned Regular with OFL and Windows metadata")
    release.add_argument("--version", choices=('1.000', '1.100', '1.200', '1.210', '1.211', '1.220', '1.230', '1.240', '1.250', '1.260', '1.270'), default='1.100')
    release.add_argument("--out", type=Path)
    p = sub.add_parser("preview", help="Proof image rendered using the generated TTF")
    p.add_argument("--font", type=Path, default=Path("dist/Leonardus-EngineeringDemo.ttf"))
    p.add_argument("--out", type=Path, default=Path("dist/Leonardus-Preview.png"))
    p.add_argument("--text", default="Leonardo")
    sp = sub.add_parser("specimen", help="Render four explicit point sizes from the unapproved pilot TTF")
    sp.add_argument("--font", type=Path, default=Path("dist/pilot/Leonardus-ProposalV3-Unapproved.ttf"))
    sp.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("prepare", help="Enhance / mirror a locally sourced manuscript image")
    s.add_argument("--input", required=True, type=Path)
    s.add_argument("--output", required=True, type=Path)
    s.add_argument("--mirror", action="store_true")
    s.add_argument("--contrast", type=float, default=1.4)
    a = sub.add_parser("audit", help="Inspect TTF structure and quadratic off-curve control points")
    a.add_argument("--font", required=True, type=Path)
    ch = sub.add_parser("charset", help="Validate proposed Unicode repertoire and optional font cmap")
    ch.add_argument("--manifest", type=Path, default=Path("data/charset_regular_v1.json"))
    ch.add_argument("--font", type=Path)
    source = sub.add_parser("source", help="Record a source and declared local-use conditions")
    source.add_argument("--registry", type=Path, default=Path("data/source_registry.csv"))
    source.add_argument("--id", required=True)
    source.add_argument("--institution", required=True)
    source.add_argument("--manuscript", required=True)
    source.add_argument("--url", required=True)
    source.add_argument("--period", default="")
    source.add_argument("--kind", choices=("historical", "synthetic"), default="historical")
    source.add_argument("--rights", choices=("UNVERIFIED", "PERMITTED_LOCAL", "RESTRICTED", "SELF_CREATED"),
                        default="UNVERIFIED")
    source.add_argument("--rights-basis", default="")
    source.add_argument("--permitted-use", action="append", default=[],
                        choices=("local_study", "processing", "private_comparison"))
    source.add_argument("--notes", default="")
    source.add_argument("--update", action="store_true")
    annotation = sub.add_parser("annotate", help="Record a candidate crop on immutable raw source pixels")
    annotation.add_argument("--id", required=True)
    annotation.add_argument("--character", required=True)
    annotation.add_argument("--source", required=True)
    annotation.add_argument("--folio", required=True)
    annotation.add_argument("--image-id", required=True)
    annotation.add_argument("--image", required=True, type=Path)
    annotation.add_argument("--crop", type=int, nargs=4, required=True,
                            metavar=("X", "Y", "WIDTH", "HEIGHT"))
    annotation.add_argument("--direction", required=True, choices=("rtl", "ltr", "unknown"))
    annotation.add_argument("--mirror", action="store_true")
    annotation.add_argument("--rotation", type=int, choices=(0, 90, 180, 270), default=0)
    annotation.add_argument("--confidence", type=float, default=0.0)
    annotation.add_argument("--attribution", required=True)
    annotation.add_argument("--notes", default="")
    annotation.add_argument("--update", action="store_true")
    review = sub.add_parser("review", help="Record an explicit manual review, without authentication claims")
    review.add_argument("--id", required=True)
    review.add_argument("--status", required=True, choices=("reviewed", "rejected"))
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", required=True)
    validation = sub.add_parser("validate-evidence", help="Validate source/sample records, optionally checking images")
    validation.add_argument("--check-images", action="store_true")
    comparison = sub.add_parser("compare", help="Render 4-10 local samples with original/transformed views")
    comparison.add_argument("--character", required=True)
    comparison.add_argument("--ids", nargs="+")
    comparison.add_argument("--out", required=True, type=Path)
    for command in (annotation, review, validation, comparison):
        command.add_argument("--sources", type=Path, default=Path("data/source_registry.csv"))
        command.add_argument("--evidence", type=Path, default=Path("data/glyph_evidence.csv"))
    args = parser.parse_args(argv)
    try:
        if args.cmd == "build":
            result = build_font(args.glyphs, args.out, args.family)
        elif args.cmd == "build-proposal":
            result = build_proposal(args.glyphs, args.out, args.sources, args.evidence)
        elif args.cmd == "build-regular":
            result = build_regular(args.glyphs, args.out)
        elif args.cmd == "build-release":
            output = args.out or Path(f'dist/release/{args.version}/Leonardus-Regular.ttf')
            result = build_release(output, version=args.version)
        elif args.cmd == "preview":
            result = {"preview_file": make_preview(args.font, args.out, args.text)}
        elif args.cmd == "specimen":
            result = make_specimens(args.font, args.out)
        elif args.cmd == "prepare":
            result = {"prepared_image": prepare_scan(args.input, args.output, args.mirror, args.contrast)}
        elif args.cmd == "audit":
            result = audit_font(args.font)
        elif args.cmd == "charset":
            result = audit_charset(args.manifest, args.font)
        elif args.cmd == "source":
            result = register_source(args.registry, source_id=args.id, institution=args.institution,
                                     manuscript=args.manuscript, url=args.url, period=args.period,
                                     rights_status=args.rights, source_kind=args.kind,
                                     rights_basis=args.rights_basis, permitted_uses=args.permitted_use,
                                     notes=args.notes, update=args.update)
        elif args.cmd == "annotate":
            result = annotate_sample(args.sources, args.evidence, sample_id=args.id,
                                     target_character=args.character, source_id=args.source,
                                     folio=args.folio, source_image_id=args.image_id, image=args.image,
                                     crop=tuple(args.crop), original_direction=args.direction,
                                     attribution=args.attribution, mirror_applied=args.mirror,
                                     rotation_degrees=args.rotation,
                                     transcription_confidence=args.confidence,
                                     designer_notes=args.notes, update=args.update)
        elif args.cmd == "review":
            result = review_sample(args.sources, args.evidence, sample_id=args.id,
                                   status=args.status, reviewer=args.reviewer, notes=args.notes)
        elif args.cmd == "validate-evidence":
            result = validate_evidence(args.sources, args.evidence, args.check_images)
        else:
            result = make_comparison(args.sources, args.evidence, args.out, args.character, args.ids)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    # ASCII JSON remains valid on Windows consoles that cannot encode combining marks.
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result


if __name__ == "__main__":
    main()
