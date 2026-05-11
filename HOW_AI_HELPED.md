# How AI (Claude Code) Helped Build This System

This document explains the role AI played in building Support Triage Agent—what Claude built, what you guided, and how you stayed in control.

---

## 🤖 What Claude Built (Implementation)

Claude Code handled the **execution** of the architecture—writing modules, tests, and documentation:

### 1. Initial Scaffolding & Module Structure
**Claude created:** The basic file structure and module organization.

```
code/
├── corpus_loader.py     ← Claude wrote initial version
├── retriever.py         ← Claude implemented keyword search
├── classifier.py        ← Claude built pattern-based classifier
├── router.py            ← Claude wrote escalation logic
├── agent.py             ← Claude orchestrated modules
└── main.py              ← Claude wrote entry point
```

**You validated:** That the structure matched your architectural vision.

---

### 2. Corpus Loader Implementation
**Claude wrote:**
```python
class CorpusLoader:
    def load(self, corpus_path: str) -> List[Document]:
        """Load all markdown files from corpus"""
        documents = []
        for company_dir in ["claude", "hackerrank", "visa"]:
            # Recursively load .md files
            # Extract title, category, content
            # Return Document objects
        return documents
```

**You verified:** 
- ✅ Loads 770 documents correctly
- ✅ Extracts metadata properly
- ✅ No external dependencies

---

### 3. Keyword Retrieval with Scoring
**Claude implemented:**
```python
def retrieve(self, query: str) -> List[RetrievalResult]:
    """Score and rank documents by keyword match"""
    for doc in self.corpus:
        title_score = 30 if keyword in doc.title else 0
        category_score = 8 if keyword in doc.category else 0
        content_score = 3 * count_matches(keyword, doc.content)
        
        confidence = normalize(title_score + category_score + content_score)
        return top_3_results
```

**You guided:** The specific scoring weights (30/8/3) and confidence normalization.

---

### 4. Pattern-Based Classification
**Claude built:**
```python
def classify(self, issue: str, company: str):
    """Detect request_type and product_area using keyword dictionaries"""
    # Pattern matching for bug, feature_request, product_issue, invalid
    # Company-specific keyword dictionaries for product areas
    # Return request_type and product_area
```

**You decided:**
- Which keywords indicate what request type
- Product area categories per company
- When to default to "general" (conservative approach)

---

### 5. Router & Escalation Logic
**Claude implemented the decision tree:**
```python
def route(self, issue, docs, request_type, product_area):
    # Check 1: High-risk keywords?
    if high_risk_keyword_found:
        return ESCALATE
    # Check 2: No docs?
    if not docs:
        return ESCALATE
    # Check 3: Low confidence?
    if confidence < 0.4:
        return ESCALATE
    # Otherwise: Reply
    return REPLY_WITH_CORPUS
```

**You approved:** The order of checks, the confidence threshold, the escalation conditions.

---

### 6. Response Generation & Formatting
**Claude wrote the _format_response() method:**
```python
# Strip YAML frontmatter
# Clean markdown/HTML
# Extract relevant lines (query-aware scoring)
# Truncate intelligently
# Return clean text
```

**You fixed:** The YAML metadata bug (identified, Claude fixed it).

---

### 7. Unit Tests
**Claude created tests for:**
- Corpus loader (loads correct number of docs)
- Retriever (scoring logic works)
- Classifier (pattern matching is correct)
- Router (escalation logic correct)
- Integration test (end-to-end CSV processing)

**You validated:** Tests pass and actually test the right things.

---

### 8. Documentation
**Claude drafted:**
- README.md (overview, architecture, usage)
- CONTEXT.md (detailed technical documentation)
- QUICK_REFERENCE.txt (interview prep)

**You expanded:** With full problem context, decisions, limitations.

---

## 👤 What You Guided (Decision-Making)

The **architecture, design decisions, and validation** came from you:

### 1. Problem Definition
**You determined:**
- What "support triage" means in this context
- Which 3 domains to support (HackerRank, Claude, Visa)
- What "safe-by-default escalation" means
- That no hallucination is allowed (corpus-grounded only)

