"""
API Routers
===========

POST /sessions/start          — create a new session
GET  /sessions/{id}/next      — get the next adaptive question
POST /sessions/{id}/answer    — submit an answer
GET  /sessions/{id}/result    — get final results + AI study plan
GET  /health                  — health check
"""

from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    StartSessionRequest, StartSessionResponse,
    NextQuestionResponse, SubmitAnswerRequest, SubmitAnswerResponse,
    SessionResultResponse, AnswerRecord,
)
from app.services.database import questions_col, sessions_col
from app.services.adaptive import (
    IRTQuestion, select_next_question, update_ability,
    INITIAL_ABILITY, MAX_QUESTIONS,
)
from app.services.ai_insights import generate_study_plan

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# POST /sessions/start
# ─────────────────────────────────────────────────────────────

@router.post("/sessions/start", response_model=StartSessionResponse, tags=["Session"])
async def start_session(body: StartSessionRequest):
    """Create a new adaptive testing session."""
    from app.models.schemas import UserSession
    session = UserSession(student_name=body.student_name or "Anonymous")
    await sessions_col().insert_one(session.model_dump())
    return StartSessionResponse(
        session_id=session.session_id,
        student_name=session.student_name,
        message=f"Session started for {session.student_name}. Good luck!",
    )


# ─────────────────────────────────────────────────────────────
# GET /sessions/{session_id}/next
# ─────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/next", response_model=NextQuestionResponse, tags=["Session"])
async def next_question(session_id: str):
    """Return the next best question for the student's current ability."""
    session = await sessions_col().find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.get("is_complete"):
        raise HTTPException(status_code=400, detail="Session is already complete. Retrieve results via /result.")

    questions_asked: list[str] = session.get("questions_asked", [])
    current_ability: float = session.get("ability", INITIAL_ABILITY)

    # Fetch candidates (excluding already-asked questions)
    cursor = questions_col().find(
        {"question_id": {"$nin": questions_asked}},
        {"_id": 0},
    )
    raw_questions = await cursor.to_list(length=200)

    if not raw_questions:
        raise HTTPException(status_code=404, detail="No more questions available.")

    candidates = [
        IRTQuestion(
            question_id=q["question_id"],
            difficulty=q["difficulty"],
            discrimination=q.get("discrimination", 1.0),
        )
        for q in raw_questions
    ]

    chosen_irt = select_next_question(current_ability, candidates)
    chosen = next(q for q in raw_questions if q["question_id"] == chosen_irt.question_id)

    return NextQuestionResponse(
        session_id=session_id,
        question_number=len(questions_asked) + 1,
        question_id=chosen["question_id"],
        text=chosen["text"],
        options=chosen["options"],
        topic=chosen["topic"],
        current_ability=round(current_ability, 4),
    )


# ─────────────────────────────────────────────────────────────
# POST /sessions/{session_id}/answer
# ─────────────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/answer", response_model=SubmitAnswerResponse, tags=["Session"])
async def submit_answer(session_id: str, body: SubmitAnswerRequest):
    """Submit the student's answer and update their ability estimate."""
    if session_id != body.session_id:
        raise HTTPException(status_code=400, detail="session_id in path must match body.")

    session = await sessions_col().find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.get("is_complete"):
        raise HTTPException(status_code=400, detail="Session is already complete.")

    question = await questions_col().find_one({"question_id": body.question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail=f"Question '{body.question_id}' not found.")

    is_correct = body.answer.upper() == question["correct_answer"].upper()
    ability_before: float = session.get("ability", INITIAL_ABILITY)
    questions_answered = len(session.get("answers", [])) + 1

    new_ability = update_ability(
        theta=ability_before,
        is_correct=is_correct,
        b=question["difficulty"],
        a=question.get("discrimination", 1.0),
        questions_answered=questions_answered,
    )

    record = AnswerRecord(
        question_id=body.question_id,
        topic=question["topic"],
        difficulty=question["difficulty"],
        submitted_answer=body.answer.upper(),
        is_correct=is_correct,
        ability_before=round(ability_before, 4),
        ability_after=round(new_ability, 4),
    ).model_dump()

    questions_asked = session.get("questions_asked", []) + [body.question_id]
    is_complete = questions_answered >= MAX_QUESTIONS

    update_payload = {
        "$set": {"ability": round(new_ability, 4), "is_complete": is_complete},
        "$push": {"answers": record, "questions_asked": body.question_id},
    }
    if is_complete:
        update_payload["$set"]["completed_at"] = datetime.utcnow()

    await sessions_col().update_one({"session_id": session_id}, update_payload)

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question["correct_answer"],
        ability_updated=round(new_ability, 4),
        questions_answered=questions_answered,
        is_complete=is_complete,
        message=(
            "✓ Correct! Moving to a harder question."
            if is_correct
            else f"✗ The correct answer was {question['correct_answer']}. Adjusting difficulty."
        ),
    )


# ─────────────────────────────────────────────────────────────
# GET /sessions/{session_id}/result
# ─────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/result", response_model=SessionResultResponse, tags=["Session"])
async def get_result(session_id: str):
    """Retrieve full session results and generate the AI study plan."""
    session = await sessions_col().find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    answers: list[dict] = session.get("answers", [])
    correct_count = sum(1 for a in answers if a.get("is_correct"))
    total = len(answers)

    # Build topic breakdown
    topic_breakdown: dict[str, dict] = {}
    for a in answers:
        t = a.get("topic", "Unknown")
        if t not in topic_breakdown:
            topic_breakdown[t] = {"correct": 0, "total": 0}
        topic_breakdown[t]["total"] += 1
        if a.get("is_correct"):
            topic_breakdown[t]["correct"] += 1

    # Generate or reuse study plan
    study_plan = session.get("study_plan")
    if not study_plan and session.get("is_complete") and total > 0:
        study_plan = generate_study_plan(
            student_name=session.get("student_name", "Student"),
            final_ability=session.get("ability", INITIAL_ABILITY),
            total_questions=total,
            correct_count=correct_count,
            topic_breakdown=topic_breakdown,
        )
        await sessions_col().update_one(
            {"session_id": session_id},
            {"$set": {"study_plan": study_plan}},
        )

    return SessionResultResponse(
        session_id=session_id,
        student_name=session.get("student_name", "Anonymous"),
        final_ability=round(session.get("ability", INITIAL_ABILITY), 4),
        total_questions=total,
        correct_count=correct_count,
        accuracy=round(correct_count / total, 4) if total else 0.0,
        topic_breakdown=topic_breakdown,
        study_plan=study_plan,
        answers=[AnswerRecord(**a) for a in answers],
    )


# ─────────────────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
async def health_check():
    from app.services.database import get_client
    try:
        await get_client().admin.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "database": db_status}
