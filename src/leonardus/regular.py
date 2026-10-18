"""Versioned Regular alpha compiler with explicit provenance and accent shaping."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from .charset import audit_charset
from .evidence import validated_samples
from .fontbuild import _blank_glyph, _build_timestamp, _notdef_glyph, _svg_to_glyph
from .proposal import text_sha256

FAMILY = "Leonardus Alpha 0200"
POSTSCRIPT = "LeonardusLab-Alpha0200-Regular"


def validate_regular(directory: Path, root: Path) -> dict:
    manifest = json.loads((directory / "design_manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("schema_version") != 1 or manifest.get("status") != "regular_alpha"
            or manifest.get("version") != "0.200" or manifest.get("policy") != "A"
            or manifest.get("direction") != "ltr"):
        raise ValueError("Expected versioned policy-A Regular alpha 0.200")
    human = json.loads((root / manifest["human_gate_receipt"]).read_text(encoding="utf-8"))
    if (human.get("status") != "human_decisions_recorded" or human.get("M2", {}).get("policy") != "A"
            or human.get("M2", {}).get("quote") != "Approvo il pacchetto M2 con politica A"):
        raise ValueError("M2 policy-A human gate receipt required")
    repertoire = root / manifest["repertoire"]
    charset = audit_charset(repertoire)
    if charset["status"] != "agreed" or text_sha256(repertoire) != manifest["repertoire_sha256"]:
        raise ValueError("Agreed repertoire hash differs")
    required = {int(cp[2:],16) for cp in charset["required_codepoints"]}
    records = manifest["glyphs"]
    mapped = [r["codepoint"] for r in records.values() if r["codepoint"] is not None]
    if len(mapped) != len(set(mapped)) or set(mapped) != required:
        raise ValueError("Manifest codepoints must exactly match agreed repertoire")
    rows = {r["sample_id"]: r for r in validated_samples(root / "data/source_registry.csv", root / "data/glyph_evidence.csv")}
    for char in "adelnor":
        if sum(r['target_character'] == char and r['review_status'] == 'reviewed'
               and r['source_kind'] == 'historical' for r in rows.values()) < 5:
            raise ValueError("M1B requires at least five reviewed letters per pilot character")
    if {r['codepoint'] for r in records.values() if r['classification'] == 'normalized'} != set(map(ord,'adelnor')):
        raise ValueError("The seven selected V3 forms must retain normalized provenance")
    expected_svg = {r["file"] for r in records.values() if "file" in r}
    if {p.name for p in directory.glob("*.svg")} != expected_svg:
        raise ValueError("SVG file inventory differs from manifest")
    for name, record in records.items():
        cp = record["codepoint"]
        if name != (f"uni{cp:04X}" if cp is not None else "dotlessi"):
            raise ValueError("Unicode glyph name mismatch")
        kind = record["classification"]
        ids = record.get("sample_ids", [])
        if kind == "normalized":
            if not ids or len(set(ids)) != len(ids) or record.get("display_anchor") not in ids:
                raise ValueError("Normalized glyph needs reviewed evidence and an anchor")
            if any(sid not in rows or rows[sid]["review_status"] != "reviewed"
                   or rows[sid]["source_kind"] != "historical" or rows[sid]["target_character"] != chr(cp)
                   or rows[sid]["folio"] not in human["foliation"]["mapping"].values() for sid in ids):
                raise ValueError("Normalized glyph requires reviewed historical letters on verified working folios")
            if text_sha256(root / record["legacy_source"]) != record["svg_sha256"]:
                raise ValueError("Selected V3 contour lineage differs")
        elif kind not in {"designed", "system"} or ids:
            raise ValueError("Completion/system glyph cannot claim historical evidence")
        if not record.get("design_notes"):
            raise ValueError("Every glyph requires design notes")
        if type(record["advance"]) is not int or not 0 <= record["advance"] <= 1500:
            raise ValueError("Invalid advance")
        if (record["advance"] == 0) != (cp in {0x0300,0x0301}):
            raise ValueError("Only combining marks have zero advance")
        if "file" in record:
            file = directory / record["file"]
            if file.parent.resolve() != directory.resolve() or text_sha256(file) != record["svg_sha256"]:
                raise ValueError("SVG path/hash differs")
            glyph = _svg_to_glyph(file)
            glyph.recalcBounds(None)
            if (glyph.numberOfContours <= 0 or glyph.numberOfContours != record["contours"]
                    or [glyph.xMin,glyph.yMin,glyph.xMax,glyph.yMax] != record["bounds"]):
                raise ValueError("Invalid recorded contours/bounds")
        elif "components" in record:
            if kind != "designed" or len(record["components"]) != 2:
                raise ValueError("Expected contemporary base/accent composite")
            for component in record["components"]:
                target = records.get(component["glyph"], {})
                if "file" not in target or len(component["offset"]) != 2 or any(type(x) is not int for x in component["offset"]):
                    raise ValueError("Composite requires existing simple glyphs and integer offsets")
        elif kind != "system" or cp not in {32,160}:
            raise ValueError("Only technical spaces may have no contours")
    return manifest


def accent_features(records: dict) -> str:
    lines = ["languagesystem DFLT dflt;", "languagesystem latn dflt;",
             "markClass uni0300 <anchor 0 0> @ACCENT;",
             "markClass uni0301 <anchor 0 0> @ACCENT;",
             "feature ccmp { sub uni0069' [uni0300 uni0301] by dotlessi; } ccmp;",
             "feature mark {"]
    for name, record in records.items():
        cp = record["codepoint"]
        if "bounds" not in record or (name != "dotlessi" and (cp is None or not chr(cp).isalpha())):
            continue
        xmin,ymin,xmax,ymax = record["bounds"]
        lower = name == "dotlessi" or chr(cp).islower()
        x = round((xmin+xmax)/2 + (35 if lower else 20))
        y = ymax + 60
        lines.append(f"pos base {name} <anchor {x} {y}> mark @ACCENT;")
    lines.append("} mark;")
    return "\n".join(lines)


def build_regular(directory: Path, output: Path, root: Path = Path('.')) -> dict:
    directory,output,root = Path(directory),Path(output),Path(root)
    manifest = validate_regular(directory,root)
    if output.exists():
        with TTFont(output) as old:
            if old["name"].getDebugName(6) != POSTSCRIPT:
                raise ValueError("Cannot overwrite a font from another version/category")
    records = manifest['glyphs']
    glyphs = {'.notdef':_notdef_glyph()}
    for name,r in records.items():
        if 'file' in r:
            glyphs[name] = _svg_to_glyph(directory/r['file'])
        elif r['classification'] == 'system':
            glyphs[name] = _blank_glyph()
    for name,r in records.items():
        if 'components' in r:
            pen = TTGlyphPen(glyphs)
            for part in r['components']:
                pen.addComponent(part['glyph'],(1,0,0,1,*part['offset']))
            glyphs[name] = pen.glyph()
    order = ['.notdef']+sorted(records)
    builder = FontBuilder(1000,isTTF=True)
    # Keep the binary independent of optional QA packages: fontTools otherwise
    # changes layout-table packing when uharfbuzz happens to be installed.
    builder.font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
    builder.font['head'].created = builder.font['head'].modified = _build_timestamp()
    builder.font.recalcTimestamp = False
    builder.font['head'].fontRevision = 0.200
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap({r['codepoint']:name for name,r in records.items() if r['codepoint'] is not None})
    builder.setupGlyf(glyphs)
    glyf = builder.font['glyf']
    for glyph in glyphs.values():
        glyph.recalcBounds(glyf)
    metrics = {name:(r['advance'],getattr(glyphs[name],'xMin',0)) for name,r in records.items()}
    metrics['.notdef'] = (600,80)
    builder.setupHorizontalMetrics(metrics)
    ascent = max(900,max(getattr(g,'yMax',0) for g in glyphs.values())+70)
    descent = min(-250,min(getattr(g,'yMin',0) for g in glyphs.values())-70)
    builder.setupHorizontalHeader(ascent=ascent,descent=descent,lineGap=0)
    builder.setupNameTable({
        'familyName':FAMILY,'styleName':'Regular','fullName':FAMILY+' Regular',
        'psName':POSTSCRIPT,'uniqueFontIdentifier':'LeonardusLab:Alpha0200:Regular',
        'version':'Version 0.200; contemporary Regular alpha; private trial',
        'designer':'Leonardus Lab; independent project outlines with agent assistance',
        'description':'Contemporary LTR reinterpretation. Seven normalized V3 letterforms linked to reviewed BNE samples; remaining forms are designed completions. NOT authenticated handwriting or signature. Full alpha visual and Office QA pending.',
        'licenseDescription':'Private project trial. Final font license pending human decision. Code MIT; BNE reproductions separately CC BY 4.0. No museum endorsement.',
        'copyright':'Original Leonardus Lab outlines. References: BNE MSS/8937, 1r-4r. Imágenes procedentes de los fondos de la Biblioteca Nacional de España. https://creativecommons.org/licenses/by/4.0/ https://bnedigital.bne.es/bd/card?oid=0000040157&site=bdh',
    })
    builder.setupOS2(sTypoAscender=ascent,sTypoDescender=descent,sTypoLineGap=0,
                     usWinAscent=ascent,usWinDescent=-descent,sxHeight=360,sCapHeight=650,
                     fsType=0x0002,fsSelection=0x0040)
    builder.setupPost()
    builder.setupDummyDSIG()
    addOpenTypeFeaturesFromString(builder.font,accent_features(records))
    output.parent.mkdir(parents=True,exist_ok=True)
    builder.save(str(output))
    coverage = audit_charset(root/manifest['repertoire'],output)
    with TTFont(output) as font:
        if not coverage['coverage_complete'] or len(font.getBestCmap()) != 119:
            raise ValueError('Compiled font coverage differs')
        if any(font['glyf'][name].numberOfContours == 0 and cp not in {32,160} for cp,name in font.getBestCmap().items()):
            raise ValueError('Mapped nonspace glyph is empty')
    return {'file':str(output),'status':'regular_alpha','version':'0.200','family':FAMILY,
            'codepoints':119,'glyphs':len(order),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'accent_features':['ccmp','mark'],'license':'Private trial; final decision pending; embedding restricted'}
