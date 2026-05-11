import sys
from pathlib import Path
import csv
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from agent import TriageAgent


def test_agent_end_to_end():
    # Get corpus path
    corpus_path = Path(__file__).parent.parent / "data"

    # Create agent
    agent = TriageAgent(str(corpus_path))

    # Create temp input CSV
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        input_path = f.name
        writer = csv.DictWriter(f, fieldnames=["Issue", "Subject", "Company"])
        writer.writeheader()
        writer.writerow(
            {
                "Issue": "How do I invite candidates to a test?",
                "Subject": "Test invites",
                "Company": "HackerRank",
            }
        )
        writer.writerow(
            {
                "Issue": "I want to delete a conversation with private info",
                "Subject": "Delete chat",
                "Company": "Claude",
            }
        )
        writer.writerow(
            {
                "Issue": "What is the meaning of life?",
                "Subject": "Philosophy",
                "Company": "None",
            }
        )

    # Create temp output CSV
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        output_path = f.name

    try:
        # Process tickets
        agent.process_tickets(input_path, output_path)

        # Verify output
        with open(output_path, "r") as f:
            reader = csv.DictReader(f)
            results = list(reader)

        assert len(results) == 3, "Should have 3 results"

        # Check first result (should be replied)
        assert results[0]["status"] in ["replied", "escalated"], "Should have status"
        assert results[0]["product_area"], "Should have product area"
        assert results[0]["response"], "Should have response"
        assert results[0]["justification"], "Should have justification"
        assert results[0]["request_type"], "Should have request type"

        # Check structure
        for result in results:
            assert len(result["response"]) <= 500, "Response should be truncated"
            assert len(result["justification"]) <= 200, "Justification should be truncated"

        print("✓ Agent end-to-end processing working")
        print(f"  Result 1: {results[0]['status']} ({results[0]['product_area']})")
        print(f"  Result 2: {results[1]['status']} ({results[1]['product_area']})")
        print(f"  Result 3: {results[2]['status']} ({results[2]['product_area']})")

    finally:
        # Cleanup
        Path(input_path).unlink()
        Path(output_path).unlink()


def test_agent_company_detection():
    corpus_path = Path(__file__).parent.parent / "data"
    agent = TriageAgent(str(corpus_path))

    # Test with each company
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        input_path = f.name
        writer = csv.DictWriter(f, fieldnames=["Issue", "Subject", "Company"])
        writer.writeheader()
        writer.writerow({"Issue": "test assessment", "Subject": "test", "Company": "hackerrank"})
        writer.writerow({"Issue": "account login", "Subject": "account", "Company": "claude"})
        writer.writerow({"Issue": "card fraud", "Subject": "fraud", "Company": "visa"})

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        output_path = f.name

    try:
        agent.process_tickets(input_path, output_path)

        with open(output_path, "r") as f:
            reader = csv.DictReader(f)
            results = list(reader)

        # Company-specific checks
        assert results[0]["product_area"], "HackerRank should have product area"
        assert results[1]["product_area"], "Claude should have product area"
        assert results[2]["status"] == "escalated", "Fraud should escalate"

        print("✓ Company detection working")

    finally:
        Path(input_path).unlink()
        Path(output_path).unlink()


if __name__ == "__main__":
    test_agent_end_to_end()
    test_agent_company_detection()
    print("\n✅ All integration tests passed")
