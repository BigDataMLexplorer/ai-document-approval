from io import BytesIO
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from app.parsers import parse_bytes


def test_text_parser():
    assert parse_bytes('x.txt', b'hello') == 'hello'


def test_pdf_parser_extracts_text(tmp_path: Path):
    path=tmp_path/'x.pdf'
    c=canvas.Canvas(str(path), pagesize=LETTER);c.drawString(72,750,'PO: X-1');c.save()
    assert 'PO: X-1' in parse_bytes(path.name,path.read_bytes())
