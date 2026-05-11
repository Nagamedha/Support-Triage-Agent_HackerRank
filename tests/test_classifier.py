import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from classifier import Classifier


def test_request_type_classification():
    classifier = Classifier()

    test_cases = [
        ("The test is broken and crashes", "bug"),
        ("How do I invite candidates?", "product_issue"),
        ("Can you add dark mode feature?", "feature_request"),
    ]

    for issue, expected_type in test_cases:
        result = classifier.classify(issue)
        assert (
            result["request_type"] == expected_type
        ), f"Expected {expected_type}, got {result['request_type']} for: {issue}"

    print("✓ Request type classification working")


def test_product_area_hackerrank():
    classifier = Classifier()

    test_cases = [
        ("I need to add a test for my company", "screen"),
        ("How do I schedule an interview?", "interviews"),
        ("I forgot my password", "accounts"),
        ("Can you reduce my subscription?", "billing"),
    ]

    for issue, expected_area in test_cases:
        result = classifier.classify(issue, "hackerrank")
        assert (
            result["product_area"] == expected_area
        ), f"Expected {expected_area}, got {result['product_area']} for: {issue}"

    print("✓ HackerRank product area classification working")


def test_product_area_claude():
    classifier = Classifier()

    test_cases = [
        ("Can I delete my account?", "account-management"),
        ("I want to delete a conversation", "conversation-management"),
        ("How does web search work?", "features"),
        ("I want a refund", "billing"),
    ]

    for issue, expected_area in test_cases:
        result = classifier.classify(issue, "claude")
        assert (
            result["product_area"] == expected_area
        ), f"Expected {expected_area}, got {result['product_area']} for: {issue}"

    print("✓ Claude product area classification working")


def test_product_area_visa():
    classifier = Classifier()

    test_cases = [
        ("My credit card was stolen", "consumer"),
        ("I have a dispute with a payment", "merchant"),
    ]

    for issue, expected_area in test_cases:
        result = classifier.classify(issue, "visa")
        assert (
            result["product_area"] == expected_area
        ), f"Expected {expected_area}, got {result['product_area']} for: {issue}"

    print("✓ Visa product area classification working")


def test_invalid_detection():
    classifier = Classifier()

    # Short, vague queries are likely invalid
    result = classifier.classify("x y")
    assert result["request_type"] == "invalid", "Very short query should be invalid"

    # Real domain queries should not be invalid
    result = classifier.classify("How to invite candidates?")
    assert result["request_type"] != "invalid", "Real query should not be invalid"

    print("✓ Invalid detection working")


if __name__ == "__main__":
    test_request_type_classification()
    test_product_area_hackerrank()
    test_product_area_claude()
    test_product_area_visa()
    test_invalid_detection()
    print("\n✅ All classifier tests passed")
