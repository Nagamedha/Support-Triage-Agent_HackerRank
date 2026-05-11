import sys
from pathlib import Path
import csv
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from agent import TriageAgent


def test_on_sample_tickets():
    # Paths
    corpus_path = Path(__file__).parent.parent / "data"
    sample_input = Path(__file__).parent.parent / "support_tickets" / "sample_support_tickets.csv"

    # Create agent
    agent = TriageAgent(str(corpus_path))
    print(f"✓ Agent initialized with {len(agent.documents)} documents\n")

    # Read sample tickets
    tickets = []
    expected_outputs = {}

    with open(sample_input, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            issue = row.get("Issue", "").strip()
            tickets.append(row)

            # Store expected outputs
            expected_outputs[idx] = {
                "status": row.get("Status", "").strip().lower(),
                "product_area": row.get("Product Area", "").strip().lower(),
                "request_type": row.get("Request Type", "").strip().lower(),
            }

    print(f"✓ Loaded {len(tickets)} sample tickets\n")

    # Process with temp output file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        temp_input = f.name
        writer = csv.DictWriter(f, fieldnames=["Issue", "Subject", "Company"])
        writer.writeheader()
        for ticket in tickets:
            writer.writerow(
                {
                    "Issue": ticket.get("Issue", ""),
                    "Subject": ticket.get("Subject", ""),
                    "Company": ticket.get("Company", ""),
                }
            )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        temp_output = f.name

    try:
        # Run agent
        print("Running agent on sample tickets...")
        agent.process_tickets(temp_input, temp_output)

        # Read results
        results = []
        with open(temp_output, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)

        print(f"✓ Agent produced {len(results)} outputs\n")

        # Compare
        status_correct = 0
        area_correct = 0
        type_correct = 0

        print("Sample Results:")
        print("-" * 80)

        for idx, result in enumerate(results[:5]):  # Show first 5
            expected = expected_outputs[idx]
            actual_status = result["status"].lower()
            actual_area = result["product_area"].lower()
            actual_type = result["request_type"].lower()

            status_match = actual_status == expected["status"]
            area_match = actual_area == expected["product_area"]
            type_match = actual_type == expected["request_type"]

            print(f"\nTicket {idx + 1}:")
            print(f"  Status:  {actual_status:20} Expected: {expected['status']:20} {'✓' if status_match else '✗'}")
            print(
                f"  Area:    {actual_area:20} Expected: {expected['product_area']:20} {'✓' if area_match else '✗'}"
            )
            print(f"  Type:    {actual_type:20} Expected: {expected['request_type']:20} {'✓' if type_match else '✗'}")

        # Count all
        for idx, result in enumerate(results):
            expected = expected_outputs[idx]
            if result["status"].lower() == expected["status"]:
                status_correct += 1
            if result["product_area"].lower() == expected["product_area"]:
                area_correct += 1
            if result["request_type"].lower() == expected["request_type"]:
                type_correct += 1

        # Print metrics
        print("\n" + "=" * 80)
        print("ACCURACY METRICS:")
        print("=" * 80)
        print(f"Status Accuracy:       {status_correct}/{len(results)} ({100*status_correct/len(results):.1f}%)")
        print(f"Product Area Accuracy: {area_correct}/{len(results)} ({100*area_correct/len(results):.1f}%)")
        print(f"Request Type Accuracy: {type_correct}/{len(results)} ({100*type_correct/len(results):.1f}%)")
        overall = (status_correct + area_correct + type_correct) / (3 * len(results))
        print(f"Overall Accuracy:      {100*overall:.1f}%")
        print("=" * 80)

    finally:
        Path(temp_input).unlink()
        Path(temp_output).unlink()


if __name__ == "__main__":
    test_on_sample_tickets()
