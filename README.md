# Support Triage Agent

A deterministic support ticket triage system that automatically routes tickets to either self-reply or human escalation across three product domains: **HackerRank**, **Claude**, and **Visa**.

---

## 🎯 The Problem We Solved

**Support teams face a bottleneck:** Every incoming ticket requires human review and classification. As companies scale, this becomes expensive and slow. The challenge: automate ticket routing while maintaining safety (don't give bad advice) and transparency (explain every decision).

This agent solves it by:
1. **Retrieving** relevant support documentation from a 770-document corpus
2. **Classifying** the issue type and product area
3. **Routing** safely: escalate anything risky, reply only when confident
4. **Generating** corpus-grounded responses with zero hallucination

**Real-world impact:** Companies like HackerRank, Claude, and Visa handle thousands of support tickets daily. Automating 50% of safe, routine requests (with 100% accuracy) saves operational costs and frees teams to focus on complex issues.

---

## 🏗️ Architecture

```
Input CSV (issue, subject, company)
    ↓
[1] Corpus Loader
    └─ Loads 770 markdown documents (321 Claude, 436 HackerRank, 13 Visa)
    ↓
[2] Retriever
    └─ Keyword search (deterministic, cost-free)
    └─ Scores: title (30 pts) + category (8 pts) + content (3 pts/word)
    └─ Returns top-3 docs with confidence 0-1
    ↓
[3] Classifier
    └─ Pattern-based detection (no ML)
    └─ Identifies: request_type (bug/feature/product_issue/invalid)
    └─ Identifies: product_area (domain-specific categories)
    ↓
[4] Router (Escalation Logic)
    ├─ Check 1: High-risk keywords? → ESCALATE
    ├─ Check 2: No relevant docs? → ESCALATE
    ├─ Check 3: Confidence < 0.4? → ESCALATE
    └─ Otherwise: REPLY with corpus-grounded response
    ↓
[5] Response Generator
    └─ Strips YAML frontmatter
    └─ Cleans markdown formatting
    └─ Extracts relevant lines (query-aware scoring)
    └─ Truncates to 500 characters
    ↓
Output CSV (status, product_area, response, justification, request_type)
```

---

## 🤔 Why This Architecture?

### **Design Decision 1: Keyword Search Over LLM/Embeddings**

**What we chose:** Hybrid approach—keyword search primary, embeddings fallback (optional).

**Why:**
- ✅ **Deterministic** — Same query always produces same output (reproducible)
- ✅ **Cost-free** — No API calls needed for most cases
- ✅ **Transparent** — Easy to explain why a doc matched
- ✅ **Fast** — Instant retrieval from corpus
- ✅ **Safe** — For support docs with clear terminology, keyword matching is good enough

**Trade-off we accepted:**
- ❌ Misses semantic understanding (e.g., "I can't login" vs "access lost" treated as different)
- **Mitigation:** Explicit keyword lists for high-risk concepts

**What we rejected:**
- Pure ML/embeddings: Non-deterministic, expensive, hard to debug
- Pure LLM: Hallucination risk (we give wrong advice)

---

### **Design Decision 2: Explicit High-Risk Keywords Over ML Risk Detector**

**What we chose:** Hardcoded list of 17+ keywords that always escalate.

**High-Risk Keywords:**
- Financial: refund, payment, billing, invoice, order id
- Security: fraud, identity theft, security breach, vulnerability
- Destructive: delete account, remove data, wipe, erase
- Scoring: score dispute, unfair, review my answers
- Access: access lost, locked out, can't login, account suspended
- Outages: site is down, all requests failing
- Permissions: permissions, access level
- Policy disclosure: infosec, security questionnaire

**Why:**
- ✅ **Safe by default** — Humans review anything sensitive
- ✅ **Transparent** — No black-box model
- ✅ **Fast** — Simple regex check
- ✅ **Correct** — We know these are always risky

**Trade-off:**
- ❌ May over-escalate non-risky tickets that contain these words
- **Accepted because:** Better safe than sorry in support context

---

### **Design Decision 3: Modular Architecture**

**What we chose:** 5 separate modules (corpus_loader, retriever, classifier, router, agent).

**Why:**
- ✅ **Testable** — Unit tests for each module
- ✅ **Debuggable** — Isolate where failures occur
- ✅ **Maintainable** — Clear separation of concerns
- ✅ **Evolvable** — Can swap implementations (add embeddings later without rewriting everything)

---

### **Design Decision 4: Pattern-Based Classification (Not ML)**

**What we chose:** Keyword dictionaries per company/product area.

**Why:**
- ✅ Fast, deterministic, explainable
- ✅ No training data needed
- ✅ Easy to debug (see which keywords matched)

**Trade-off:**
- ❌ Lower accuracy on product area (70% vs 100%)
- **Reason:** Conservative approach to avoid hallucinating wrong categories

---

## 📊 Performance & Accuracy

### Sample Dataset (10 labeled tickets):
- **Status routing:** 100% accuracy (correct replied/escalated decision)
- **Product area detection:** 70% accuracy (many default to "general" to be conservative)
- **Request type classification:** 100% accuracy (bug/feature/product_issue detection)
- **Overall:** 90% accuracy

### Production Run (29 real tickets):
- 16 replied (55.2%) — Safe, routine questions
- 13 escalated (44.8%) — Sensitive, risky, or unclear issues
- 0 hallucinations (all responses 100% from corpus)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- No external dependencies (stdlib only)

### Installation
```bash
git clone https://github.com/Nagamedha/Support-Triage-Agent_HackerRank.git
cd Support-Triage-Agent_HackerRank

# Verify setup
python3 -c "from code.agent import TriageAgent; print('✓ Ready')"
```

### Run the Agent
```bash
python3 code/main.py
```

This will:
- Load 770 documents from `data/`
- Read tickets from `support_tickets/support_tickets.csv`
- Write predictions to `support_tickets/output.csv`

### Run Tests
```bash
# Unit tests
python3 tests/test_corpus_loader.py
python3 tests/test_retriever.py
python3 tests/test_classifier.py
python3 tests/test_router.py

# Integration test (end-to-end)
python3 tests/test_integration.py

# Regression test (accuracy on labeled sample)
python3 tests/test_regression.py
```

---

## 📁 Project Structure

```
code/
├── main.py              # Entry point
├── agent.py             # Orchestrator (calls retriever → classifier → router)
├── corpus_loader.py     # Loads 770 documents from data/
├── retriever.py         # Keyword search + optional embeddings
├── classifier.py        # Request type & product area detection
└── router.py            # Escalation logic & response generation

support_tickets/
├── support_tickets.csv  # Input: 29 real support tickets
└── output.csv           # Output: predictions (status, product_area, response, etc.)

tests/
├── test_corpus_loader.py
├── test_retriever.py
├── test_classifier.py
├── test_router.py
├── test_integration.py
└── test_regression.py

data/
├── claude/              # 321 Claude docs
├── hackerrank/          # 436 HackerRank docs
└── visa/                # 13 Visa docs
```

---

## 🔍 How It Works: Step-by-Step Example

**Incoming ticket:**
```
Issue: "I need a refund for my subscription"
Subject: "Payment Issue"
Company: "HackerRank"
```

**Step 1: Retrieve relevant docs**
- Search corpus for "refund", "payment", "subscription"
- Find: billing FAQs, refund policies, payment guides
- Confidence: 0.75 (strong title + category match)

**Step 2: Classify**
- Detect request_type: "product_issue" (payment-related)
- Detect product_area: "billing" (HackerRank billing keywords matched)

**Step 3: Route (Escalation Decision Tree)**
- Check high-risk keywords: **FOUND "refund"** ⚠️
- **Decision: ESCALATE** (humans must handle refund requests)

**Step 4: Output**
```
status: escalated
product_area: billing
response: "I can't safely resolve this directly. A support specialist will handle it."
justification: "Sensitive or high-risk request detected: 'refund'. Requires human review."
request_type: product_issue
```

---

## 🧪 Testing Strategy

**Level 1: Unit Tests**
- Test each module independently
- Corpus loader: Does it load 770 documents correctly?
- Retriever: Does keyword scoring work?
- Classifier: Does pattern matching detect request types?
- Router: Does escalation logic catch high-risk keywords?

**Level 2: Integration Test**
- End-to-end pipeline: CSV input → CSV output
- Does output have correct columns and format?

**Level 3: Regression Test**
- Test against labeled sample (10 tickets with ground truth)
- Measure accuracy on status, product area, request type
- Result: 90% overall accuracy

---

## 📈 Results & Evaluation

### What Worked Well ✅
- **Status routing:** 100% accuracy on sample set
- **Request type detection:** 100% accuracy
- **Zero hallucinations:** All responses from corpus only
- **Fast & cost-free:** No API calls, instant decisions
- **Explainable:** Can trace every decision to source

### What Needs Improvement ⚠️
See [LIMITATIONS.md](./LIMITATIONS.md) for detailed analysis.

---

## 🔮 How to Make It Better

See [IMPROVEMENTS.md](./IMPROVEMENTS.md) for tier-based roadmap:
- **Tier 1 (1-2 weeks):** Add more keyword patterns, improve product area detection
- **Tier 2 (1 month):** Enable semantic search with embeddings
- **Tier 3 (3+ months):** ML-based risk classifier, feedback loop integration

---

## 🤖 How AI (Claude Code) Helped

See [HOW_AI_HELPED.md](./HOW_AI_HELPED.md) for detailed explanation of:
- What Claude built (scaffolding, modules, tests)
- What you guided (architecture decisions, high-risk keywords, bug fixes)
- How you stayed in control (approval gates, validation, documentation)

**TL;DR:** Claude handled implementation; you made all the design decisions.

---

## 📋 Output Format

Each row in `output.csv`:

| Column | Example | Meaning |
|--------|---------|---------|
| `status` | `replied` or `escalated` | Route decision |
| `product_area` | `billing`, `accounts`, `features` | Support category |
| `response` | "Here's how to refund..." | User-facing answer (max 500 chars) |
| `justification` | "Grounded in HackerRank docs" | Why this decision |
| `request_type` | `bug`, `feature_request`, `product_issue`, `invalid` | Issue classification |

---

## 🛠️ Troubleshooting

**"Corpus not found"**
```bash
# Make sure you're in repo root
cd /path/to/Support-Triage-Agent_HackerRank
python3 code/main.py
```

**"No output generated"**
```bash
# Check input CSV exists
ls support_tickets/support_tickets.csv
```

**Test failures**
```bash
# Run individual test for diagnostics
python3 tests/test_regression.py -v
```

---

## 🧠 Key Design Insights

1. **Determinism beats intelligence for compliance:** Support triage needs reproducible, explainable decisions. A simple, clear system beats a powerful black box.

2. **Safety-first escalation:** Better to over-escalate risky tickets than under-escalate (miss dangerous ones).

3. **Modular design = evolvability:** Built as 5 independent modules so you can improve one (e.g., add embeddings) without rewriting others.

4. **Testing iteratively:** Started with basic accuracy (66.7%), improved to 90% by testing against real tickets and fixing edge cases.

5. **Explicit is better than implicit:** Hardcoded high-risk keywords are better than training a model when the rules are clear.

---

## 📚 Learn More

- **CONTEXT.md** — Technical deep-dive (all module details, confidence scoring, etc.)
- **LIMITATIONS.md** — What doesn't work and why
- **IMPROVEMENTS.md** — Future roadmap
- **HOW_AI_HELPED.md** — How AI assisted in building this

---

## 📝 License

MIT License — feel free to adapt for your own support corpus.

---

## 🎓 Lessons Learned

This project taught me that:
- A well-designed simple system beats a complex black box
- Transparency and explainability matter more than raw accuracy
- Modular architecture scales better than monolithic code
- Real-world validation is essential (tested on actual tickets, not just theory)
- Trade-offs are unavoidable; own them instead of hiding them

Built during **HackerRank Orchestrate (May 2026)** — A 2-day challenge to build an AI-assisted system under real constraints.

---

**Questions?** See LIMITATIONS.md or IMPROVEMENTS.md for detailed discussions.
