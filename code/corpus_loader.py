import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Document:
    path: str
    title: str
    content: str
    company: str
    category: str


class CorpusLoader:
    def __init__(self, corpus_path: str):
        self.corpus_path = Path(corpus_path)
        self.documents: List[Document] = []

    def load(self) -> List[Document]:
        # Load all markdown files from corpus
        companies = ["claude", "hackerrank", "visa"]

        for company in companies:
            company_path = self.corpus_path / company
            if not company_path.exists():
                continue

            self._load_company(company_path, company)

        return self.documents

    def _load_company(self, company_path: Path, company: str):
        # Recursively load all .md files from company folder
        for md_file in company_path.rglob("*.md"):
            if md_file.name == "index.md":
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
                # Extract title from filename
                title = md_file.stem.replace("-", " ").title()
                # Extract category from parent folder
                category = md_file.parent.name

                doc = Document(
                    path=str(md_file.relative_to(self.corpus_path)),
                    title=title,
                    content=content,
                    company=company,
                    category=category
                )
                self.documents.append(doc)
            except Exception as e:
                print(f"Error loading {md_file}: {e}")

    def search_keyword(self, query: str, top_k: int = 5) -> List[Document]:
        # Simple keyword search, case-insensitive
        query_lower = query.lower()
        results = []

        for doc in self.documents:
            score = 0
            if query_lower in doc.title.lower():
                score += 10
            if query_lower in doc.content.lower():
                score += 5

            if score > 0:
                results.append((doc, score))

        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:top_k]]

    def get_by_company(self, company: str) -> List[Document]:
        # Get all documents for a specific company
        return [doc for doc in self.documents if doc.company == company]

    def get_all(self) -> List[Document]:
        return self.documents