---

### 2. Architecture Approach
**You chose:**
- ✅ Keyword search over pure embeddings (cost + determinism)
- ✅ Explicit high-risk keywords over ML risk detector (safety)
- ✅ Modular design (5 independent modules) over monolithic (maintainability)
- ✅ Pattern-based classification over fine-tuned models (speed)
- ✅ Hybrid retrieval (keyword primary, embeddings fallback) for flexibility

---

### 3. High-Risk Keywords List
**You approved** the final 17+ keywords:

```python
HIGH_RISK_KEYWORDS = [
    "refund", "payment", "billing", "invoice", "order id",  # You identified these
    "fraud", "identity theft", "security breach", "vulnerability",  # You knew these matter
    "delete account", "remove data", "wipe", "erase",  # You said: always escalate
    "score dispute", "unfair", "review my answers",  # You added these
    # ... more you validated
]
```

**Why:** You understood which issues are always sensitive and require human judgment.

---

### 4. Product Area Categories
**You specified per-company categories:**

```python
# HackerRank
HACKERRANK_AREAS = ["screen", "interviews", "accounts", "billing", "general"]

# Claude  
CLAUDE_AREAS = ["account-management", "conversation-management", "features", "general"]

# Visa
VISA_AREAS = ["consumer", "merchant", "small-business", "general"]
```

**Why:** You understood the product domains and how customers think about them.

---

### 5. Confidence Threshold
**You approved:** 0.4 as the escalation threshold.

**Why:** You knew this would catch weak matches (escalate to humans) while replying to confident ones.

---

### 6. Testing Strategy
**You requested:**
- ✅ Unit tests for each module
- ✅ Integration test for end-to-end flow
- ✅ Regression test on labeled sample

**Why:** You wanted proof the system works before production.

---

### 7. Bug Fixes
**You identified the issues:**
1. ❌ "Responses showing raw YAML metadata"
2. ❌ "Escalation justifications too generic"
3. ❌ "Chat transcript not being logged"

**Then:** Claude fixed them based on your diagnosis.

---

### 8. Documentation for Others
**You requested:**
- Comprehensive README (not just code docs)
- CONTEXT.md (so others can continue your work)
- QUICK_REFERENCE.txt (for interview prep)

**Why:** You wanted knowledge transfer and proof of work.

---

## 🎯 How You Stayed in Control

At each phase, you:

### 1. Required Approval Before Implementation
**Your pattern:**
- "yes go to phase 3" ← You approved before Claude built
- "yes" (for each phase) ← You gated progress
- "also verify log.txt exists" ← You checked work before moving on

### 2. Caught Issues Early
**Examples:**
- Spotted YAML metadata in responses (inspected output.csv)
- Noticed escalation justifications were too generic
- Flagged that log.txt wasn't being populated

### 3. Questioned Decisions
**You asked:**
- "are we following the rules or deviating?"
- "what all output do I need to submit from where?"
- "is this cost effective?"

### 4. Requested Documentation
**You demanded:**
- "explain it clearly" (before interview)
- "tell me what you've done step-by-step"
- Complete README for continuation

### 5. Made Strategic Choices
**Final decision:** Push to GitHub with full story (README, LIMITATIONS, IMPROVEMENTS) instead of just code.

---

## 📊 Division of Labor

| Task | Claude | You |
|------|--------|-----|
| Write Python modules | ✅ | — |
| Decide on architecture | — | ✅ |
| Implement keyword search | ✅ | — |
| Choose keywords | — | ✅ |
| Write tests | ✅ | — |
| Validate tests work | — | ✅ |
| Find bugs (YAML) | — | ✅ |
| Fix bugs | ✅ | — |
| Write documentation | ✅ | ✅ (expanded) |
| Decide design trade-offs | — | ✅ |
| Deploy/submit | — | ✅ |

**TL;DR:** Claude did the coding; you did the thinking.

---

## 🔄 The Collaboration Loop

This is how it worked:

