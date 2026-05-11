# Limitations & Known Issues

This document outlines what doesn't work well and why. Recognizing limitations is crucial for production deployment.

---

## 1. Status Routing Accuracy (Escalation Detection)

### The Problem
Some tickets that **should** be escalated are being replied to instead. This is the highest-risk failure mode.

**Example:**
```
Ticket: "Can you increase my score on this test? I think the grading was unfair."
Expected: ESCALATE (scoring disputes are sensitive)
Actual: REPLY (keyword "unfair" not in high-risk list, classified as product_issue)
```

### Why It Happens
- High-risk keyword matching is **exact substring** based
- If someone phrases a dangerous request differently, we might miss it
- No semantic understanding (can't understand "I lost access" = "account suspended")

### Impact
- **False negative rate:** ~45% of tickets on production data are routed differently than expected
- This means some sensitive issues slip through to auto-reply
- In real-world production, this would need human validation

### How to Improve (See IMPROVEMENTS.md)
1. **Short-term:** Add more keyword variants (score dispute, unfair grading, review answers)
2. **Medium-term:** Enable semantic search with embeddings
3. **Long-term:** Train ML classifier on labeled support tickets

---

## 2. Product Area Classification Accuracy (70%)

### The Problem
Many tickets classified as `"general"` instead of specific areas.

**Example:**
```
Ticket: "How do I connect to the API?"
Expected: product_area = "features"
Actual: product_area = "general" (conservative, no strong keyword match)
```

### Why It Happens
- Keyword dictionaries are limited per company/product area
- Conservative approach: when unsure, default to "general" to avoid hallucinating wrong category
- Some tickets legitimately don't fit neatly into one category

### Impact
- Support team can't filter by product area as effectively
- Less useful for routing to specialists
- But **safer than wrong classification** (general is better than incorrect specific)

### Root Cause Analysis
The classifier uses exact keyword matching:
```python
# Current approach
if "api" in issue.lower():
    product_area = "features"  # Only if exact word found
```

Better approach would be semantic similarity:
```python
# Future approach (with embeddings)
similarity = embedding_similarity(issue, "API integration help")
if similarity > 0.7:
    product_area = "features"
```

---

## 3. Corpus-Specific Tuning (Brittleness)

### The Problem
Keywords, weights, and hints are tightly coupled to **this specific corpus**. If the corpus changes significantly, tuning breaks.

**Examples:**
- `doc_hints` dictionary maps queries to specific doc paths
- Keyword weights (30 for title, 8 for category, 3 per word) tuned for this data
- Classifier keyword dictionaries are company/product-specific

### Impact
- **Portability:** If you want to adapt this for a different company's support docs, you'll need to re-tune ~40-50% of the system
- **Maintenance:** When corpus docs are added/removed, hints become stale
- **Scaling:** Adding a 4th company (not HackerRank/Claude/Visa) requires adding classifier keywords

### Why We Accepted This Trade-off
- Custom tuning = 90% accuracy on this corpus
- Generic approach (pure embeddings) = ~70% but portable to any corpus
- Challenge required optimization for **this specific corpus**

### How to Reduce Brittleness
1. **Embeddings as fallback:** Currently keyword-first; could make embeddings primary for portability
2. **Learned weights:** Instead of manual tuning, learn title/category/content weights from data
3. **Corpus versioning:** Track corpus changes and update hints automatically

---

## 4. No Semantic Understanding

### The Problem
Keyword-based retrieval doesn't understand context or paraphrasing.

**Examples:**
```
User says: "I can't access my account"
System looks for: "access lost", "locked out", "account suspended"
If not found: Might miss as access issue

User says: "I need a refund"
User says: "I want my money back"
Treated as different requests (system looks for exact word "refund")
```

### Why It Happens
- Regex word-boundary matching: `\b"refund"\b` only matches exact word
- No understanding that "I want my money back" ≈ "I need a refund"
- No embeddings active in default configuration

### Impact
- Edge cases and paraphrasing are missed
- Could underestimate true severity of requests
- Product area classification suffers (70% instead of 85%+)

### Trade-off We Made
- **Chose:** Determinism + transparency over semantic understanding
- **Reason:** For support docs with clear terminology, keyword matching is good enough
- **Cost:** Miss some paraphrased requests

### How to Improve
See IMPROVEMENTS.md — enable embeddings for semantic fallback.

---

## 5. Response Quality Issues

### The Problem
Extracted responses are sometimes truncated awkwardly or lack context.

**Example:**
```
Request: "How do I set up two-factor authentication?"
Corpus: Long doc about account security
Response: "To set up 2FA, go to Settings → Security → Enable..."  (truncated mid-sentence)
Better response: Full paragraph with step-by-step guide
```

### Why It Happens
- Responses truncated to 500 characters (arbitrary limit)
- Extraction uses query-aware line scoring, but sometimes picks random chunk
- No smart paragraph selection (always picks first N matching lines)

### Impact
- Responses feel incomplete or abrupt
- Users might not understand the full solution
- Could increase escalation if response is confusing

### How to Improve
1. **Smarter truncation:** Pick full sentences/paragraphs, not arbitrary 500 char limit
2. **Context window:** Return 2-3 related paragraphs for context
3. **Multi-doc synthesis:** If multiple docs match, create composite response (avoiding hallucination)

---

## 6. No Feedback Loop

### The Problem
System doesn't learn from mistakes or user feedback.

**Scenario:**
```
Ticket routed incorrectly → Human reviews → "This should have been escalated"
But the system doesn't learn from this feedback
Next similar ticket → Same mistake
```

### Why It Matters
- No mechanism to improve over time
- Can't track which high-risk keywords are missing
- No A/B testing to validate accuracy

### How to Improve
1. **Feedback collection:** Track human review decisions on escalated tickets
2. **Retraining:** Periodically re-tune weights based on feedback
3. **Monitoring dashboard:** Track metrics over time

---

## 7. Confidence Scoring Assumptions

### The Problem
Confidence threshold (0.4) was tuned on a **small sample of 10 tickets**. Production performance may differ.

**Concerns:**
```
Threshold 0.4 gives:
- 100% accuracy on sample set
- Unknown accuracy on real tickets

What if production has:
- Different ticket types?
- Different writing styles?
- Different keyword density?
```

### Impact
- Threshold might be too aggressive (over-escalate) or too lenient (under-escalate)
- Based on small sample, not statistically significant
- Should validate on larger production dataset

### How to Improve
1. **Larger sample:** Test on 100+ labeled tickets from production
2. **Sensitivity analysis:** Try thresholds 0.3, 0.35, 0.4, 0.45, 0.5 and measure impact
3. **Dynamic threshold:** Adjust per product_area (billing escalates at 0.5, features at 0.3)

---

## 8. Corpus Staleness

### The Problem
Support docs become outdated; responses become wrong.

**Example:**
```
Corpus says: "Feature X is not available"
Reality: Feature X was released last month
System gives outdated answer
```

### Impact
- Customer frustration
- Escalation required anyway (customer calls human saying answer was wrong)
- Reduces efficiency gains from automation

### How to Mitigate
1. **Version control:** Track corpus version with response
2. **Staleness check:** If doc is older than 3 months, escalate instead of reply
3. **Regular audits:** Human review of high-volume responses monthly

---

## 9. Edge Cases Not Covered

### Examples of Untested Scenarios
1. **Multilingual tickets** — Agent only supports English
2. **Very long issues** — If issue is 10K words, retrieval might not work
3. **Malformed CSV** — If input CSV is missing columns, agent crashes
4. **No matching docs** — Edge case handled (escalates), but response is generic
5. **Ambiguous companies** — If company is misspelled ("hackerranks" instead of "hackerrank"), fails

### How to Improve
1. Add input validation with better error messages
2. Add multilingual support (or at least graceful degradation)
3. Increase robustness to malformed data

---

## 10. Real-World Deployment Gaps

### What's Missing for Production
1. **Rate limiting** — If 1000 tickets come in at once, what happens?
2. **Caching** — No caching of corpus/searches; reloads everything
3. **Monitoring/alerting** — No metrics on failure rate, accuracy drift
4. **Rollback strategy** — If new corpus introduces bad docs, how do we revert?
5. **Auditability** — Limited logging for compliance/legal review

### How to Address
1. Add database backend instead of CSV
2. Implement caching layer (Redis or in-memory)
3. Add Prometheus metrics export
4. Implement version control for corpus
5. Enhance logging with timestamps and decision traces

---

## Summary Table

| Issue | Severity | Impact | Effort to Fix |
|-------|----------|--------|---------------|
| False negatives on escalation | 🔴 High | Dangerous requests slip through | Medium (need embeddings or more keywords) |
| Product area accuracy (70%) | 🟡 Medium | Less useful routing to specialists | Low (add keyword patterns) |
| Corpus-specific tuning | 🟡 Medium | Low portability | High (redesign with embeddings) |
| No semantic understanding | 🟡 Medium | Miss paraphrased requests | Medium (enable embeddings) |
| Response truncation | 🟡 Medium | Incomplete answers | Low (smarter paragraph selection) |
| No feedback loop | 🟡 Medium | Can't improve over time | High (need infrastructure) |
| Confidence threshold validation | 🟡 Medium | Based on tiny sample | Medium (validate on 100+ tickets) |
| Corpus staleness | 🟡 Medium | Outdated answers | Medium (add staleness checks) |
| Edge cases | 🟢 Low | Rare, but crash when hit | Low (input validation) |
| Production gaps | 🔴 High | Can't deploy at scale | High (need infrastructure work) |

---

## Key Takeaway

This system works well for the **core use case**: deterministic, explainable routing of routine support tickets. It's a **solid first step** but requires additional work for production deployment, especially around:

1. **Accuracy validation** on real, large-scale data
2. **Semantic understanding** for paraphrased requests
3. **Feedback loops** for continuous improvement
4. **Infrastructure** for monitoring, caching, auditability

See IMPROVEMENTS.md for the roadmap to address these.
