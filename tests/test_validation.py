from datetime import date
from app.extraction.demo import DeterministicDemoExtractor
from app.validation.rules import validate_extraction

BASE='''PO: A-1\nCustomer: Acme\nOrder Date: 2026-11-05\nCurrency: USD\nITEM|S1|Item|2|10.00|20.00\nSubtotal: 20.00\nTax: 2.00\nTotal: 22.00\nRequested Delivery: 2026-11-10\nSignature: present'''

def test_clean_document_has_no_blocking_issues():
    issues=validate_extraction(DeterministicDemoExtractor().extract(BASE),today=date(2026,11,5))
    assert not [x for x in issues if x.severity=='error']

def test_bad_total_is_caught():
    text=BASE.replace('Total: 22.00','Total: 30.00')
    codes={x.code for x in validate_extraction(DeterministicDemoExtractor().extract(text),today=date(2026,11,5))}
    assert 'total_mismatch' in codes

def test_line_math_error_is_caught():
    text=BASE.replace('ITEM|S1|Item|2|10.00|20.00','ITEM|S1|Item|2|10.00|25.00').replace('Subtotal: 20.00','Subtotal: 25.00').replace('Tax: 2.00','Tax: 2.50').replace('Total: 22.00','Total: 27.50')
    codes={x.code for x in validate_extraction(DeterministicDemoExtractor().extract(text),today=date(2026,11,5))}
    assert 'line_total_mismatch' in codes
