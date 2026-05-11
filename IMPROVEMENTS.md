# Improvement Roadmap

This document outlines how to improve the system, organized by scope and effort.

---

## 🎯 Quick Wins (1-2 weeks, Low effort)

### 1. Expand High-Risk Keywords
**Effort:** 1 day | **Impact:** Reduce false negatives on escalation

Add more keyword variants for high-risk patterns:
```python
HIGH_RISK_KEYWORDS = [
    # Financial (add variants)
    "refund", "reimbursement", "money back", "charge dispute",
    "payment issue", "billing problem", "invoice dispute",
    
    # Access (add variants)
    "locked out", "can't login", "access denied", "account suspended",
    "forgot password", "reset password", "locked out",
    
    # Scoring (add variants)
    "score dispute", "grade appeal", "unfair grading", "wrong score",
    "challenge my score", "review my answers",
    
    # More security patterns
    "my account was hacked", "unauthorized access", "suspicious activity",
    "leaked credentials", "data breach", "privacy concern",
]
```

**Test:** Run regression test before/after to measure improvement.

---

### 2. Improve Product Area Classification
**Effort:** 3-5 days | **Impact:** From 70% → 80% accuracy

Expand keyword dictionaries with more patterns per company:

```python
# HackerRank
HACKERRANK_KEYWORDS = {
    "screen": ["screen", "failed test", "time limit", "code editor", "ide"],
    "interviews": ["interview", "mock interview", "preparation", "interview prep"],
    "accounts": ["account", "profile", "username", "login", "subscription"],
    "billing": ["refund", "payment", "invoice", "subscription", "charge"],
}

# Claude
CLAUDE_KEYWORDS = {
    "account-management": ["login", "password", "subscription", "billing"],
    "conversation-management": ["chat", "conversation", "history", "clear"],
    "features": ["features", "api", "integration", "connector"],
}
```

**Before:** "How do I use the API?" → "general"  
**After:** "How do I use the API?" → "features" (API keyword added)

---

### 3. Better Response Truncation
**Effort:** 2-3 days | **Impact:** More complete, better-formatted responses

Instead of hard 500-char limit:
```python
def _format_response(self, result: RetrievalResult, query: str) -> str:
    # Extract full paragraphs, not arbitrary chunks
    
    # Find query-relevant paragraphs
    paragraphs = result.document.content.split("\n\n")
    scored_paragraphs = []
    
    for para in paragraphs:
        score = sum(1 for term in query_terms if term in para.lower())
        if score > 0:
            scored_paragraphs.append((score, para))
    
    # Pick best 2-3 paragraphs (not arbitrary 500 chars)
    if scored_paragraphs:
        scored_paragraphs.sort(reverse=True)
        response = "\n\n".join([p for _, p in scored_paragraphs[:2]])
    else:
        response = result.document.title
    
    # Truncate at sentence boundary, not mid-word
    if len(response) > 500:
        response = response[:500].rsplit(".", 1)[0] + "."
    
    return response
```

**Test:** Verify responses are complete and sensible.

---

### 4. Add Input Validation
**Effort:** 1-2 days | **Impact:** Better error handling

```python
def validate_ticket(self, ticket):
    required_fields = ["issue", "subject", "company"]
    for field in required_fields:
        if field not in ticket:
            raise ValueError(f"Missing field: {field}")
    
    if ticket["company"].lower() not in ["hackerrank", "claude", "visa"]:
        raise ValueError(f"Unknown company: {ticket['company']}")
    
    if len(ticket["issue"]) < 10:
        raise ValueError("Issue too short (min 10 chars)")
    
    if len(ticket["issue"]) > 10000:
        raise ValueError("Issue too long (max 10000 chars)")
```

---

## 🔧 Medium-Term Improvements (1 month, Medium effort)

### 5. Enable OpenAI Embeddings (Already coded, just activate)
**Effort:** 3-5 days (integration + testing) | **Impact:** Semantic understanding

The code already has embeddings fallback in `retriever.py`. Just:

1. Uncomment embeddings code
2. Test on sample set
3. Compare keyword-only vs hybrid accuracy

**Before:**
```
Query: "I lost my password"
Keyword match: No exact "access" keyword → Escalate
```

**After with embeddings:**
```
Query: "I lost my password"
Keyword match: No match (escalate as fallback)
Embedding match: High similarity to "account recovery" → Reply with docs
```

