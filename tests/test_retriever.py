import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from corpus_loader import CorpusLoader
from retriever import Retriever


def test_keyword_retrieve():
    # Load corpus
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    retriever = Retriever(docs)

    # Test keyword retrieval
    results = retriever.retrieve("test assessment", top_k=3)

    assert len(results) > 0, "Should find results for 'test assessment'"
    assert all(r.method == "keyword" for r in results), "Should use keyword method for good matches"
    assert all(0 <= r.confidence <= 1 for r in results), "Confidence should be 0-1"

    print(f"✓ Keyword retrieval: Found {len(results)} docs, top confidence: {results[0].confidence:.2f}")


def test_company_filter():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    retriever = Retriever(docs)

    # Retrieve only from Claude
    results = retriever.retrieve("conversation delete", company="claude", top_k=3)

    assert len(results) > 0, "Should find Claude docs"
    assert all(r.document.company == "claude" for r in results), "All results should be from Claude"

    print(f"✓ Company filter: Found {len(results)} Claude docs")


def test_multiple_queries():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    retriever = Retriever(docs)

    test_queries = [
        ("test candidates", "hackerrank"),
        ("account deletion", "claude"),
        ("visa card fraud", "visa"),
    ]

    for query, expected_company in test_queries:
        results = retriever.retrieve(query, company=expected_company, top_k=1)
        assert len(results) > 0, f"Should find results for '{query}' in {expected_company}"

    print("✓ Multiple queries working")


def test_low_confidence_fallback():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    retriever = Retriever(docs)

    # Query that might not match well
    results = retriever.retrieve("xyz123notaword", top_k=3)

    # Should return empty or low confidence results, not crash
    assert isinstance(results, list), "Should return list even for bad query"

    print(f"✓ Low confidence fallback: Returned {len(results)} results")


def test_result_structure():
    corpus_path = Path(__file__).parent.parent / "data"
    loader = CorpusLoader(str(corpus_path))
    docs = loader.load()

    retriever = Retriever(docs)
    results = retriever.retrieve("test", top_k=1)

    if results:
        result = results[0]
        assert hasattr(result, "document"), "Result should have document"
        assert hasattr(result, "confidence"), "Result should have confidence"
        assert hasattr(result, "method"), "Result should have method"
        assert result.method in ["keyword", "embedding"], "Method should be keyword or embedding"

    print("✓ Result structure valid")


if __name__ == "__main__":
    test_keyword_retrieve()
    test_company_filter()
    test_multiple_queries()
    test_low_confidence_fallback()
    test_result_structure()
    print("\n✅ All retriever tests passed")
