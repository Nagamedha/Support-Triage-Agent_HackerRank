import csv
from pathlib import Path
from typing import List, Dict

from corpus_loader import CorpusLoader
from retriever import Retriever
from classifier import Classifier
from router import Router


class TriageAgent:
    def __init__(self, corpus_path: str, api_provider: str = "keyword"):
        # Initialize all modules
        self.corpus_path = Path(corpus_path)
        self.api_provider = api_provider

        # Load corpus
        loader = CorpusLoader(str(self.corpus_path))
        self.documents = loader.load()
        print(f"✓ Loaded {len(self.documents)} documents")

        # Initialize retriever, classifier, router
        self.retriever = Retriever(self.documents, api_provider)
        self.classifier = Classifier()
        self.router = Router()

    def process_tickets(self, input_csv: str, output_csv: str) -> None:
        # Read input CSV
        input_path = Path(input_csv)
        output_path = Path(output_csv)

        tickets = []
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tickets.append(row)

        print(f"✓ Read {len(tickets)} tickets from {input_csv}")

        # Process each ticket
        results = []
        for idx, ticket in enumerate(tickets):
            result = self._process_single_ticket(ticket)
            results.append(result)

            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(tickets)}")

        # Write output CSV
        self._write_output(results, output_path)
        print(f"✓ Wrote {len(results)} results to {output_csv}")

    def _process_single_ticket(self, ticket: Dict) -> Dict:
        # Extract fields
        issue = ticket.get("Issue", "").strip()
        subject = ticket.get("Subject", "").strip()
        company = ticket.get("Company", "").strip() or None

        # Normalize company name
        if company:
            company = company.lower()
            if company not in ["hackerrank", "claude", "visa"]:
                company = None

        # Step 1: Retrieve relevant docs
        retrieved = self.retriever.retrieve(issue, top_k=3, company=company)

        # Step 2: Classify
        classification = self.classifier.classify(issue, company)

        # Step 3: Route (reply or escalate)
        routing = self.router.route(
            issue=issue,
            retrieved_docs=retrieved,
            request_type=classification["request_type"],
            product_area=classification["product_area"],
            company=company,
        )

        # Step 4: Assemble output row
        return {
            "Issue": issue,
            "Subject": subject,
            "Company": company or "",
            "status": routing["status"],
            "product_area": routing["product_area"],
            "response": routing["response"],
            "justification": routing["justification"],
            "request_type": classification["request_type"],
        }

    @staticmethod
    def _write_output(results: List[Dict], output_path: Path) -> None:
        # Write CSV with required columns
        fieldnames = ["status", "product_area", "response", "justification", "request_type"]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow(
                    {
                        "status": result["status"],
                        "product_area": result["product_area"],
                        "response": result["response"][:500],  # Truncate to 500 chars
                        "justification": result["justification"][:200],  # Truncate to 200 chars
                        "request_type": result["request_type"],
                    }
                )
