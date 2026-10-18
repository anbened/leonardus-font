"""Local, manually reviewed sample metadata; never historical authentication."""
from __future__ import annotations

import csv
import hashlib
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from .prepare import assert_distinct_files

SOURCE_FIELDS = [
    "source_id", "institution", "manuscript", "url", "period", "rights_status",
    "local_path", "notes", "source_kind", "rights_basis", "permitted_uses",
]
SAMPLE_FIELDS = [
    "sample_id", "target_character", "source_id", "folio", "source_url",
    "source_local_path", "crop_x", "crop_y", "crop_width", "crop_height",
    "mirror_applied", "rights_status", "attribution", "review_status",
    "transcription_confidence", "designer_notes", "source_kind",
    "source_image_id", "image_width", "image_height", "image_sha256",
    "original_direction", "rotation_degrees", "rights_basis", "permitted_uses",
    "reviewer", "review_notes", "reviewed_at",
]
USES = {"local_study", "processing", "private_comparison"}
RIGHTS = {"UNVERIFIED", "PERMITTED_LOCAL", "RESTRICTED", "SELF_CREATED"}


def _read_csv(path: Path, fields: list[str], legacy_count: int) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames or []
        if (len(header) != len(set(header)) or
                not set(fields[:legacy_count]).issubset(header) or
                set(header) - set(fields)):
            raise ValueError(f"Unsupported CSV header: {path}")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Malformed CSV row: {path}")
            rows.append({name: row.get(name, "") for name in fields})
    return rows


def _write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _identifier(value: str, field: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError(f"Invalid {field}: {value!r}")


def _character(value: str) -> None:
    if len(value) != 1 or 0xD800 <= ord(value) <= 0xDFFF:
        raise ValueError("target_character must be one Unicode scalar")


def _permissions(row: dict, required: set[str]) -> None:
    if row["rights_status"] not in {"SELF_CREATED", "PERMITTED_LOCAL"}:
        raise ValueError(f"Local use not documented for {row['source_id']}")
    if not required.issubset(set(row["permitted_uses"].split("|"))):
        raise ValueError(f"Missing permitted uses for {row['source_id']}: {sorted(required)}")


def _sources(path: Path) -> dict[str, dict]:
    result = {}
    for row in _read_csv(path, SOURCE_FIELDS, 8):
        _identifier(row["source_id"], "source_id")
        row["source_kind"] = row["source_kind"] or "historical"
        if row["source_id"] in result:
            raise ValueError(f"Duplicate source_id: {row['source_id']}")
        if not row["institution"].strip() or not row["manuscript"].strip():
            raise ValueError("Source institution and manuscript/description are required")
        if row["source_kind"] not in {"historical", "synthetic"}:
            raise ValueError("source_kind must be historical or synthetic")
        if row["rights_status"] not in RIGHTS:
            raise ValueError("Invalid rights_status")
        if row["rights_status"] == "SELF_CREATED" and row["source_kind"] != "synthetic":
            raise ValueError("SELF_CREATED is only valid for synthetic sources")
        url = urlparse(row["url"])
        if row["source_kind"] == "historical":
            if url.scheme not in {"http", "https"} or not url.netloc:
                raise ValueError("Historical sources require an HTTP(S) source URL")
        elif not row["url"].strip():
            raise ValueError("Synthetic sources require an identifying URL or URN")
        uses = row["permitted_uses"].split("|") if row["permitted_uses"] else []
        if len(uses) != len(set(uses)) or set(uses) - USES:
            raise ValueError("Invalid or duplicate permitted_uses")
        if row["rights_status"] in {"PERMITTED_LOCAL", "SELF_CREATED"}:
            if not row["rights_basis"].strip():
                raise ValueError("Document the basis for permitted local use")
        elif uses:
            raise ValueError("Unverified/restricted sources cannot declare permitted uses")
        result[row["source_id"]] = row
    return result


def register_source(sources_path: Path, *, source_id: str, institution: str,
                    manuscript: str, url: str, rights_status: str = "UNVERIFIED",
                    source_kind: str = "historical", rights_basis: str = "",
                    permitted_uses: list[str] | None = None, period: str = "",
                    notes: str = "", update: bool = False) -> dict:
    """Record a user's rights declaration, not a legal permission grant."""
    sources_path = Path(sources_path).resolve()
    sources = _sources(sources_path)
    exists = source_id in sources
    if exists != update:
        raise ValueError("Source already exists; use --update" if exists else
                         "Cannot update an unknown source")
    row = dict.fromkeys(SOURCE_FIELDS, "")
    row.update(source_id=source_id, institution=institution, manuscript=manuscript,
               url=url, rights_status=rights_status, source_kind=source_kind,
               rights_basis=rights_basis, permitted_uses="|".join(permitted_uses or []),
               period=period, notes=notes)
    if exists:
        row["local_path"] = sources[source_id]["local_path"]
    # Validate without touching the user's registry on failure.
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory) / "sources.csv"
        _write_csv(candidate, SOURCE_FIELDS, [*[
            value for key, value in sources.items() if key != source_id], row])
        validated = _sources(candidate)
    _write_csv(sources_path, SOURCE_FIELDS, list(validated.values()))
    return row


