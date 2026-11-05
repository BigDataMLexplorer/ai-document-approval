from app.extraction.demo import DeterministicDemoExtractor
from app.models import HumanReviewRequest, ReviewStatus
from app.workflow.engine import DocumentWorkflow

CLEAN='''PO: A-1\nCustomer: Acme\nOrder Date: 2026-11-05\nCurrency: USD\nITEM|S1|Item|2|10.00|20.00\nSubtotal: 20.00\nTax: 2.00\nTotal: 22.00\nRequested Delivery: 2026-11-10\nSignature: present'''

def test_clean_case_auto_approves():
    case=DocumentWorkflow(DeterministicDemoExtractor()).process(CLEAN)
    assert case.status==ReviewStatus.AUTO_APPROVED

def test_low_confidence_routes_to_human():
    case=DocumentWorkflow(DeterministicDemoExtractor()).process(CLEAN+'\nLOW_CONFIDENCE: total')
    assert case.status==ReviewStatus.NEEDS_REVIEW

def test_human_can_approve_review_case():
    wf=DocumentWorkflow(DeterministicDemoExtractor())
    case=wf.process(CLEAN.replace('Signature: present','Signature: missing'))
    reviewed=wf.review(case.id,HumanReviewRequest(approved=True,note='verified signature offline'))
    assert reviewed.status==ReviewStatus.HUMAN_APPROVED
    assert reviewed.audit[-1].event_type=='human_approved'
