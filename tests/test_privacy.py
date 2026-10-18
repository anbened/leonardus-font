"""Regression checks for leaks that an ordinary font build does not detect."""
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_privacy', ROOT / 'examples/check_privacy.py')
privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(privacy)


def test_distributable_tree_has_no_privacy_findings():
    assert privacy.inspect_tree()['findings'] == []


@pytest.mark.parametrize('contents', [
    ('C:' + '/Users/' + 'example/Documents/file.pdf').encode(),
    ('OneDrive' + ' - ' + 'Example Org').encode(),
    ('{"thread' + '_id": "example"}').encode(),
    ('personal' + '@' + 'example.test').encode(),
])
def test_plaintext_leaks_are_rejected(contents):
    assert privacy.inspect_payload('data/example.json', contents)


def test_classification_inside_pdf_metadata_is_rejected():
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.add_metadata({'/' + 'MSIP' + '_Label_' + '0' * 36 + '_Name': 'Restricted'})
    stream = io.BytesIO()
    writer.write(stream)
    assert any(item['category'] == 'classification' for item in privacy.inspect_payload('proof.pdf', stream.getvalue()))


def test_compressed_xmp_metadata_is_decoded_before_scanning():
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    metadata = DecodedStreamObject()
    metadata.set_data(('<metadata>' + 'MSIP' + '_Label_' + '0' * 36 + '_Name</metadata>').encode())
    writer._root_object[NameObject('/Metadata')] = writer._add_object(metadata.flate_encode())
    stream = io.BytesIO()
    writer.write(stream)
    assert any(item['category'] == 'classification' for item in privacy.inspect_payload('proof.pdf', stream.getvalue()))


def test_encrypted_pdf_cannot_be_cleared_without_inspection():
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.encrypt('synthetic' + '-fixture')
    stream = io.BytesIO()
    writer.write(stream)
    assert any(item['category'] == 'encrypted_pdf' for item in privacy.inspect_payload('proof.pdf', stream.getvalue()))


def test_personal_pdf_author_is_rejected():
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.add_metadata({'/Author': 'Example Person'})
    stream = io.BytesIO()
    writer.write(stream)
    assert any(item['category'] == 'personal_pdf_author' for item in privacy.inspect_payload('proof.pdf', stream.getvalue()))


def test_nested_archive_is_inspected():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('data/identity.json', 'personal' + '@' + 'example.test')
    assert any(item['category'] == 'email' for item in privacy.inspect_payload('package.zip', stream.getvalue()))


def test_office_protection_wrapper_is_rejected():
    assert privacy.inspect_payload('proof.docx', privacy.OFFICE_HEADER + b'placeholder')


def test_pdf_default_epoch_matches_ci_epoch(tmp_path):
    first, second = tmp_path / 'default.pdf', tmp_path / 'epoch0.pdf'
    environment = dict(os.environ)
    environment.pop('SOURCE_DATE_EPOCH', None)
    command = [sys.executable, str(ROOT / 'examples/regular_pdf_specimen.py'),
               '--font', str(ROOT / 'fonts/Leonardus-Regular.ttf')]
    subprocess.run([*command, '--out', str(first)], cwd=ROOT, env=environment,
                   capture_output=True, check=True)
    environment['SOURCE_DATE_EPOCH'] = '0'
    subprocess.run([*command, '--out', str(second)], cwd=ROOT, env=environment,
                   capture_output=True, check=True)
    assert first.read_bytes() == second.read_bytes() == (ROOT / 'specimen/Leonardus-Specimen.pdf').read_bytes()