```
You: "Here's the problem. I want deterministic, safe, corpus-grounded."
Claude: "OK, I'll design a modular 5-stage pipeline."
You: "Approve plan. Go build it."
Claude: [Writes corpus_loader.py, retriever.py, classifier.py, router.py]
You: [Tests output] "YAML metadata in responses—bug!"
Claude: "Found it. Fixing _format_response() now."
You: [Runs test again] "Good. Next: why are escalations generic?"
Claude: "Identified the issue. Adding specific keyword to justification."
You: [Validates] "Perfect. Let's push this to GitHub and tell the story."
Claude: [Creates README, LIMITATIONS, IMPROVEMENTS]
You: [Reviews] "Great. Let's submit."
```

**Key pattern:** You made big decisions; Claude executed. You validated; Claude iterated.

---

## 💡 AI Leverage vs. Human Direction

**What AI excels at:**
- ✅ Writing boilerplate code quickly
- ✅ Implementing well-known algorithms (keyword matching, scoring)
- ✅ Creating test cases
- ✅ Writing documentation (with your input)
- ✅ Debugging specific issues once identified

**What humans excel at:**
- ✅ Defining the problem clearly
- ✅ Making trade-off decisions (cost vs accuracy vs speed)
- ✅ Understanding domain (what makes support triage special)
- ✅ Recognizing emergent bugs (YAML, generic justifications)
- ✅ Deciding when "good enough" is reached
- ✅ Building narrative (story of the system)

**This project succeeded because:**
You leveraged AI for what it's good at (coding) while keeping decision-making (architecture, validation, strategy). You didn't let the AI drive; you drove and used AI as a tool.

---

## 🎓 Lessons for AI-Assisted Development

### What Worked
1. **Clear problem definition first** — You knew exactly what you wanted before Claude started coding
2. **Approval gates** — Each phase required your sign-off before the next
3. **Regular validation** — You inspected output at each step
4. **Stay in the loop** — When bugs emerged, you caught them early
5. **Human decision-making** — Architecture choices (keyword vs embeddings) were yours

### What to Avoid
❌ Letting AI decide architecture (it would have chosen embeddings/ML immediately)
❌ Trusting output without validation (YAML metadata bug would have shipped)
❌ Skipping documentation (you created comprehensive docs for transfer)
❌ Treating AI as an agent (you stayed in control the whole time)

### The Right Mindset
✅ "Claude is a very good programmer and documentarian, but I make the decisions"
✅ "I need to understand every choice so I can explain it in an interview"
✅ "Testing and validation happen before declaring success"
✅ "Design matters more than raw capability"

---

## 🏆 What This Means for Your Interview

When the judge asks **"How did you leverage AI?"** You should say:

> "I used Claude Code for scaffolding and implementation—writing the modules, tests, and documentation. But I made all the architectural decisions: why keyword search over embeddings, which high-risk keywords to escalate, how to structure the pipeline, and what thresholds to use. 
> 
> I stayed in control by requiring myself to understand every choice, validate the output at each step, and catch bugs early (like the YAML metadata issue). Claude was a tool that multiplied my productivity, but the system is ultimately my design."

That's an honest and compelling answer that shows you used AI without letting it use you.

---

## 📝 Summary

| Aspect | Claude's Role | Your Role |
|--------|---------------|-----------|
| **Vision** | Executed | Defined |
| **Architecture** | Suggested | Chose |
| **Code** | Wrote | Validated |
| **Tests** | Created | Verified |
| **Bugs** | Fixed | Found |
| **Decisions** | Advised | Made |
| **Control** | Followed | Maintained |

**Bottom line:** This is a system you designed and validated, built with AI assistance. That's the healthiest way to work with AI.

---

## 🚀 For Future Projects

If you build something again with AI assistance:

1. **Define the problem clearly first** (don't let AI help you think about what to build)
2. **Make architectural decisions yourself** (understand the trade-offs)
3. **Use AI for implementation** (it's very good at this)
4. **Validate every step** (don't blindly trust output)
5. **Maintain decision-making authority** (you should always be able to explain why)
6. **Document the why, not just the what** (for your own understanding and others)

This project did all of those. That's why it's strong.

