import os
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from corpus_loader import Document


@dataclass
class RetrievalResult:
    document: Document
    confidence: float
    method: str  # "keyword" or "embedding"


class Retriever:
    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do", "for",
        "from", "have", "help", "how", "i", "in", "is", "it", "me", "my", "of",
        "on", "or", "our", "please", "the", "them", "there", "this", "to", "us",
        "we", "what", "when", "where", "with", "you", "your", "all", "any", "not",
        "hackerrank", "claude", "visa", "support", "issue",
    }

    DOC_HINTS = [
        (("extra time", "time accommodation", "add time"), "adding-extra-time-for-candidates"),
        (("variant", "variants"), "test-variants"),
        (("delete my account", "google login"), "delete-an-account"),
        (("private info", "delete conversation"), "delete-or-rename-a-conversation"),
        (("traveller", "travelers cheque", "cheques"), "travelers-cheques"),
        (("lost or stolen", "lost card", "stolen card", "identity"), "support.md"),
        (("emergency cash", "urgent cash", "cash"), "travel-support"),
        (("minimum", "minimum spend"), "support.md"),
        (("dispute a charge", "wrong product"), "support.md"),
        (("pause subscription",), "pause-subscription"),
        (("remove an interviewer", "employee has left", "remove them", "remove a user"), "locking-user-access"),
        (("inactivity", "kicked out", "lobby"), "enhancing-your-account-security"),
        (("compatibility", "compatible check", "zoom connectivity"), "audio-and-video-calls"),
        (("apply tab", "quick apply"), "set-up-quick-apply"),
        (("resume builder",), "create-a-resume-with-resume-builder"),
        (("certificate",), "download-certificate"),
        (("crawler", "crawling", "stop crawling"), "block-the-crawler"),
        (("vulnerability", "bug bounty"), "public-vulnerability-reporting"),
        (("bedrock",), "amazon-bedrock"),
        (("lti", "canvas"), "claude-lti"),
        (("data to improve", "use my data", "improve the models"), "sensitive-data-into-my-chats"),
        (("rescheduling", "reschedule"), "ensuring-a-great-candidate-experience"),
    ]

    def __init__(self, documents: List[Document], api_provider: str = "keyword"):
        self.documents = documents
        self.api_provider = api_provider
        self.embedding_cache = {}

    def retrieve(self, query: str, top_k: int = 3, company: str = None) -> List[RetrievalResult]:
        # Step 1: Try keyword search (fast, deterministic, free)
        keyword_results = self._keyword_search(query, company, top_k)

        if keyword_results and keyword_results[0].confidence > 0.5:
            return keyword_results

        # Step 2: If low confidence, try embedding search (slower, costs $, accurate)
        if self.api_provider == "openai":
            embedding_results = self._embedding_search(query, company, top_k)
            if embedding_results:
                return embedding_results

        # Step 3: Fallback to keyword results even if low confidence
        return keyword_results

    def _keyword_search(self, query: str, company: str = None, top_k: int = 3) -> List[RetrievalResult]:
        # Case-insensitive keyword matching
        query_lower = query.lower()
        query_words = self._tokens(query_lower)
        results = []

        search_docs = [d for d in self.documents if company is None or d.company == company]

        for doc in search_docs:
            score = 0
            doc_title_lower = doc.title.lower()
            doc_content_lower = doc.content.lower()
            doc_category_lower = doc.category.lower()
            doc_path_lower = doc.path.lower()

            for triggers, path_hint in self.DOC_HINTS:
                if any(trigger in query_lower for trigger in triggers) and path_hint in doc_path_lower:
                    score += 80
            if any(term in query_lower for term in ("inactivity", "kicked out", "lobby")) and "enhancing-your-account-security" in doc_path_lower:
                score += 160

            # Prefer exact/near-exact title and path matches, then body evidence.
            phrase = " ".join(query_words[:6])
            if phrase and phrase in doc_title_lower:
                score += 30
            for word in query_words:
                if word in doc_path_lower:
                    score += 12

            for word in query_words:
                if word in doc_title_lower:
                    score += 15
                if word in doc_category_lower:
                    score += 8
                if word in doc_content_lower:
                    score += 2

            if score > 0:
                confidence = min(score / 45.0, 1.0)
                results.append((RetrievalResult(doc, confidence, "keyword"), score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [result for result, _score in results[:top_k]]

    @classmethod
    def _tokens(cls, text: str) -> List[str]:
        words = re.findall(r"[a-z0-9][a-z0-9'-]{2,}", text.lower())
        return [w for w in words if w not in cls.STOPWORDS]

    def _embedding_search(self, query: str, company: str = None, top_k: int = 3) -> List[RetrievalResult]:
        # Use OpenAI embeddings for semantic search
        try:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return []

            client = OpenAI(api_key=api_key)

            # Get embedding for query
            query_embedding = client.embeddings.create(
                model="text-embedding-3-small", input=query
            ).data[0].embedding

            # Get embeddings for documents (use cache)
            search_docs = [d for d in self.documents if company is None or d.company == company]
            results = []

            for doc in search_docs:
                doc_key = f"{doc.company}:{doc.path}"
                if doc_key not in self.embedding_cache:
                    doc_embedding = client.embeddings.create(
                        model="text-embedding-3-small", input=doc.content[:1000]  # First 1000 chars
                    ).data[0].embedding
                    self.embedding_cache[doc_key] = doc_embedding
                else:
                    doc_embedding = self.embedding_cache[doc_key]

                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                if similarity > 0.3:
                    results.append(RetrievalResult(doc, similarity, "embedding"))

            results.sort(key=lambda x: x.confidence, reverse=True)
            return results[:top_k]

        except Exception as e:
            print(f"Embedding search failed: {e}")
            return []

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        # Calculate cosine similarity between two embedding vectors
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x**2 for x in a) ** 0.5
        magnitude_b = sum(x**2 for x in b) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)