def image_path(evidence_path: Path, sample: dict) -> Path:
    return (Path(evidence_path).resolve().parent / sample["source_local_path"]).resolve()


def _image_metadata(path: Path) -> tuple[int, int, str]:
    before = _digest(path)
    with Image.open(path) as image:
        width, height = image.size  # raw pixels; deliberately no EXIF transpose
        image.load()
    if before != _digest(path):
        raise ValueError("Source image changed during inspection")
    return width, height, before


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_sample(row: dict, source: dict, evidence_path: Path,
                     check_images: bool) -> None:
    _identifier(row["sample_id"], "sample_id")
    _character(row["target_character"])
    for field in ("source_url", "source_local_path", "source_image_id", "attribution"):
        if not row[field].strip():
            raise ValueError(f"Missing {field} for {row['sample_id']}")
    if not re.fullmatch(r"\S+(?:\s+)?(?:recto|verso|[rv])", row["folio"]):
        raise ValueError("folio must identify a leaf and recto/verso (e.g. 12r or 12 recto)")
    for field in ("rights_status", "source_kind", "rights_basis", "permitted_uses"):
        if row[field] != source[field]:
            raise ValueError(f"Stale source metadata ({field}) for {row['sample_id']}")
    if row["source_url"] != source["url"]:
        raise ValueError(f"Stale source URL for {row['sample_id']}")
    _permissions(source, {"local_study", "processing"})
    if row["original_direction"] not in {"rtl", "ltr", "unknown"}:
        raise ValueError("Invalid original_direction")
    if row["mirror_applied"] not in {"true", "false"}:
        raise ValueError("mirror_applied must be true or false")
    if row["rotation_degrees"] not in {"0", "90", "180", "270"}:
        raise ValueError("rotation_degrees must be 0, 90, 180 or 270")
    try:
        confidence = float(row["transcription_confidence"])
        dimensions = [int(row[key]) for key in (
            "image_width", "image_height", "crop_x", "crop_y", "crop_width", "crop_height")]
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid numeric sample metadata") from exc
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("transcription_confidence must be finite, between 0 and 1")
    width, height, x, y, crop_width, crop_height = dimensions
    if (width <= 0 or height <= 0 or x < 0 or y < 0 or crop_width <= 0 or
            crop_height <= 0 or x + crop_width > width or y + crop_height > height):
        raise ValueError("Crop must be inside the original image")
    if not re.fullmatch(r"[0-9a-f]{64}", row["image_sha256"]):
        raise ValueError("Missing or invalid source SHA256")
    if row["review_status"] not in {"candidate", "reviewed", "rejected"}:
        raise ValueError("Invalid review_status")
    review_fields = ("reviewer", "review_notes", "reviewed_at")
    if row["review_status"] == "candidate":
        if any(row[key] for key in review_fields):
            raise ValueError("Candidate samples cannot retain previous review metadata")
    else:
        if not all(row[key].strip() for key in review_fields):
            raise ValueError("Reviewed/rejected samples require reviewer, notes and date")
        try:
            if datetime.fromisoformat(row["reviewed_at"]).tzinfo is None:
                raise ValueError("Review date needs a timezone")
        except ValueError as exc:
            raise ValueError("Invalid review date") from exc
    if check_images:
        actual = _image_metadata(image_path(evidence_path, row))
        if actual != (width, height, row["image_sha256"]):
            raise ValueError(f"Original image changed: {row['sample_id']}")


def validated_samples(sources_path: Path, evidence_path: Path,
                      check_images: bool = False) -> list[dict[str, str]]:
    sources_path, evidence_path = Path(sources_path).resolve(), Path(evidence_path).resolve()
    assert_distinct_files(sources_path, evidence_path)
    sources = _sources(sources_path)
    rows = _read_csv(evidence_path, SAMPLE_FIELDS, 16)
    seen = set()
    images = {}
    for row in rows:
        if row["sample_id"] in seen:
            raise ValueError(f"Duplicate sample_id: {row['sample_id']}")
        seen.add(row["sample_id"])
        if row["source_id"] not in sources:
            raise ValueError(f"Unknown source_id: {row['source_id']}")
        _validate_sample(row, sources[row["source_id"]], evidence_path, check_images)
        identity = (row["source_id"], row["source_image_id"])
        image_metadata = tuple(row[key] for key in ("image_width", "image_height", "image_sha256", "folio"))
        if identity in images and images[identity] != image_metadata:
            raise ValueError(f"Conflicting source image identity: {identity}")
        images[identity] = image_metadata
    return rows


