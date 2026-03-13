"""
Pydantic schemas for request/response validation and MongoDB document shapes.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ---------------------------------------------------------------------------
# Question document
# ---------------------------------------------------------------------------

class QuestionOption(BaseModel):
    key: str          # "A", "B", "C", "D"
    text: str


class Question(BaseModel):
    """Stored in the `questions` collection."""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    options: list[QuestionOption]
    correct_answer: str          # key of the correct option, e.g. "B"
    difficulty: float            # IRT b-parameter, 0.1 – 1.0
    discrimination: float = 1.0  # IRT a-parameter (default = 1.0 for 1PL)
    topic: str                   # "Algebra", "Vocabulary", etc.
    tags: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "What is the value of x in 2x + 3 = 7?",
                "options": [
                    {"key": "A", "text": "1"},
                    {"key": "B", "text": "2"},
                    {"key": "C", "text": "3"},
                    {"key": "D", "text": "4"},
                ],
                "correct_answer": "B",
                "difficulty": 0.3,
                "discrimination": 1.2,
                "topic": "Algebra",
                "tags": ["linear_equations", "gre_quant"],
            }
        }


# ---------------------------------------------------------------------------
# UserSession document
# ---------------------------------------------------------------------------

class AnswerRecord(BaseModel):
    question_id: str
    topic: str
    difficulty: float
    submitted_answer: str
    is_correct: bool
    ability_before: float        # θ before this answer
    ability_after: float         # θ after Bayesian update
    answered_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(BaseModel):
    """Stored in the `sessions` collection."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_name: Optional[str] = "Anonymous"
    ability: float = 0.5         # θ – current estimated ability (0.0 – 1.0)
    questions_asked: list[str] = []          # question_ids already used
    answers: list[AnswerRecord] = []
    is_complete: bool = False
    study_plan: Optional[str] = None        # LLM-generated plan
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# API request / response shapes
# ---------------------------------------------------------------------------

class StartSessionRequest(BaseModel):
    student_name: Optional[str] = "Anonymous"


class StartSessionResponse(BaseModel):
    session_id: str
    student_name: str
    message: str


class NextQuestionResponse(BaseModel):
    session_id: str
    question_number: int          # 1-indexed
    question_id: str
    text: str
    options: list[QuestionOption]
    topic: str
    current_ability: float


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str                   # key: "A" / "B" / "C" / "D"


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    ability_updated: float
    questions_answered: int
    is_complete: bool
    message: str


class SessionResultResponse(BaseModel):
    session_id: str
    student_name: str
    final_ability: float
    total_questions: int
    correct_count: int
    accuracy: float
    topic_breakdown: dict[str, dict]   # topic → {correct, total}
    study_plan: Optional[str]
    answers: list[AnswerRecord]
