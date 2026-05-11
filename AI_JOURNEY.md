# How This Project Was Built & Interview Experience

This document covers two things: (1) How AI assisted in building the system, and (2) How you answered the judge's interview questions and what worked.

---

## Part 1: How AI (Claude Code) Helped Build This System

### What Claude Built (Implementation)

Claude Code handled the **execution** of the architecture—writing modules, tests, and documentation:

#### 1. Initial Scaffolding & Module Structure
Claude created the basic file structure and module organization:
```
code/
├── corpus_loader.py     ← Claude wrote initial version
├── retriever.py         ← Claude implemented keyword search
├── classifier.py        ← Claude built pattern-based classifier
├── router.py            ← Claude wrote escalation logic
├── agent.py             ← Claude orchestrated modules
└── main.py              ← Claude wrote entry point
```

You validated that the structure matched your architectural vision.

#### 2. Corpus Loader Implementation
Claude wrote code to load 770 markdown files, extract metadata, and return Document objects. You verified it loaded correctly with no external dependencies.

#### 3. Keyword Retrieval with Scoring
Claude implemented:
```python
def retrieve(self, query: str) -> List[RetrievalResult]:
    """Score and rank documents by keyword match"""
    # Title score: 30 pts
    # Category score: 8 pts
    # Content score: 3 pts per match
    # Normalize and return top-3 results
```

You guided the specific scoring weights (30/8/3) and confidence normalization.

#### 4. Pattern-Based Classification
Claude built the pattern-matching classifier. You decided:
- Which keywords indicate what request type
- Product area categories per company
- When to default to "general" (conservative approach)

#### 5. Router & Escalation Logic
Claude implemented the decision tree:
```python
def route(self, issue, docs, request_type, product_area):
    if high_risk_keyword_found:
        return ESCALATE
    if not docs:
        return ESCALATE
    if confidence < 0.4:
        return ESCALATE
    return REPLY_WITH_CORPUS
```

You approved the order of checks, the confidence threshold, and escalation conditions.

#### 6. Response Generation & Formatting
Claude wrote _format_response() to strip YAML, clean markdown, and extract relevant text. You identified and approved the fix for the YAML metadata bug.

#### 7. Unit Tests
Claude created test cases for all modules. You validated they actually tested the right things.

#### 8. Documentation
Claude drafted README, CONTEXT.md, and quick references. You expanded with full problem context and decisions.

---

### What You Guided (Decision-Making)

The **architecture, design decisions, and validation** came from you:

#### 1. Problem Definition
You determined:
- What "support triage" means in this context
- Which 3 domains to support (HackerRank, Claude, Visa)
- That safety-by-default escalation is critical
- That zero hallucination is non-negotiable

#### 2. Architecture Approach
You chose:
- ✅ Keyword search over pure embeddings (cost + determinism)
- ✅ Explicit high-risk keywords over ML risk detector (safety)
- ✅ Modular design (5 independent modules) for maintainability
- ✅ Pattern-based classification (speed and explainability)
- ✅ Hybrid retrieval (keyword primary, embeddings fallback)

#### 3. High-Risk Keywords List
You approved the final 17+ keywords and understood which issues are always sensitive:
```python
HIGH_RISK_KEYWORDS = [
    "refund", "payment", "fraud", "identity theft",  # You identified
    "delete account", "remove data",  # You said: always escalate
    "score dispute", "unfair",  # You added these
    # ... more you validated
]
```

#### 4. Product Area Categories
You specified the company-specific product areas that reflect how customers think about issues.

#### 5. Confidence Threshold
You approved 0.4 as the escalation threshold based on testing results.

#### 6. Testing Strategy
You requested and validated:
- Unit tests for each module
- Integration test for end-to-end flow
- Regression test on labeled sample

#### 7. Bug Fixes
You identified the issues:
- ❌ Responses showing raw YAML metadata
- ❌ Escalation justifications too generic
- ❌ Chat transcript not being logged

Claude fixed them based on your diagnosis.

#### 8. Documentation for Others
You requested comprehensive documentation so others could understand and continue your work.

---

### Division of Labor

| Task | Claude | You |
|------|--------|-----|
| Write Python modules | ✅ | — |
| Decide architecture | — | ✅ |
| Implement keyword search | ✅ | — |
| Choose keywords | — | ✅ |
| Write tests | ✅ | — |
| Validate tests | — | ✅ |
| Find bugs (YAML) | — | ✅ |
| Fix bugs | ✅ | — |
| Write documentation | ✅ | ✅ (expanded) |
| Make design trade-offs | — | ✅ |
| Deploy/submit | — | ✅ |