**Trade-off:** Costs $$$ per API call, non-deterministic, but better semantic understanding.

---

### 6. Add Feedback Loop Infrastructure
**Effort:** 2 weeks | **Impact:** System learns over time

```python
# New: feedback_log.csv
# Columns: ticket_id, system_decision, human_correction, reason, timestamp

def log_feedback(self, ticket_id, system_decision, human_correction, reason):
    """Log when human disagrees with system decision"""
    with open("feedback_log.csv", "a") as f:
        f.write(f"{ticket_id},{system_decision},{human_correction},{reason}\n")

def analyze_feedback(self):
    """Weekly: analyze feedback to identify missed patterns"""
    # Find high-risk keywords we're missing
    missed_escalations = [row for row in feedback if 
                         row['system_decision'] == 'replied' and 
                         row['human_correction'] == 'escalated']
    
    # Extract keywords from missed_escalations
    # Add to HIGH_RISK_KEYWORDS list
    # Re-test and validate
```

---

### 7. Add Monitoring & Metrics
**Effort:** 1 week | **Impact:** Track performance over time

```python
import json
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "total_tickets": 0,
            "escalated_count": 0,
            "replied_count": 0,
            "high_risk_keywords_triggered": {},
            "product_area_distribution": {},
            "confidence_scores": [],
            "timestamp": None,
        }
    
    def record_routing(self, ticket, result):
        self.metrics["total_tickets"] += 1
        self.metrics["timestamp"] = datetime.now().isoformat()
        
        if result["status"] == "escalated":
            self.metrics["escalated_count"] += 1
            keyword = result["justification"].split("'")[1]  # Extract keyword
            self.metrics["high_risk_keywords_triggered"][keyword] = \
                self.metrics["high_risk_keywords_triggered"].get(keyword, 0) + 1
        else:
            self.metrics["replied_count"] += 1
        
        # Track product area distribution
        area = result["product_area"]
        self.metrics["product_area_distribution"][area] = \
            self.metrics["product_area_distribution"].get(area, 0) + 1
        
        # Track confidence
        if result.get("confidence"):
            self.metrics["confidence_scores"].append(result["confidence"])
    
    def export_metrics(self, filepath="metrics.json"):
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)
```

**Benefits:**
- See which high-risk keywords are triggering most
- Track escalation rate over time (should be stable ~40-50%)
- Monitor confidence score distribution

---

### 8. Support Multiple Corpora
**Effort:** 1 week | **Impact:** Adapt for other companies

```python
# Current: hardcoded data/
corpus_loader = CorpusLoader(corpus_path="data/")

# Future: configurable
corpus_loader = CorpusLoader(corpus_path="data/slack/")  # New company
corpus_loader = CorpusLoader(corpus_path="data/stripe/") # Another company
```

Requires:
- Dynamic classifier keyword dictionaries
- Per-corpus confidence thresholds
- Per-corpus high-risk keyword customization

---

## 🚀 Long-Term Improvements (3+ months, High effort)

### 9. ML-Based Risk Classifier
**Effort:** 4-6 weeks | **Impact:** Higher accuracy on false negatives

```python
# Instead of keyword matching, train a classifier
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class RiskClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    def train(self, tickets, labels):
        """
        tickets: list of issue texts
        labels: list of 0 (safe) / 1 (escalate)
        """
        X = self.vectorizer.fit_transform(tickets)
        self.model.fit(X, labels)
    
    def predict_risk(self, issue):
        """Return probability that issue should be escalated"""
        X = self.vectorizer.transform([issue])
        probability = self.model.predict_proba(X)[0][1]
        return probability
```

**Requires:** 
- 500+ labeled examples (safe vs escalate)
- Regular retraining as patterns emerge
- A/B testing against keyword baseline

**Benefits:**
- Catch nuanced high-risk patterns
- Learn from feedback automatically
- Higher accuracy than static keywords

---

### 10. Multi-Doc Response Synthesis
**Effort:** 3-4 weeks | **Impact:** More complete answers

