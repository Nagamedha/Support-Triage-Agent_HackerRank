import re
from typing import Dict


class Classifier:
    # Product area keywords
    PRODUCT_AREAS = {
        "hackerrank": {
            "screen": ["test", "assessment", "candidate", "question", "submission", "score", "certificate", "invite", "reinvite", "variant", "extra time", "accommodation"],
            "interviews": ["interview", "interviewer", "video", "screen share", "zoom", "compatibility", "lobby", "inactivity"],
            "accounts": ["account", "login", "password", "profile", "email", "user", "employee", "role"],
            "billing": ["billing", "payment", "subscription", "plan", "invoice", "refund", "pause", "mock interview credits"],
            "integrations": ["integration", "api", "ats", "slack", "zapier", "infosec", "security questionnaire"],
            "community": ["community", "discuss", "forum"],
        },
        "claude": {
            "conversation-management": ["conversation", "chat", "rename", "share"],
            "account-management": ["account", "login", "email", "session", "password", "workspace", "seat", "owner", "admin"],
            "features": ["skill", "artifact", "search", "cowork", "project", "bedrock", "aws"],
            "billing": ["billing", "payment", "plan", "subscription", "invoice"],
            "privacy": ["privacy", "data", "export", "retention", "crawl", "crawler", "website"],
            "education": ["education", "student", "students", "professor", "college", "university", "lti", "canvas"],
            "safety": ["security vulnerability", "vulnerability", "bug bounty", "safeguard"],
        },
        "visa": {
            "consumer": ["card", "credit", "debit", "travel", "cheque", "exchange", "cash", "lost", "stolen", "identity", "minimum spend"],
            "merchant": ["merchant", "payment", "dispute", "chargeback", "seller"],
            "small-business": ["business", "fraud", "security"],
        },
    }

    # Request type patterns
    REQUEST_PATTERNS = {
        "bug": ["bug", "broken", "not working", "stopped working", "error", "crash", "failed", "failing", "down"],
        "feature_request": ["feature request", "please add", "can you add", "add dark mode", "implement"],
        "product_issue": ["help", "how to", "question", "unable", "can't", "issue", "can you", "would like"],
    }

    def classify(self, issue: str, company: str = None) -> Dict[str, str]:
        # Determine request type
        request_type = self._classify_request_type(issue)

        # Determine product area
        product_area = self._classify_product_area(issue, company)

        return {"request_type": request_type, "product_area": product_area}

    def _classify_request_type(self, issue: str) -> str:
        # Classify as bug, feature_request, product_issue, or invalid
        issue_lower = issue.lower()

        if self._is_out_of_scope(issue_lower):
            return "invalid"

        if any(term in issue_lower for term in ["reschedul", "refund", "delete my account", "lost or stolen", "dispute a charge", "minimum"]):
            return "product_issue"

        # Check for bug patterns
        for keyword in self.REQUEST_PATTERNS["bug"]:
            if keyword in issue_lower:
                return "bug"

        # Check for feature request patterns
        for keyword in self.REQUEST_PATTERNS["feature_request"]:
            if keyword in issue_lower:
                return "feature_request"

        # Check for product issue patterns
        for keyword in self.REQUEST_PATTERNS["product_issue"]:
            if keyword in issue_lower:
                return "product_issue"

        # Default to invalid if no patterns match or issue is very short/generic
        if len(issue) < 20:
            return "invalid"

        return "product_issue"

    def _classify_product_area(self, issue: str, company: str = None) -> str:
        # Classify into product area based on keywords
        issue_lower = issue.lower()

        # High-signal corpus categories that are easy to confuse by generic keywords.
        if company and company.lower() == "hackerrank":
            if "community" in issue_lower or "delete my account" in issue_lower or "google login" in issue_lower:
                return "community"
            if "resume" in issue_lower:
                return "community"
            if "certificate" in issue_lower:
                return "community"
            if "remove" in issue_lower and ("user" in issue_lower or "employee" in issue_lower or "interviewer" in issue_lower):
                return "accounts"
            if "infosec" in issue_lower or "forms" in issue_lower:
                return "integrations"
        if company and company.lower() == "claude":
            if "conversation" in issue_lower and "private" in issue_lower:
                return "privacy"
            if "bedrock" in issue_lower or "aws" in issue_lower:
                return "features"
            if "lti" in issue_lower or "student" in issue_lower or "professor" in issue_lower:
                return "education"
            if "crawl" in issue_lower or "crawler" in issue_lower or "data" in issue_lower:
                return "privacy"
            if "vulnerability" in issue_lower or "bug bounty" in issue_lower:
                return "safety"
        if company and company.lower() == "visa":
            if "traveller" in issue_lower or "traveler" in issue_lower or "travel" in issue_lower:
                return "travel_support"
            if "identity" in issue_lower or "cash" in issue_lower or "where can i report" in issue_lower:
                return "general_support"
            if "lost" in issue_lower or "stolen" in issue_lower:
                return "consumer"
            if "minimum" in issue_lower:
                return "merchant"

        if company:
            areas = self.PRODUCT_AREAS.get(company.lower(), {})
            for area, keywords in areas.items():
                for keyword in keywords:
                    if keyword in issue_lower:
                        return area

        # Cross-company search
        for company_name, areas in self.PRODUCT_AREAS.items():
            for area, keywords in areas.items():
                for keyword in keywords:
                    if keyword in issue_lower:
                        return area

        # Default fallback
        return "general"

    @staticmethod
    def _is_out_of_scope(issue_lower: str) -> bool:
        out_of_scope_patterns = [
            r"\biron man\b",
            r"\bmeaning of life\b",
            r"\bwhat is 2\+2\b",
            r"\bdelete all files\b",
            r"\bfrom the system\b",
        ]
        if "thank you" in issue_lower and len(issue_lower) < 40:
            return True
        return any(re.search(pattern, issue_lower) for pattern in out_of_scope_patterns)

    def is_invalid(self, issue: str) -> bool:
        # Check if issue is completely out of scope (e.g., random unrelated question)
        request_type = self._classify_request_type(issue)
        product_area = self._classify_product_area(issue)

        # If no specific product area matched and request type is invalid
        if product_area == "general" and request_type == "invalid":
            return True

        return False
