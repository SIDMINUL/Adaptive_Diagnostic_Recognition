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