```python
# Instead of single best doc, synthesize from multiple sources
# WITHOUT hallucinating (all text from corpus)

def synthesize_response(self, retrieved_docs: List[RetrievalResult], query: str) -> str:
    """Combine multiple docs into coherent response"""
    
    # Extract relevant sections from top 3 docs
    sections = []
    for doc in retrieved_docs[:3]:
        relevant_paragraphs = self._extract_relevant_paragraphs(doc, query)
        sections.extend(relevant_paragraphs)
    
    # Organize: intro → how-to → details → contact support
    intro = self._find_intro_section(sections)
    steps = self._find_step_by_step(sections)
    details = self._find_supporting_details(sections)
    
    # Synthesize (all text from corpus, no hallucination)
    response = f"{intro}\n\n{steps}\n\n{details}"
    
    # Truncate to 1000 chars (more room for complex answers)
    return self._truncate_intelligently(response)
```

**Benefit:** Users get complete, well-organized answers from multiple sources.

---

### 11. A/B Testing Framework
**Effort:** 2 weeks | **Impact:** Validate improvements before deployment

```python
class ABTestingFramework:
    def __init__(self):
        self.control_group = []  # Current system
        self.treatment_group = []  # New system variant
    
    def route_ticket(self, ticket):
        """Route with random assignment to control/treatment"""
        if random.random() < 0.5:
            result = self.route_with_current_system(ticket)
            self.control_group.append((ticket, result))
        else:
            result = self.route_with_new_system(ticket)
            self.treatment_group.append((ticket, result))
        
        return result
    
    def compare_results(self):
        """Measure accuracy difference"""
        control_accuracy = self._measure_accuracy(self.control_group)
        treatment_accuracy = self._measure_accuracy(self.treatment_group)
        
        improvement = treatment_accuracy - control_accuracy
        if improvement > 0.05:  # 5% improvement threshold
            return "Deploy treatment"
        else:
            return "Keep control"
```

---

### 12. Real-Time Corpus Updates
**Effort:** 2-3 weeks | **Impact:** No more stale docs

```python
# Watch for corpus changes and reload automatically
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CorpusWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".md"):
            print(f"Corpus updated: {event.src_path}")
            self.corpus_loader.reload()  # Reload all docs
            self.cache.clear()  # Clear response cache
            print("✓ Corpus reloaded and cache cleared")

observer = Observer()
observer.schedule(CorpusWatcher(), path="data/", recursive=True)
observer.start()
```

---

## 📊 Impact Roadmap

```
Week 1-2   [Quick Wins]          Expand keywords, better truncation    → 75% → 85% accuracy
Week 3-4   [Medium Term]         Feedback loop, monitoring             → 85% → 88% accuracy
Month 2    [ML Classifier]       Risk detection from data              → 88% → 92% accuracy
Month 3    [Synthesis]           Multi-doc responses                   → 92% → 94% accuracy
Month 4+   [Real-time updates]   Live corpus sync, A/B testing         → 94% → 96%+ accuracy
```

---

## 🏆 Success Metrics

Track these as you improve:

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Status routing accuracy | 100% (sample) | 95%+ (production) | Month 1 |
| Product area accuracy | 70% | 85% | Week 2 |
| False negative rate | ~45% | <10% | Month 2 |
| Response relevance | Manual check | 90%+ (user ratings) | Month 3 |
| Escalation rate | 44.8% | 30-40% (optimal) | Month 2 |
| System availability | Single process | 99.9% uptime | Month 4 |
| Cost per ticket | Free | <$0.01 (with embeddings) | Month 2 |

---

## 🎓 Implementation Priority

**If you have 2 weeks:**
- ✅ Expand keywords (quick win)
- ✅ Better response formatting
- ✅ Input validation
- ✅ Enable embeddings (fallback)

**If you have 1 month:**
- ✅ All of above
- ✅ Feedback loop infrastructure
- ✅ Monitoring/metrics
- ✅ A/B testing setup

**If you have 3+ months:**
- ✅ All of above
- ✅ ML risk classifier
- ✅ Multi-doc synthesis
- ✅ Real-time corpus updates
- ✅ Production deployment (database, caching, auditability)

---

## 🔗 See Also

- **LIMITATIONS.md** — What doesn't work and why
- **README.md** — Overview and quick start
- **CONTEXT.md** — Technical deep-dive

---

**Remember:** Better is the enemy of good. Start with quick wins, measure impact, then tackle medium-term improvements. Only pursue long-term rewrites if the ROI justifies the effort.