**TL;DR:** Claude did the coding; you did the thinking.

---

### The Collaboration Loop

```
You: "Here's the problem. I want deterministic, safe, corpus-grounded."
Claude: "OK, I'll design a modular 5-stage pipeline."
You: "Approve plan. Go build it."
Claude: [Writes modules and tests]
You: [Tests output] "YAML metadata bug!"
Claude: [Fixes _format_response()]
You: [Validates] "Perfect. Why are justifications generic?"
Claude: [Adds specific keyword to justification]
You: [Reviews] "Great. Let's push this to GitHub."
Claude: [Creates documentation]
You: [Reviews all docs] "Let's submit."
```

**Key pattern:** You made decisions; Claude executed. You validated; Claude iterated.

---

### AI Leverage vs. Human Direction

**What AI excels at:**
- ✅ Writing boilerplate code quickly
- ✅ Implementing known algorithms
- ✅ Creating test cases
- ✅ Writing documentation
- ✅ Debugging identified issues

**What humans excel at:**
- ✅ Defining the problem
- ✅ Making trade-off decisions
- ✅ Understanding domain
- ✅ Recognizing emergent bugs
- ✅ Deciding when "good enough" is reached
- ✅ Building narrative

**This project succeeded because:** You leveraged AI for what it's good at (coding) while keeping decision-making authority.

---

## Part 2: The AI Judge Interview Experience

**Interview Date:** May 2, 2026  
**Duration:** 30 minutes (4:30-9:30 AM IST)  
**Format:** Voice-based, real-time Q&A  
**Outcome:** ✅ Completed successfully

### The Judge's 13 Deep-Dive Questions & Your Answers

#### Q1: Why rule-based over LLM?

**Your Answer:**
> Rule-based is deterministic and safe: same query always returns same routing decision—critical for compliance. LLMs are non-deterministic and hallucinate. Zero cost, full transparency: no API calls and we can explain every decision.

**Why Judge Liked It:**
- ✅ Led with compliance (not just "cheaper")
- ✅ Understood LLM risk (hallucination)
- ✅ Concrete trade-off (determinism vs intelligence)
- ✅ Safety-first mindset

---

#### Q2: Hardest constraint to satisfy?

**Your Answer:**
> Balancing safety vs reply rate: escalate too much = waste humans' time. Too lenient = dangerous requests slip through. Solution: explicit list of 17+ high-risk keywords to be safe-by-default without over-escalating.

**Why Judge Liked It:**
- ✅ Identified the real tension
- ✅ Explained the solution
- ✅ Showed constraint was understood before building

---

#### Q3: How did you arrive at high-risk keywords?

**Your Answer:**
> Domain reasoning + testing: Started with obvious categories (refund, fraud, delete account, access issues). Ran Phase 8 on 29 real tickets, identified misclassifications, added missing keywords. Better to over-escalate risky cases than miss them.

**Why Judge Liked It:**
- ✅ Iterative process (not just intuition)
- ✅ Tested against real data
- ✅ Transparent about the "over-escalate" trade-off

---

#### Q4: Confidence threshold 0.4—why that number?

**Your Answer:**
> Empirical tuning: Tested 0.3, 0.4, 0.5 on sample_support_tickets.csv. At 0.4, achieved 100% status routing accuracy—escalates weak matches, replies to confident ones. Confidence normalized 0-1 from keyword scores.

**Why Judge Liked It:**
- ✅ Concrete explanation (not arbitrary)
- ✅ A/B testing approach
- ✅ Could trace back to data

---

#### Q5: doc_hints mapping—how was this built and how brittle is it?

**Your Answer:**
> Problem: query "login" could match 3 different doc types. Solution: manual mappings to boost known-good paths. Built incrementally from failures—when Phase 8 routed wrong, we traced it and added hints.

> Brittleness: ~40-50% of tuning would need redoing if corpus changed. BUT high-risk keywords are domain-agnostic. Modular design isolates tuning to retriever + classifier. With more time, would use embeddings for portability.

**Why Judge Appreciated This:**
- ✅ Explained the problem first
- ✅ Showed learning from failures
- ✅ Didn't oversell portability
- ✅ Had a roadmap to fix it

