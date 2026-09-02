"""Generate a personalized study plan with the Groq API."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is not set in environment.")
        _client = Groq(api_key=api_key)
    return _client


def ability_label(score: float) -> str:
    if score < 0.4:
        return "Beginner"
    if score < 0.7:
        return "Intermediate"
    return "Advanced"


def _build_prompt(
    student_name: str,
    final_ability: float,
    total_questions: int,
    correct_count: int,
    topic_breakdown: dict,
) -> str:
    accuracy = correct_count / total_questions if total_questions else 0
    level = ability_label(final_ability)

    weak_topics = [
        topic
        for topic, stats in topic_breakdown.items()
        if stats["total"] > 0
        and stats["correct"] / stats["total"] < 0.60
    ]

    topic_detail = "\n".join(
        f"- {topic}: {stats['correct']}/{stats['total']} correct"
        for topic, stats in topic_breakdown.items()
    )

    return f"""You are an expert GRE tutor analyzing a student's adaptive test performance.

Student: {student_name}
Estimated level: {level}
Accuracy: {accuracy:.0%}

Topic Breakdown:
{topic_detail}

Weak Topics: {", ".join(weak_topics) if weak_topics else "None"}

Create a concise, practical 3-step personalized study plan.
Focus on the student's weakest topics and include concrete practice actions.
"""


def generate_study_plan(
    student_name: str,
    final_ability: float,
    total_questions: int,
    correct_count: int,
    topic_breakdown: dict,
) -> str:
    prompt = _build_prompt(
        student_name,
        final_ability,
        total_questions,
        correct_count,
        topic_breakdown,
    )

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert GRE tutor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=700,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        level = ability_label(final_ability)
        return (
            f"⚠️ AI study plan generation failed ({exc}). "
            f"You performed at the {level} level with "
            f"{correct_count}/{total_questions} correct."
        )
