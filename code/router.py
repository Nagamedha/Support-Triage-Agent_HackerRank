import re
from typing import List, Dict
from retriever import RetrievalResult


class Router:
    # High-risk keywords that should always escalate
    HIGH_RISK_KEYWORDS = [
        "refund", "payment", "billing", "invoice", "order id",  # Financial
        "fraud", "identity theft", "security breach", "vulnerability", "bug bounty",  # Security
        "delete account", "remove data", "wipe", "erase", "delete all files",  # Destructive
        "score dispute", "unfair", "review my answers",  # Scoring/fairness
        "access lost", "locked out", "can't login", "account suspended", "restore my access",  # Account access
        "site is down", "all requests are failing", "all requests to claude", "none of the submissions",  # Outage/bugs
        "permissions", "access level",  # Permissions
        "infosec", "security questionnaire",
        "internal", "logic exact", "documents retrieved", "règles internes", "logique exacte",  # prompt injection / policy disclosure
    ]

    def route(
        self,
        issue: str,
        retrieved_docs: List[RetrievalResult],
        request_type: str,
        product_area: str,
        company: str,
    ) -> Dict:
        # Step 1: Check for high-risk keywords
        high_risk_reason = self._high_risk_reason(issue)
        if high_risk_reason:
            return self._escalate(
                "I can't safely resolve this directly from the support corpus. A support specialist should review it.",
                issue,
                request_type,
                product_area,
                high_risk_reason,
            )

        # Step 2: Check if invalid request
        if request_type == "invalid":
            return self._reply_out_of_scope(product_area)

        # Step 3: Check if we have good docs
        if not retrieved_docs:
            return self._escalate(
                "Unable to find relevant information in support corpus. Escalating to human.",
                issue,
                request_type,
                product_area,
            )

        # Step 4: Check confidence
        top_confidence = retrieved_docs[0].confidence
        if top_confidence < 0.4:
            return self._escalate(
                "Unable to find reliable answer. Requires human review.",
                issue,
                request_type,
                product_area,
            )

        # Step 5: Generate grounded reply
        return self._reply_with_corpus(retrieved_docs, request_type, product_area, issue)

    def _is_high_risk(self, issue: str) -> bool:
        return self._high_risk_reason(issue) is not None

    def _high_risk_reason(self, issue: str) -> str:
        issue_lower = issue.lower()
        for keyword in self.HIGH_RISK_KEYWORDS:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, issue_lower):
                return keyword
        return None

    def _reply_out_of_scope(self, product_area: str) -> Dict:
        # Reply with friendly "out of scope" message
        return {
            "status": "replied",
            "response": "I am sorry, this is out of scope from my capabilities. Please contact our support team for assistance.",
            "justification": "Request is unrelated to supported domains (HackerRank, Claude, Visa).",
            "product_area": product_area,
        }

    def _reply_with_corpus(
        self, retrieved_docs: List[RetrievalResult], request_type: str, product_area: str, issue: str
    ) -> Dict:
        # Generate reply grounded in corpus
        doc = retrieved_docs[0]
        response_text = self._format_response(doc, issue)

        return {
            "status": "replied",
            "response": response_text,
            "justification": f"Answer grounded in {doc.document.company} support documentation ({doc.document.title}). Confidence: {doc.confidence:.2f}",
            "product_area": product_area,
        }

    def _escalate(self, reason: str, issue: str, request_type: str, product_area: str, high_risk_keyword: str = None) -> Dict:
        # Escalate to human with specific justification
        justification = reason

        # If high-risk, identify specific keyword
        if high_risk_keyword:
            justification = f"Sensitive or high-risk request detected: '{high_risk_keyword}'. Requires human review."

        return {
            "status": "escalated",
            "response": reason,
            "justification": justification,
            "product_area": product_area,
        }

    @staticmethod
    def _format_response(result: RetrievalResult, query: str = "") -> str:
        # Extract relevant snippet from document
        doc_content = result.document.content

        # Strip YAML frontmatter (everything between --- markers at start)
        if doc_content.startswith("---"):
            # Find the closing --- marker
            closing_marker = doc_content.find("\n---\n", 3)
            if closing_marker > 0:
                # Extract content after the YAML block
                doc_content = doc_content[closing_marker + 5:].strip()

        lines = []
        for raw_line in doc_content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("![") or line.startswith("|"):
                continue
            if line.startswith("<") or "<table" in line or "<td" in line or "<tr" in line:
                continue
            if line.startswith("_Last updated") or line.startswith("_Last modified"):
                continue
            if line.startswith("title:") or line.startswith("source_url:") or line.startswith("description:"):
                continue
            if line.startswith("#"):
                continue
            line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
            lines.append(line)

        query_terms = {
            term for term in re.findall(r"[a-z0-9][a-z0-9'-]{3,}", query.lower())
            if term not in {"please", "help", "hackerrank", "claude", "visa", "issue", "with", "from", "what", "where", "have", "this", "that", "your"}
        }
        if query_terms:
            scored_lines = []
            for idx, line in enumerate(lines):
                lowered = line.lower()
                score = sum(1 for term in query_terms if term in lowered)
                if score:
                    scored_lines.append((score, idx, line))
            if scored_lines:
                scored_lines.sort(key=lambda item: (-item[0], item[1]))
                start = scored_lines[0][1]
                window = lines[start:start + 5]
                text = " ".join(window)
            else:
                text = " ".join(lines)
        else:
            text = " ".join(lines)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            text = result.document.title

        if len(text) > 500:
            cut = text[:500].rsplit(".", 1)[0]
            if len(cut) < 180:
                cut = text[:500].rsplit(" ", 1)[0]
            text = cut.strip() + "..."
        return text