def annotate_sample(sources_path: Path, evidence_path: Path, *, sample_id: str,
                    target_character: str, source_id: str, folio: str,
                    source_image_id: str, image: Path, crop: tuple[int, int, int, int],
                    original_direction: str, attribution: str,
                    mirror_applied: bool = False, rotation_degrees: int = 0,
                    transcription_confidence: float = 0.0, designer_notes: str = "",
                    update: bool = False) -> dict:
    sources_path, evidence_path = Path(sources_path).resolve(), Path(evidence_path).resolve()
    assert_distinct_files(sources_path, evidence_path)
    sources = _sources(sources_path)
    if source_id not in sources:
        raise ValueError(f"Unknown source_id: {source_id}")
    source = sources[source_id]
    _permissions(source, {"local_study", "processing"})
    # Preserve other rows, including stale rights snapshots, so that an explicit
    # update can repair them one at a time after a source declaration changes.
    rows = _read_csv(evidence_path, SAMPLE_FIELDS, 16)
    ids = [row["sample_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate sample_id in registry")
    old = next((row for row in rows if row["sample_id"] == sample_id), None)
    if (old is not None) != update:
        raise ValueError("Sample already exists; use --update" if old is not None else
                         "Cannot update an unknown sample")
    if old is not None:
        expected = (int(old["image_width"]), int(old["image_height"]), old["image_sha256"])
        if _image_metadata(image_path(evidence_path, old)) != expected:
            raise ValueError("Original image changed; an update cannot replace its recorded hash")
    image = Path(image).resolve()
    for protected in [sources_path, evidence_path]:
        assert_distinct_files(image, protected)
    # Protect all originals already referenced by this registry, including aliases.
    for row in rows:
        assert_distinct_files(image_path(evidence_path, row), evidence_path)
        assert_distinct_files(image_path(evidence_path, row), sources_path)
    width, height, digest = _image_metadata(image)
    try:
        local_path = os.path.relpath(image, Path(evidence_path).resolve().parent)
    except ValueError:  # Windows paths on different drives
        local_path = str(image)
    if len(crop) != 4 or any(type(value) is not int for value in crop):
        raise ValueError("crop requires four integers: x y width height")
    if type(mirror_applied) is not bool or type(rotation_degrees) is not int:
        raise ValueError("Invalid transformation types")
    row = dict.fromkeys(SAMPLE_FIELDS, "")
    row.update(sample_id=sample_id, target_character=target_character,
               source_id=source_id, folio=folio, source_url=source["url"],
               source_local_path=local_path, source_image_id=source_image_id,
               crop_x=str(crop[0]), crop_y=str(crop[1]), crop_width=str(crop[2]),
               crop_height=str(crop[3]), mirror_applied=str(mirror_applied).lower(),
               image_width=str(width), image_height=str(height), image_sha256=digest,
               original_direction=original_direction, rotation_degrees=str(rotation_degrees),
               attribution=attribution, review_status="candidate",
               transcription_confidence=str(transcription_confidence), designer_notes=designer_notes)
    for field in ("rights_status", "source_kind", "rights_basis", "permitted_uses"):
        row[field] = source[field]
    _validate_sample(row, source, evidence_path, True)
    for item in rows:
        if (item["sample_id"] != sample_id and item["source_id"] == source_id and
                item["source_image_id"] == source_image_id and
                any(item[key] != row[key] for key in (
                    "image_width", "image_height", "image_sha256", "folio"))):
            raise ValueError("Conflicting source image identity")
    updated = [row if item["sample_id"] == sample_id else item for item in rows]
    if old is None:
        updated.append(row)
    _write_csv(evidence_path, SAMPLE_FIELDS, updated)
    return row


def review_sample(sources_path: Path, evidence_path: Path, *, sample_id: str,
                  status: str, reviewer: str, notes: str) -> dict:
    sources_path, evidence_path = Path(sources_path).resolve(), Path(evidence_path).resolve()
    if status not in {"reviewed", "rejected"}:
        raise ValueError("Review status must be reviewed or rejected")
    if not reviewer.strip() or not notes.strip():
        raise ValueError("A reviewer and review notes are required")
    rows = validated_samples(sources_path, evidence_path, check_images=True)
    row = next((row for row in rows if row["sample_id"] == sample_id), None)
    if row is None:
        raise ValueError(f"Unknown sample_id: {sample_id}")
    for item in rows:
        for target in (sources_path, evidence_path):
            assert_distinct_files(image_path(evidence_path, item), target)
    row.update(review_status=status, reviewer=reviewer, review_notes=notes,
               reviewed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    _write_csv(evidence_path, SAMPLE_FIELDS, rows)
    return row


def validate_evidence(sources_path: Path, evidence_path: Path,
                      check_images: bool = False) -> dict:
    rows = validated_samples(sources_path, evidence_path, check_images)
    return {"sources": len(_sources(sources_path)), "samples": len(rows),
            "historical_samples": sum(row["source_kind"] == "historical" for row in rows),
            "synthetic_samples": sum(row["source_kind"] == "synthetic" for row in rows),
            "reviewed_samples": sum(row["review_status"] == "reviewed" for row in rows),
            "images_checked": check_images,
            "note": "Metadata validation does not authenticate handwriting or grant usage rights."}
