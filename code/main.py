#!/usr/bin/env python3
"""
Support Triage Agent - Main Entry Point
Processes support tickets and generates output.csv
"""

import os
import sys
from pathlib import Path

from agent import TriageAgent


def main():
    # Load environment variables from .env (simple manual loading)
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    # Get paths
    repo_root = Path(__file__).parent.parent
    corpus_path = repo_root / "data"
    input_csv = repo_root / "support_tickets" / "support_tickets.csv"
    output_csv = repo_root / "support_tickets" / "output.csv"

    # Validate paths
    if not corpus_path.exists():
        print(f"❌ Error: Corpus not found at {corpus_path}")
        sys.exit(1)

    if not input_csv.exists():
        print(f"❌ Error: Input CSV not found at {input_csv}")
        sys.exit(1)

    # Initialize agent
    print("Initializing Support Triage Agent...\n")
    agent = TriageAgent(str(corpus_path), api_provider="keyword")

    # Process tickets
    print(f"Processing tickets from {input_csv.name}...\n")
    agent.process_tickets(str(input_csv), str(output_csv))

    print(f"\n✅ Output written to: {output_csv}\n")
    print("Ready for submission!")


if __name__ == "__main__":
    main()
