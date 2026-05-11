import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from corpus_loader import CorpusLoader


def test_load_corpus():
    # Load corpus and check counts
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    assert len(docs) > 0, "Corpus should load documents"
    print(f"✓ Loaded {len(docs)} documents")


def test_load_by_company():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    loader.load()

    claude_docs = loader.get_by_company("claude")
    hackerrank_docs = loader.get_by_company("hackerrank")
    visa_docs = loader.get_by_company("visa")

    assert len(claude_docs) > 0, "Should have Claude docs"
    assert len(hackerrank_docs) > 0, "Should have HackerRank docs"
    assert len(visa_docs) > 0, "Should have Visa docs"

    print(f"✓ Claude: {len(claude_docs)}, HackerRank: {len(hackerrank_docs)}, Visa: {len(visa_docs)}")


def test_keyword_search():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    loader.load()

    # Search for common terms
    test_queries = ["test", "account", "card"]

    for query in test_queries:
        results = loader.search_keyword(query, top_k=5)
        assert len(results) > 0, f"Should find results for '{query}'"

    print("✓ Keyword search working")


def test_document_structure():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    for doc in docs[:5]:  # Check first 5
        assert doc.path, "Document should have path"
        assert doc.title, "Document should have title"
        assert doc.content, "Document should have content"
        assert doc.company in ["claude", "hackerrank", "visa"], "Invalid company"
        assert doc.category, "Document should have category"

    print("✓ Document structure valid")


if __name__ == "__main__":
    test_load_corpus()
    test_load_by_company()
    test_keyword_search()
    test_document_structure()
    print("\n✅ All corpus loader tests passed")