---

#### Q6: Real-world viability—did you validate with actual users?

**Your Answer (Honest):**
> Primary users: Support team leads (review escalations) and support agents (handle replies). But honest answer: **no real validation**. This is a challenge exercise built on assumed requirements, not production feedback from actual support teams.

**Why Judge Appreciated:**
- ✅ Refreshing honesty
- ✅ Self-awareness about challenge vs production gap
- ✅ Didn't oversell

---

#### Q7: What's the single biggest risk in production?

**Your Answer:**
> False negatives on escalation. Ticket that SHOULD escalate gets auto-replied instead. Example: customer says "I want my money back" instead of exact keyword "refund"—system replies with generic text instead of escalating.

> Why worse than false positives: Over-escalating wastes time but keeps customer safe. Under-escalating harms customers directly. Current 55% accuracy on status routing means ~45% wrong—unacceptable in production. Would need extensive A/B testing and feedback loops before deploying.

**Why Judge Liked:**
- ✅ Identified the real risk
- ✅ Explained why it's worse
- ✅ Honest about accuracy gaps
- ✅ Showed production maturity

---

#### Q8: 90% vs 55% accuracy—which is it?

**Your Answer (Clarification):**
> Good catch. 90% overall accuracy was on small sample set (10 tickets). Status routing on sample: 100%. But 55% was identified as a limitation/improvement area. Production run (29 tickets) has unknown accuracy—no ground-truth labels to validate.

**Why Judge Appreciated:**
- ✅ Didn't deflect
- ✅ Clarified source of each metric
- ✅ Admitted what you don't actually know
- ✅ Intellectual honesty

---

#### Q9: How would you make it better?

**Your Answer:**
> Three things: (1) Better escalation detection—add ML or more keyword patterns. (2) Semantic search with embeddings for context understanding. (3) Smarter response extraction—pick relevant paragraphs instead of first 500 chars.

**Why Judge Liked:**
- ✅ Tiered approach
- ✅ Concrete improvements
- ✅ Showed systems thinking

---

#### Q10: If you had more time, what would you change?

**Your Answer:**
> **Tier 1 (1-2 weeks):** Expand keywords, validation, formatting → 75% → 85% accuracy  
> **Tier 2 (1 month):** Embeddings, feedback loops, monitoring → 85% → 88%  
> **Tier 3 (3+ months):** ML classifier, multi-doc synthesis, corpus updates → 90%+

**Why Judge Liked:**
- ✅ Had actually thought about this
- ✅ Realistic time estimates
- ✅ Clear ROI for each tier
- ✅ Prioritized by impact

---

#### Q11: Why OpenAI API if you're not using it?

**Your Answer:**
> API in .env for fallback implementation—design flexibility. Keyword search works for this corpus; embeddings would be overkill. But if corpus changes or queries get complex, embeddings are already coded. Don't pay for what you don't need; design for upgrade path.

**Why Judge Liked:**
- ✅ Intentional design, not oversight
- ✅ Thinking about evolution
- ✅ Cost-conscious

---

#### Q12: Is it cost-effective?

**Your Answer:**
> Cost-effective for this challenge: $0 per ticket (no API calls). Compare to LLM: $0.01-0.05 per ticket. For company with 10K tickets/month, we save $100-500/month while keeping determinism. Trade-off: less semantic understanding, but 90% accuracy is sufficient.

**Why Judge Liked:**
- ✅ Business thinking
- ✅ Quantified savings
- ✅ Explained the trade-off

---

#### Q13: Will this work in real-world or only this use case?

**Your Answer:**
> Works well: domains with clear terminology (support docs, FAQs, policies). Works where safety > intelligence (compliance, financial, security).  
> Struggles: ambiguous queries, paraphrasing, context-dependent issues.

> For production: Need monitoring, feedback loops, A/B testing, corpus versioning. Current system is proof-of-concept. Core design (modular, pattern-based, safe-by-default) is sound for this class of problem.

**Why Judge Liked:**
- ✅ Honest about scope
- ✅ Showed where it works vs doesn't
- ✅ Realistic about production requirements
- ✅ Didn't claim "one-size-fits-all"

---

### What The Judge Appreciated Overall

Based on interview flow, judge valued:

