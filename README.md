# AdaptIQ — AI-Driven Adaptive Diagnostic Engine

> A production-grade 1-Dimension Adaptive Testing prototype using **Item Response Theory (IRT)** and **Claude AI** to dynamically assess student ability and generate personalised study plans.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Quick Start](#quick-start)
4. [Adaptive Algorithm Logic](#adaptive-algorithm-logic)
5. [API Documentation](#api-documentation)
6. [Project Structure](#project-structure)
7. [AI Log](#ai-log)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/JS)                    │
│          Dynamic quiz UI · Ability meter · Study plan        │
└───────────────────────────┬─────────────────────────────────┘
                            │  REST (JSON)
┌───────────────────────────▼─────────────────────────────────┐
│                FastAPI Application (Python)                  │
│                                                              │
│   /api/v1/sessions/start    → Create UserSession            │
│   /api/v1/sessions/{id}/next → IRT question selection       │
│   /api/v1/sessions/{id}/answer → IRT ability update         │
│   /api/v1/sessions/{id}/result → Results + AI study plan    │
│                                                              │
│  ┌──────────────┐   ┌────────────────┐   ┌───────────────┐ │
│  │  adaptive.py │   │  ai_insights   │   │  database.py  │ │
│  │  (IRT 1PL)   │   │  (Claude API)  │   │  (Motor/Mongo)│ │
│  └──────────────┘   └────────────────┘   └───────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │          MongoDB              │
            │  collections: questions,      │
            │               sessions        │
            └───────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 · FastAPI · Uvicorn |
| Database | MongoDB (Motor async driver) |
| AI Integration | Anthropic Claude (`claude-sonnet-4-20250514`) |
| Frontend | Vanilla HTML/CSS/JS (single file, served by FastAPI) |
| Testing | Pytest |

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- MongoDB running locally **or** a MongoDB Atlas connection string
- An Anthropic API key (for study plan generation)

### 2. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/adaptive-diagnostic-engine.git
cd adaptive-diagnostic-engine
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in MONGO_URI and ANTHROPIC_API_KEY
```

### 4. Seed the database

```bash
python -m app.seed
# Output: [Seed] Done — 25 inserted, 0 already existed.
```

### 5. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Open the app
- **Frontend UI:** http://localhost:8000
- **Swagger API docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 7. Run tests

```bash
pytest tests/ -v
```

---

## Adaptive Algorithm Logic

### Overview — 1-Parameter Logistic IRT (Rasch Model)

The engine uses the **1PL Item Response Theory** model to estimate a student's **latent ability (θ)** and dynamically select the most informative question at each step.

### Key Parameters

| Symbol | Meaning | Range |
|--------|---------|-------|
| θ (theta) | Student ability estimate | 0.05 – 0.95 |
| b | Item difficulty parameter | 0.1 – 1.0 |
| a | Item discrimination (2PL extension) | 0.8 – 1.5 |

### Probability Model

The probability that a student with ability θ answers a question of difficulty b correctly:

```
P(correct | θ, b) = 1 / (1 + exp(-D × a × (θ_c − b_c)))
```

Where:
- `D = 1.702` — IRT scaling constant
- θ and b are linearly mapped from [0,1] → [−2, +2] to give the logistic meaningful range

### Ability Update (MLE Gradient Step)

After each response, θ is updated using a **decaying gradient ascent** rule:

```
error         = response (0 or 1) − P(correct | θ, b)
learning_rate = 0.15 × 0.5^(floor((n−1)/5))   # halves every 5 items
θ_new         = clamp(θ + learning_rate × error, 0.05, 0.95)
```

This mirrors the Newton–Raphson update in full MLE-CAT but is computationally lightweight and converges reliably in ≤10 items.

### Question Selection (Maximum Information)

The next question is chosen from the unanswered pool to **maximise Fisher Information** at the current θ:

```python
I(θ, b, a) = (D × a)² × P × (1 − P)
```

In practice, this is approximated by selecting the question with **difficulty closest to current θ**, with ties broken by highest discrimination — a well-established approximation used in operational CAT systems (e.g., LSAT, GRE CAT).

### Session Flow

```
θ₀ = 0.5  (baseline)
for each question (up to 10):
    q* = argmin |difficulty − θ| over unanswered questions
    present q* to student
    receive response r ∈ {0, 1}
    θ ← update_ability(θ, r, b_q*)
end
generate_study_plan(θ_final, topic_breakdown)
```

---

## API Documentation

Base URL: `http://localhost:8000/api/v1`

### `POST /sessions/start`
Create a new adaptive testing session.

**Request body:**
```json
{ "student_name": "Alex" }
```
**Response:**
```json
{
  "session_id": "uuid4",
  "student_name": "Alex",
  "message": "Session started for Alex. Good luck!"
}
```

---

### `GET /sessions/{session_id}/next`
Retrieve the next question selected by the IRT engine for the student's current ability.

**Response:**
```json
{
  "session_id": "...",
  "question_number": 3,
  "question_id": "q_voc_02",
  "text": "Choose the word most nearly OPPOSITE to LOQUACIOUS.",
  "options": [{"key": "A", "text": "Garrulous"}, ...],
  "topic": "Vocabulary",
  "current_ability": 0.56
}
```

---

### `POST /sessions/{session_id}/answer`
Submit the student's answer to the current question.

**Request body:**
```json
{
  "session_id": "uuid4",
  "question_id": "q_voc_02",
  "answer": "C"
}
```
**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "C",
  "ability_updated": 0.62,
  "questions_answered": 3,
  "is_complete": false,
  "message": "✓ Correct! Moving to a harder question."
}
```

---

### `GET /sessions/{session_id}/result`
Retrieve complete session results including the AI-generated study plan.

**Response:**
```json
{
  "session_id": "...",
  "student_name": "Alex",
  "final_ability": 0.68,
  "total_questions": 10,
  "correct_count": 7,
  "accuracy": 0.70,
  "topic_breakdown": {
    "Vocabulary": {"correct": 2, "total": 3},
    "Algebra":    {"correct": 2, "total": 2}
  },
  "study_plan": "**Step 1: ...**\n...",
  "answers": [...]
}
```

---

### `GET /health`
Health check — verifies server is running and MongoDB is reachable.

```json
{ "status": "ok", "database": "connected" }
```

---

## Project Structure

```
adaptive-diagnostic-engine/
├── app/
│   ├── main.py                 # FastAPI app, lifecycle hooks, CORS
│   ├── seed.py                 # Seeds 25 GRE questions into MongoDB
│   ├── models/
│   │   └── schemas.py          # Pydantic models (Question, UserSession, requests)
│   ├── services/
│   │   ├── adaptive.py         # IRT algorithm: probability, update, selection
│   │   ├── ai_insights.py      # Anthropic Claude integration
│   │   └── database.py         # Motor async MongoDB client + indexes
│   └── routers/
│       └── api.py              # All API route handlers
├── frontend/
│   └── index.html              # Single-file adaptive quiz UI
├── tests/
│   └── test_adaptive.py        # Pytest unit tests (IRT algorithm)
├── .env.example
├── requirements.txt
└── README.md
```

---

## AI Log

### How AI tools were used

**Anthropic Claude (this project!) — Production AI integration**
Claude `claude-sonnet-4-20250514` is used at the end of each session to generate personalised study plans. The prompt includes the student's performance breakdown by topic, their final ability score, and their identified weak areas. Claude outputs a structured 3-step plan with concrete, actionable advice. The fallback is graceful — if the API is unavailable, a meaningful plain-text summary is returned instead.

**Development workflow**
Claude was used to:
- Draft the initial IRT probability and update functions, which were then verified mathematically against published IRT literature (Lord, 1980)
- Generate the 25 GRE-style questions ensuring correct difficulty calibration across topics
- Write boilerplate FastAPI route structure that was then refined with proper error handling and validation
- Suggest the decaying-learning-rate approach for the ability update step, which produces more stable convergence than a fixed step size

**Where AI fell short**
- AI-generated question difficulties initially clustered around 0.4–0.6, requiring manual redistribution to cover the full 0.1–0.9 range
- The initial IRT implementation used a naïve θ ∈ [0,1] directly in the logistic, which produced near-flat probability curves; the [0,1] → [−2, +2] centring fix was identified through manual testing
- Async MongoDB query patterns with Motor required hand-tuning since AI suggestions occasionally used synchronous PyMongo patterns

### Challenges
- **IRT convergence in 10 items:** With only 10 questions, MLE can be unstable at the extremes. The decaying step size and clamping to [0.05, 0.95] resolve this.
- **Cold start:** The fixed θ₀ = 0.5 is a reasonable prior but could be improved with a brief prior elicitation question.
