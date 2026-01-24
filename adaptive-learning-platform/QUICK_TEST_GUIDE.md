# Quick Test Guide - World-Class Analytics

## Immediate Testing (5 minutes)

### Setup
```bash
# 1. Restart backend
cd adaptive-learning-platform/backend
uvicorn app.main:app --reload --port 8000

# 2. Get your auth token (from browser localStorage or login)
TOKEN="your_jwt_token_here"
```

---

## Test 1: Behavior Fingerprint (Works After 1 Test)

### Action:
Complete any test session

### API Call:
```bash
curl -X GET "http://localhost:8000/api/analytics/user/behavior-fingerprint-aggregate" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### What You'll See:
```json
{
  "user_id": "...",
  "risk_taking": 0.65,
  "perfectionism": 0.42,
  "skimming": 0.18,
  "grinding": 0.73,
  "primary_trait": "Grinder",
  "secondary_trait": "Risk-taker",
  "strengths": [
    "Thorough understanding of concepts",
    "High accuracy through persistence"
  ],
  "optimal_study_strategy": "Your persistence is your strength. Focus on efficiency to maximize coverage."
}
```

### Resume Line:
> "You are a **Grinder** learner - slow but thorough, high accuracy"

---

## Test 2: Exam Readiness (Works After 1+ Tests)

### Action:
Complete at least one test

### API Call:
```bash
# Replace {document_id} with your actual document ID
curl -X GET "http://localhost:8000/api/analytics/document/{document_id}/exam-readiness" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### What You'll See:
```json
{
  "overall_score": 67.5,
  "mastery_score": 65.0,
  "consistency_score": 75.0,
  "confidence_score": 70.0,
  "coverage_score": 60.0,
  "readiness_level": "Needs Work",
  "estimated_study_hours": 11,
  "priority_actions": [
    "Focus on weak topics: Probability Theory, Statistics",
    "Cover more topics to improve breadth"
  ],
  "strong_topics": ["Linear Algebra"],
  "weak_topics": ["Probability Theory", "Statistics"]
}
```

### Impact:
> "You are **67.5% ready**. Estimated **11 hours** of study to reach 90%."

---

## Test 3: Learning Velocity (Requires 2+ Tests on Same Topics)

### Action:
Complete 2+ test sessions with overlapping topics

### API Call:
```bash
curl -X GET "http://localhost:8000/api/analytics/user/learning-velocity" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### What You'll See:
```json
{
  "velocities": [
    {
      "topic": "Neural Networks",
      "sessions_analyzed": 3,
      "mastery_trajectory": [0.4, 0.6, 0.75],
      "velocity": 0.175,
      "sessions_to_mastery": 1,
      "comparative_rank": "Fastest learning topic"
    },
    {
      "topic": "Backpropagation",
      "sessions_analyzed": 2,
      "mastery_trajectory": [0.3, 0.45],
      "velocity": 0.15,
      "comparative_rank": "1.2× slower than Neural Networks"
    }
  ]
}
```

### Resume Line:
> "You learn **Neural Networks 1.2× faster** than Backpropagation"

---

## Test 4: Forgetting Curve (Requires Tests Spaced Over Time)

### Action:
1. Complete a test, get good score on a topic
2. Wait 1+ week
3. Complete another test with same topic

### API Call:
```bash
# Replace {topic} with actual topic name (URL-encode spaces)
curl -X GET "http://localhost:8000/api/analytics/user/topic/Neural%20Networks/forgetting-curve" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### What You'll See:
```json
{
  "topic": "Neural Networks",
  "peak_mastery": 0.85,
  "peak_date": "2026-01-10T10:00:00Z",
  "current_mastery": 0.68,
  "days_since_peak": 14,
  "decay_rate": 0.016,
  "half_life_days": 43.3,
  "needs_review": true
}
```

### Insight:
> "Your Neural Networks knowledge has a **43-day half-life** and **needs review**"

---

## Test 5: Grounded Explanations (Works Immediately)

