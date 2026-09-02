# 🧠 AI-Driven Adaptive Diagnostic Engine

An adaptive testing platform that estimates a student's ability level while dynamically selecting questions based on previous answers.

The backend is built with **FastAPI**, sessions and questions are stored in **MongoDB**, and **Groq** generates a personalized study plan after the assessment.

## ✨ Features

- 🎯 Adaptive question selection based on estimated ability
- 📈 IRT-inspired ability updates
- 📚 Topic-level performance tracking
- 🤖 Groq-powered personalized 3-step study plan
- 🗄️ MongoDB persistence for questions and sessions
- ⚡ FastAPI REST API with Swagger/ReDoc documentation
- 🌐 Included browser frontend
- ❤️ `/health` endpoint for service monitoring

## 🏗️ Architecture

```text
Browser Frontend
       ↓
FastAPI REST API
       ↓
Adaptive Testing Service ───→ MongoDB
       ↓
Assessment Result
       ↓
Groq LLM
       ↓
Personalized Study Plan
```

## 🧮 Adaptive Algorithm

1. The student starts with a baseline ability score of `0.5`.
2. Every question has a difficulty value between `0.1` and `1.0`.
3. A correct answer increases the estimated ability.
4. An incorrect answer decreases the estimated ability.
5. The next question is selected near the updated ability level.

This is a simplified **Item Response Theory (IRT)-inspired** approach rather than a full IRT implementation.

## 🤖 AI Study Plan

At the end of an assessment, the backend sends the student's performance summary to Groq. The generated plan considers:

- Estimated ability level
- Overall accuracy
- Weak topics
- Topic-level performance

The result is returned as a concise 3-step study plan. If the AI service is unavailable, the API returns a graceful fallback summary instead of crashing the session result.

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/sessions/start` | Create an adaptive test session |
| `GET` | `/api/v1/sessions/{session_id}/next` | Get the next adaptive question |
| `POST` | `/api/v1/sessions/{session_id}/answer` | Submit an answer and update ability |
| `GET` | `/api/v1/sessions/{session_id}/result` | Get final result and study plan |

Interactive API documentation is available at `/docs` after the server starts.

## ▶️ Run Locally

```bash
git clone https://github.com/SIDMINUL/Adaptive_Diagnostic_Recognition.git
cd Adaptive_Diagnostic_Recognition
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=mongodb://localhost:27017
DB_NAME=adaptive_engine
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## 📁 Project Structure

```text
Adaptive_Diagnostic_Recognition/
├── app/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   │   ├── adaptive.py
│   │   ├── ai_insights.py
│   │   └── database.py
│   └── seed.py
├── frontend/
│   └── index.html
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚠️ Requirements

The application requires a reachable MongoDB instance for questions and session persistence. Groq-powered study plans require a valid `GROQ_API_KEY`.

For production use, restrict CORS origins instead of allowing all origins and add authentication/rate limiting as appropriate.

## 📌 AI Development Notes

AI tools were used during development for architecture planning, debugging, API integration, and prompt engineering. External API behavior and environment configuration still require independent testing and verification.
