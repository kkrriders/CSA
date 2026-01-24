# Analytics System Refactor - From Vibes to Mathematics

## Critical Issues Fixed

### 1. ✅ Separated Signals from Interpretations

**BEFORE (Amateur Logic):**
```python
if answer.time_taken < 30:
    answer.confidence_signal = "guessed"  # WRONG: Mixed signal with interpretation
```

**AFTER (Professional):**
```python
# STEP 1: Capture RAW signals
signal = BehavioralSignals(
    time_spent=answer.time_taken,  # FACT
    answered=True,                 # FACT
    correct=False,                 # FACT
    marked_tricky=True            # FACT
)

# STEP 2: Compute probabilistic states
scores = compute_cognitive_scores(signal)
# guessing_score ∈ [0,1]
# confusion_score ∈ [0,1]
# avoidance_score ∈ [0,1]
```

**Models Created:**
- `BehavioralSignals` - Pure facts, no psychology
- `CognitiveScores` - Inferred states, probabilistic

---

### 2. ✅ Empirical Difficulty (Not LLM Guesses)

**BEFORE:**
```python
difficulty = "easy"  # From LLM - meaningless
```

**AFTER:**
```python
difficulty = % of users who got this right

# Bootstrap at 0.5, update with real data
empirical_difficulty = correct_attempts / total_attempts

# EXACTLY like SAT, GMAT, Duolingo
```

**Implementation:**
- `QuestionStatistics` model tracks real success rates
- `QuestionStatsService` updates after each attempt
- Auto-updates in `submit_answer` endpoint

---

### 3. ✅ Mathematical Weakness Mapping

**BEFORE:**
```python
weakness_score = vibes  # Just sorted by "wrong"
```

**AFTER:**
```python
# Mathematical formula:
topic_mastery = weighted_avg(correctness × difficulty × recency)

weakness_score = 1 - topic_mastery

priority = weakness × exposure × confidence_penalty

# Where:
# - difficulty weight: harder questions count more
# - recency: exponential decay (recent = more weight)
# - confidence_penalty: based on hesitation, marking tricky
```

**Implementation:**
- `_calculate_weighted_mastery()` - Real math
- `_calculate_confidence_penalty()` - Behavioral signals
- Sorted by mathematical priority (not vibes)

---

### 4. ✅ Grounded AI Explanations (Anti-Hallucination)

**BEFORE:**
```python
# Could hallucinate:
"You misunderstood transformers"  # When user just rage-clicked
```

**AFTER:**
```python
AIExplanation:
  source_paragraph: "EXACT quote from document"
  section_reference: "Section 2.3"
  behavioral_insight: "You spent 15s and skipped - suggests avoidance"

# LLM is given:
# - Question
# - User answer
# - Correct answer
# - Source context
# - Behavioral signals (time, hesitation, skipped)
```

**Critical Rules for LLM:**
1. Base explanation ONLY on provided context
2. Cite specific paragraphs
3. Consider behavioral signals
4. DO NOT hallucinate
5. If context insufficient, acknowledge it

---

### 5. ✅ Behavioral Profiling

**NEW FEATURE:**

```python
class BehavioralType(Enum):
    RUSHER = "rusher"           # Fast answers, many wrong
    HESITATOR = "hesitator"     # Slow, changes answers
    AVOIDER = "avoider"         # High skip rate
    GRINDER = "grinder"         # Slow but accurate
    RANDOM_CLICKER = "random"   # Fast, inconsistent

# Inferred from all user signals
behavioral_type = infer_behavioral_type(all_signals)
```

**Classification Logic:**
- Skip rate > 30% → Avoider
- Fast rate > 70% + low accuracy → Random Clicker
- Fast rate > 70% + high accuracy → Rusher
- Slow + high hesitation → Hesitator
- Slow + low hesitation → Grinder (default)

---

## File Structure

### New Files Created:
```
backend/app/services/
  ├── analytics_service_v2.py      # Mathematical, signal-based
  └── question_stats_service.py    # Empirical difficulty tracking

backend/app/models/
  └── analytics.py                 # Updated with new models
```

### Updated Files:
```
backend/app/routes/
  ├── analytics.py    # Uses V2 service, grounded explanations
  └── tests.py        # Tracks question statistics

backend/app/services/
  └── llm_service.py  # Behavioral context, anti-hallucination

frontend/src/
  ├── types/index.ts  # Updated AIExplanation interface
  └── app/test/results/[sessionId]/page.tsx  # Shows grounding
```

