import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from router import Router
from retriever import RetrievalResult
from corpus_loader import Document


def test_escalate_high_risk():
    router = Router()

    # High-risk: refund
    result = router.route("I need a refund", [], "product_issue", "billing", "hackerrank")
    assert result["status"] == "escalated", "Refund request should escalate"

    # High-risk: fraud
    result = router.route("My card was stolen", [], "product_issue", "consumer", "visa")
    assert result["status"] == "escalated", "Fraud should escalate"

    # High-risk: account deletion
    result = router.route("Please delete my account", [], "product_issue", "account", "claude")
    assert result["status"] == "escalated", "Account deletion should escalate"

    print("✓ High-risk escalation working")


def test_reply_invalid():
    router = Router()

    result = router.route("What is 2+2?", [], "invalid", "general", None)
    assert result["status"] == "replied", "Invalid should reply, not escalate"
    assert "out of scope" in result["response"].lower(), "Should say out of scope"

    print("✓ Invalid request handling working")


def test_escalate_no_docs():
    router = Router()

    result = router.route("Some normal question", [], "product_issue", "billing", "hackerrank")
    assert result["status"] == "escalated", "No docs should escalate"

    print("✓ No docs escalation working")


def test_escalate_low_confidence():
    router = Router()

    # Create mock doc with low confidence
    mock_doc = Document(
        path="test",
        title="Test",
        content="Some content",
        company="hackerrank",
        category="test",
    )
    low_conf_result = RetrievalResult(mock_doc, 0.3, "keyword")

    result = router.route("Some question", [low_conf_result], "product_issue", "screen", "hackerrank")
    assert result["status"] == "escalated", "Low confidence should escalate"

    print("✓ Low confidence escalation working")


def test_reply_with_corpus():
    router = Router()

    # Create mock doc with high confidence
    mock_doc = Document(
        path="test/path",
        title="How to invite candidates",
        content="To invite candidates:\n1. Go to tests\n2. Click invite\n3. Add email",
        company="hackerrank",
        category="screen",
    )
    high_conf_result = RetrievalResult(mock_doc, 0.9, "keyword")

    result = router.route("How to invite candidates?", [high_conf_result], "product_issue", "screen", "hackerrank")
    assert result["status"] == "replied", "High confidence should reply"
    assert "invite" in result["response"].lower(), "Response should be grounded in corpus"
    assert "hackerrank" in result["justification"].lower(), "Justification should cite source"

    print("✓ Corpus-grounded reply working")


def test_response_formatting():
    router = Router()

    # Long document
    long_content = "A" * 1000
    mock_doc = Document(
        path="test",
        title="Long doc",
        content=long_content,
        company="claude",
        category="test",
    )
    result = RetrievalResult(mock_doc, 0.8, "keyword")

    formatted = Router._format_response(result)
    assert len(formatted) <= 600, "Should truncate long responses"
    assert "..." in formatted, "Should show ellipsis for truncated"

    print("✓ Response formatting working")


if __name__ == "__main__":
    test_escalate_high_risk()
    test_reply_invalid()
    test_escalate_no_docs()
    test_escalate_low_confidence()
    test_reply_with_corpus()
    test_response_formatting()
    print("\n✅ All router tests passed")
