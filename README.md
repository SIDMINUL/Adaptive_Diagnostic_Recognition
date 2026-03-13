# AI-Driven Adaptive Diagnostic Engine

## Overview

This project implements a 1-D Adaptive Testing System that estimates a student's proficiency level by dynamically adjusting question difficulty based on previous responses.

The system uses:

* FastAPI (backend API)
* MongoDB (question database)
* Groq LLM (AI-generated study plan)
* Item Response Theory (IRT) inspired ability updates.

---

## Features

* Adaptive question selection
* Ability score estimation
* Topic performance tracking
* AI-generated personalized study plan

---

## How to Run

### 1 Install dependencies

pip install -r requirements.txt

### 2 Start MongoDB

mongod

### 3 Set environment variables

Create `.env`

GROQ_API_KEY=your_key_here

### 4 Run server

uvicorn app.main:app --reload

### 5 Open API docs

http://127.0.0.1:8000/docs

---

## Adaptive Algorithm Logic

1. Student starts with baseline ability = 0.5
2. Each question has difficulty (0.1–1.0)
3. If answer is correct → ability increases
4. If incorrect → ability decreases
5. Next question is selected closest to updated ability.

This mimics a simplified Item Response Theory (IRT) approach.

---

## AI Study Plan

After the test ends:

* Performance data is sent to Groq LLM
* The model analyzes:

  * weak topics
  * accuracy
  * ability level
* Generates a personalized 3-step study plan.

---

## API Endpoints

POST /api/v1/sessions/start
GET /api/v1/sessions/{session_id}/next
POST /api/v1/sessions/{session_id}/answer
GET /api/v1/sessions/{session_id}/result

---

## AI Log

AI tools used during development:

* ChatGPT for architecture planning
* ChatGPT for debugging API integration
* ChatGPT for converting Anthropic API to Groq API
* AI-assisted prompt engineering for study plan generation

Challenges AI could not solve directly:

* Groq API model deprecation
* environment variable loading issues
* adapting FastAPI service structure

These were resolved manually through debugging and documentation review.


## API Documentation

Base URL:
http://127.0.0.1:8000

Interactive docs (FastAPI Swagger):
http://127.0.0.1:8000/docs

### 1. Start Test Session

POST /api/v1/sessions/start

Description:
Creates a new adaptive testing session.

Response Example:
{
"session_id": "886c4e09-c2cb-4755-b519-c18e42e16b78"
}

### 2. Get Next Question

GET /api/v1/sessions/{session_id}/next

Description:
Returns the next question selected by the adaptive algorithm based on the user's current ability estimate.

Response Example:
{
"question_id": "q12",
"question": "Solve: 2x + 5 = 11",
"options": ["2", "3", "4", "5"],
"difficulty": 0.55,
"topic": "Algebra"
}

### 3. Submit Answer

POST /api/v1/sessions/{session_id}/answer

Description:
Submits a student's answer and updates the ability score.

Request Example:
{
"question_id": "q12",
"selected_answer": "3"
}

Response Example:
{
"correct": true,
"updated_ability": 0.62
}

### 4. Get Final Result and Study Plan

GET /api/v1/sessions/{session_id}/result

Description:
Returns final ability score, topic performance, and AI-generated study plan.

Response Example:
{
"final_ability": 0.58,
"accuracy": 0.6,
"weak_topics": ["Algebra"],
"study_plan": "Step 1: Review algebra basics..."
}
