"""Validate the printable artifact independently of Office and its local files."""
import importlib.util
from pathlib import Path

from pypdf import PdfReader
from fontTools.ttLib import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

ROOT = Path(__file__).resolve().parents[1]


def test_print_specimen_reproducible_a4_and_scale(tmp_path):
    spec = importlib.util.spec_from_file_location("print1270", ROOT / "examples/print_specimen_1270.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    repertoire = TTFont(ROOT / "fonts/Leonardus-Regular-1.270.ttf").getBestCmap()
    sample_characters = {ord(char) for lines in module.SAMPLES.values() for line in lines for char in line}
    assert set(repertoire) <= sample_characters
    output = tmp_path / "print.pdf"
    module.create_specimen(ROOT / "fonts/Leonardus-Regular-1.270.ttf", output)
    assert output.read_bytes() == (ROOT / "specimen/Leonardus-1270-Print-Specimen.pdf").read_bytes()
    pdf = PdfReader(output)
    assert len(pdf.pages) == 4
    assert not pdf.is_encrypted
    assert pdf.metadata.author == "Leonardus Lab"
    for page, pt in zip(pdf.pages, (12, 18, 36, 72)):
        assert abs(float(page.mediabox.width) - A4[0]) < .001
        assert abs(float(page.mediabox.height) - A4[1]) < .001
        assert f"{pt} punti" in page.extract_text()
        assert not page.get("/Annots")
        assert not page["/Resources"].get("/XObject")
        # The ruler is a 50 mm vector segment, independent of the sample paths.
        ops = page.get_contents().operations
        assert any(op == b"l" and abs(float(args[0]) - (45 + 50 * mm)) < .001
                   and float(args[1]) == 72 for args, op in ops)