### Action:
1. Complete a test
2. Get wrong answer on at least one question
3. Click "Ask AI Why" (or call API)

### API Call:
```bash
curl -X POST "http://localhost:8000/api/analytics/explain-wrong-answer" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "question_id": "your_question_id"
  }' | jq
```

### What You'll See:
```json
{
  "question_id": "...",
  "user_answer": "sigmoid",
  "correct_answer": "ReLU",
  "source_paragraph": "ReLU (Rectified Linear Unit) is preferred for hidden layers because it mitigates the vanishing gradient problem...",
  "section_reference": "Section 3.2: Activation Functions",
  "why_wrong": "Sigmoid suffers from vanishing gradients in deep networks",
  "concept_explanation": "ReLU allows gradients to flow better during backpropagation",
  "behavioral_insight": "You answered in 12s, suggesting possible guessing on this concept"
}
```

### Key Feature:
**NO HALLUCINATION** - Every explanation cites the exact source paragraph!

---

## Browser Testing (Frontend)

### 1. Complete a Test
```
http://localhost:3000/test/configure
```

### 2. View Results
```
http://localhost:3000/test/results/{session_id}
```

### 3. Check "Ask AI Why"
- Click on any wrong answer
- See: Source citation + Behavioral insight
- Verify: Exact quote from your document

---

## What Makes Each Feature Impressive

| Feature | Impressive Because | Resume Line |
|---------|-------------------|-------------|
| **Behavior Fingerprint** | 4 traits × 8 metrics | "Deep behavioral profiling system" |
| **Exam Readiness** | 4-component weighted formula | "Holistic readiness with study hour estimates" |
| **Learning Velocity** | Comparative metrics | "You learn X 3× faster than Y" |
| **Forgetting Curve** | Ebbinghaus formula + half-life | "Implements spaced repetition science" |
| **Grounded Explanations** | Anti-hallucination | "Citation-based, zero hallucination" |

---

## Expected Timeline

| Sessions | Features Available |
|----------|-------------------|
| **1 session** | Behavior Fingerprint, Exam Readiness, Grounded Explanations |
| **2 sessions** | Learning Velocity (basic) |
| **3+ sessions** | Learning Velocity (comparative) |
| **Week+ gap** | Forgetting Curve |

---

## Demo Script (For Interviews)

> "Let me show you our analytics system. After just one test, the platform identifies your learning personality - in my case, I'm a 'Grinder' with 73% grinding score and 65% risk-taking as a secondary trait. The system recommends I focus on efficiency to maximize coverage.
>
> For exam readiness, the platform calculates a holistic score - I'm currently 72% ready, with an estimated 9 hours of study needed. It breaks this down into specific actions: focus on Probability Theory and Statistics, my weak topics.
>
> As I complete more sessions, it tracks my learning velocity - I'm learning CNNs 3× faster than Transformers, which helps me prioritize where to spend time.
>
> And critically, all AI explanations are grounded in source material - no hallucination. Each explanation cites the exact paragraph from my study document and includes behavioral context like 'You answered in 12s, suggesting guessing'."

---

## Troubleshooting

### "No data available"
- Complete at least 1 test session first
- Make sure test is marked as "completed"

### "Token expired"
- Re-login to get fresh JWT token
- Check localStorage for 'token' key

### "Topic not found"
- URL-encode topic names with spaces
- Use exact topic name from questions

### "Velocity shows 0"
- Need 2+ sessions with same topics
- Check mastery_trajectory has 2+ values

---

## Next: Build a Dashboard

Once you've tested the APIs, create a dashboard component:

```typescript
// frontend/src/app/analytics/page.tsx
import { BehaviorFingerprint, ExamReadinessScore } from '@/types';

export default function AnalyticsDashboard() {
  // Fetch from APIs
  // Display in beautiful charts
  // Show insights and recommendations
}
```

See `WORLD_CLASS_FEATURES.md` for component examples!

---

**You're Ready!** Test these features now and prepare your resume talking points.
