"""Check distributable files and decoded document metadata without printing values."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'profile_path': re.compile(r'(?i)\b[A-Z]:[/\\]+Users[/\\]+[a-z0-9][a-z0-9_. -]*[/\\]'),
    'organization_workspace': re.compile(r'(?i)OneDrive\s*-\s*[a-z]'),
    'conversation_field': re.compile(r'["\x27](?:thread_id|threadId)["\x27]\s*:'),
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'classification': re.compile(r'(?i)MSIP_Label_[0-9a-f-]{36}|' + 'Microsoft ' + 'Information Protection|' + 'Azure ' + 'Information Protection'),
}
FORBIDDEN_SUFFIXES = {'.docx', '.pptx', '.xlsx', '.doc', '.ppt', '.xls', '.pem', '.pfx', '.p12', '.key'}
OFFICE_HEADER = bytes.fromhex('d0cf11e0a1b11ae1')


def distributable_paths(root: Path = ROOT) -> list[str]:
    result = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=root)
    return sorted(set(name for name in result.decode('utf-8').split('\0') if name))


def inspect_payload(name: str, contents: bytes, depth: int = 0) -> list[dict]:
    findings = []

    def flag(category):
        findings.append({'file': name, 'category': category})

    suffix = Path(name).suffix.lower()
    if suffix in FORBIDDEN_SUFFIXES or contents.startswith(OFFICE_HEADER):
        flag('restricted_file_type')
    if Path(name).name.startswith('.env') and Path(name).name != '.env.example':
        flag('environment_file')

    def inspect_text(text):
        for category, pattern in PATTERNS.items():
            matches = pattern.findall(text)
            if category == 'email':
                matches = [value for value in matches if not value.endswith('@users.noreply.github.com')]
            if matches:
                flag(category)

    if suffix not in {'.png', '.ttf', '.pdf', '.zip'}:
        inspect_text(contents.decode('utf-8', errors='replace'))
    if suffix == '.pdf':
        try:
            reader = PdfReader(io.BytesIO(contents), strict=False)
            if reader.is_encrypted:
                flag('encrypted_pdf')
                return findings
            metadata = dict(reader.metadata or {})
            inspect_text(json.dumps(metadata, default=str))
            if metadata.get('/Author') not in {None, '', 'Leonardus Lab', 'Leonardus Lab contributors'}:
                flag('personal_pdf_author')
            catalog = reader.trailer['/Root']
            if catalog.get('/Metadata'):
                inspect_text(catalog['/Metadata'].get_data().decode('utf-8', errors='replace'))
            if catalog.get('/Names'):
                flag('pdf_names_or_attachments')
            if catalog.get('/OpenAction') or catalog.get('/AA'):
                flag('pdf_active_content')
            for page in reader.pages:
                inspect_text(page.extract_text() or '')
                if page.get('/Annots'):
                    flag('pdf_annotations')
        except Exception:
            flag('unreadable_pdf')
    if suffix == '.png':
        try:
            with Image.open(io.BytesIO(contents)) as image:
                if image.getexif():
                    flag('image_exif')
                inspect_text(json.dumps(image.info, default=str))
        except Exception:
            flag('unreadable_image')
    if suffix == '.ttf':
        # Name table strings are the metadata exposed by installed fonts.
        from fontTools.ttLib import TTFont
        try:
            with TTFont(io.BytesIO(contents)) as font:
                for record in font['name'].names:
                    inspect_text(record.toUnicode())
        except Exception:
            flag('unreadable_font')
    if suffix == '.zip':
        if depth >= 4:
            flag('archive_depth_limit')
        else:
            try:
                with zipfile.ZipFile(io.BytesIO(contents)) as archive:
                    for entry in archive.infolist():
                        if entry.is_dir():
                            continue
                        if Path(entry.filename).is_absolute() or '..' in Path(entry.filename).parts:
                            flag('archive_path')
                        findings.extend(inspect_payload(name + '!' + entry.filename,
                                                        archive.read(entry), depth + 1))
            except Exception:
                flag('unreadable_archive')
    return findings


def inspect_tree(root: Path = ROOT) -> dict:
    paths = distributable_paths(root)
    findings = []
    for name in paths:
        findings.extend(inspect_payload(name, (root / name).read_bytes()))
    return {'files_checked': len(paths), 'findings': findings}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result = inspect_tree()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['findings']))