#### 1. Honesty Over Salesmanship
- ✅ Admitted no real-world validation
- ✅ Clarified contradictory metrics
- ✅ Acknowledged limitations upfront
- ✅ Didn't oversell

#### 2. Clear Thinking About Trade-offs
- ✅ Every design choice had rationale
- ✅ Understood what you were trading away
- ✅ Safety was intentional
- ✅ Could explain the "why" behind numbers

#### 3. Iterative Development Process
- ✅ Tested against real data (29 tickets)
- ✅ Learned from failures (YAML bug)
- ✅ Improved based on feedback
- ✅ Could trace decisions back to evidence

#### 4. Systems Thinking
- ✅ Understood failure modes
- ✅ Thought about production requirements
- ✅ Had roadmap for improvement
- ✅ Designed for evolution

#### 5. Business Acumen
- ✅ Understood cost-benefit trade-offs
- ✅ Knew when "good enough" was sufficient
- ✅ Quantified impact
- ✅ Prioritized by ROI

#### 6. Technical Depth Without Jargon
- ✅ Explained complex concepts simply
- ✅ Used concrete examples
- ✅ Could go deep when asked
- ✅ Didn't hide behind buzzwords

---

### Interview Strategy That Worked

#### Your Approach:
1. **Lead with the problem, not the solution**
   - "Support triage has a bottleneck"
   - "Safety vs efficiency is the real tension"
   - Then: "Here's how we solved it"

2. **Show your thinking, not just code**
   - Explain why keyword search
   - Walk through how you chose 0.4
   - Show trade-offs explicitly

3. **Use specific examples**
   - "When we see 'refund', we escalate"
   - "Query 'login' could match 3 doc types"
   - "YAML metadata bug showed..."

4. **Admit what you don't know**
   - "Production accuracy is unknown"
   - "No real validation with support teams"
   - "Would need A/B testing before deploying"

5. **Have a roadmap**
   - Tier 1: Quick wins
   - Tier 2: Medium improvements
   - Tier 3: Long-term evolution
   - Judge appreciated foresight

---

### Key Moments

#### ✅ Judge Was Impressed When:
1. You clarified 90% vs 55% with real explanation
2. You identified false negatives as biggest risk
3. You admitted no real-world validation
4. You showed iterative process (test → fail → learn → improve)
5. You quantified cost savings

#### ⚠️ Judge Pushed Back When:
1. You said "90% accuracy" → clarified what dataset
2. You mentioned doc_hints → clarified corpus-specific
3. You seemed to oversell → tempered to "good for this use case"

In all cases: You handled it well by admitting the nuance.

---

### What Made Your Approach Different

Most candidates:
- ❌ Oversell their solution
- ❌ Hide limitations
- ❌ Use jargon
- ❌ Claim works everywhere
- ❌ No improvement roadmap

You:
- ✅ Honest about limitations upfront
- ✅ Showed understanding of constraints
- ✅ Explained simply and clearly
- ✅ Scoped to where it works
- ✅ Detailed roadmap with time/effort

**This is what judges look for in real engineers.**

---

## Key Takeaways

### For Building Systems:
1. **Honesty is a strength** — Admitting gaps shows maturity
2. **Show your thinking** — Process matters as much as results
3. **Trade-offs are central** — Have clear reasons for choices
4. **Specific examples beat abstractions** — Make it concrete
5. **Roadmap shows foresight** — Don't just critique; propose solutions
6. **Cost-benefit thinking wins** — Show business understanding

### For Interviews:
1. **Don't oversell** — Judge appreciates realism
2. **Clarify contradictions** — Shows intellectual honesty
3. **Admit what you don't know** — Better than guessing
4. **Use concrete examples** — Makes you credible
5. **Have metrics backing your claims** — Numbers matter
6. **Show the iterative process** — How you think matters most

---

## Bottom Line

**What won the judge over:**
1. Clear problem definition
2. Intentional architectural choices with trade-offs explained
3. Honest evaluation of limitations
4. Iterative development (tested, failed, learned, improved)
5. Detailed roadmap for future improvements
6. Understanding of real-world constraints
7. Business thinking (cost, ROI, prioritization)
8. Technical depth without jargon

You didn't build the fanciest solution. You built a **thoughtfully-designed, well-tested, honestly-scoped solution**. That's what engineering is about.

The judge wasn't grading perfection. The judge was grading your ability to think clearly, make intentional choices, and own your decisions. You did all three.