---

## Migration Guide

### Backend Changes Required:

1. **Database Index (Optional but Recommended):**
```bash
# MongoDB shell
db.question_statistics.createIndex({ "question_id": 1 }, { unique: true })
```

2. **Update Analytics Routes:**
```python
# OLD:
from app.services.analytics_service import AnalyticsService

# NEW: Use V2 for new endpoints
from app.services.analytics_service_v2 import AnalyticsServiceV2
```

3. **Gradual Migration:**
- Old endpoints still work (analytics_service.py)
- New endpoints use V2 (analytics_service_v2.py)
- Migrate endpoint by endpoint

---

## TODO: Frontend Tracking

**Critical Missing Signals:**

The frontend needs to track:

```typescript
// In QuestionCard component:
interface AnswerTracking {
  changed_answer: boolean;        // Did user change their selection?
  hesitation_count: number;       // How many times changed?
  time_to_first_answer: number;   // Time until first selection
}
```

**Implementation:**
```typescript
// frontend/src/components/QuestionCard.tsx
const [answerHistory, setAnswerHistory] = useState<string[]>([]);

const handleAnswerChange = (newAnswer: string) => {
  setAnswerHistory(prev => [...prev, newAnswer]);
  onAnswerChange(newAnswer);
};

// On submit:
const tracking = {
  changed_answer: answerHistory.length > 1,
  hesitation_count: answerHistory.length - 1,
  time_to_first_answer: firstAnswerTime - questionStartTime
};
```

---

## Testing the Changes

### 1. Test Empirical Difficulty:
```bash
# Answer same question multiple times (different sessions)
# Check: GET /api/question_statistics/:question_id
# Verify: empirical_difficulty updates correctly
```

### 2. Test Grounded Explanations:
```bash
# Click "Ask AI Why" on any wrong answer
# Check response includes:
# - source_paragraph (quote from document)
# - section_reference
# - behavioral_insight
```

### 3. Test Mathematical Weakness:
```bash
# Complete a test with varied performance
# Check: GET /api/analytics/session/:id/weakness-map
# Verify: priority_score is mathematical (not random)
```

---

## Key Formulas Reference

### 1. Weighted Mastery:
```
mastery = Σ(correctness_i × difficulty_weight_i × recency_weight_i) / Σ(weights)

Where:
  correctness_i = 1 if correct, 0 if wrong
  difficulty_weight_i = 1 - empirical_difficulty
  recency_weight_i = e^(-0.14 × age_in_attempts)
```

### 2. Weakness Priority:
```
priority = (1 - mastery) × exposure × confidence_penalty

Where:
  weakness = 1 - mastery
  exposure = number of questions attempted in topic
  confidence_penalty = 1 + (avg_confusion × 0.5) + (tricky_rate × 0.3)
```

### 3. Cognitive Score Thresholds:
```
FAST_THRESHOLD = 20 seconds
SLOW_THRESHOLD = 60 seconds
EASY_DIFFICULTY = 0.7 (70%+ success)
HARD_DIFFICULTY = 0.3 (<30% success)

guessing_score = high if (fast + hard question + wrong)
confusion_score = high if (slow + hesitation + wrong)
avoidance_score = high if (skipped + easy question)
knowledge_gap_score = high if (wrong + easy question)
```

---

## Benefits

1. **Defensible AI** - Mathematical formulas, not vibes
2. **No Hallucination** - Citations to source material
3. **Empirical Difficulty** - Real data replaces LLM guesses
4. **Behavioral Insights** - Understand *how* users think
5. **Adaptive Precision** - Targets real weaknesses mathematically

---

## Old vs New Comparison

| Feature | OLD (Vibes) | NEW (Mathematical) |
|---------|-------------|-------------------|
| Difficulty | LLM guess | % who got it right |
| Weakness | "wrong" count | weighted_avg(correctness × difficulty × recency) |
| Priority | Random sort | weakness × exposure × confidence_penalty |
| Explanations | Can hallucinate | Grounded in source |
| Signals | Mixed with interpretation | Separated |
| User profiling | None | Behavioral types |

---

## Questions?

This is a MAJOR refactor but maintains backward compatibility.

- Old endpoints still work (gradual migration)
- New V2 service implements proper math
- Frontend updated to show grounding
- Database automatically bootstraps empirical difficulty

**Next Steps:**
1. Test the changes
2. Implement frontend answer tracking (TODO section)
3. Gradually migrate all endpoints to V2
4. Monitor empirical difficulty convergence
