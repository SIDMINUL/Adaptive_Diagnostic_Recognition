"""
AI Insights — Generate a personalized 3-step study plan via the Anthropic API.
"""

from __future__ import annotations
import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.services.adaptive import ability_label

load_dotenv()

_client = None

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
    elif score < 0.7:
        return "Intermediate"
    else:
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
        if stats["total"] > 0 and (stats["correct"] / stats["total"]) < 0.60
    ]

    topic_detail = "\n".join(
        f"- {topic}: {stats['correct']}/{stats['total']} correct"
        for topic, stats in topic_breakdown.items()
    )

    return f"""
    ```

    You are an expert GRE tutor analyzing a student's adaptive test performance.

    Student: {student_name}
    Level: {level}
    Accuracy: {accuracy:.0%}

    Topic Breakdown
    {topic_detail}

    Weak Topics: {", ".join(weak_topics) if weak_topics else "None"}

    Create a short **3-step personalized study plan**.
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


# def _build_prompt(
#     student_name: str,
#     final_ability: float,
#     total_questions: int,
#     correct_count: int,
#     topic_breakdown: dict[str, dict],
# ) -> str:
#     accuracy = correct_count / total_questions if total_questions else 0
#     level = ability_label(final_ability)

#     # Identify weak topics (accuracy < 60 %)
#     weak_topics = [
#         topic
#         for topic, stats in topic_breakdown.items()
#         if stats["total"] > 0 and (stats["correct"] / stats["total"]) < 0.60
#     ]
#     strong_topics = [
#         topic
#         for topic, stats in topic_breakdown.items()
#         if stats["total"] > 0 and (stats["correct"] / stats["total"]) >= 0.80
#     ]

#     topic_detail = "\n".join(
#         f"  - {topic}: {stats['correct']}/{stats['total']} correct "
#         f"({100 * stats['correct'] // stats['total'] if stats['total'] else 0}%)"
#         for topic, stats in topic_breakdown.items()
#     )

#     return f"""You are an expert GRE tutor analyzing a student's adaptive test performance.

# ## Student Performance Summary
# - Student: {student_name}
# - Estimated Ability Level: {level} (score: {final_ability:.2f}/1.00)
# - Overall Accuracy: {accuracy:.0%} ({correct_count}/{total_questions} correct)

# ## Topic Breakdown
# {topic_detail}

# ## Identified Weak Areas
# {", ".join(weak_topics) if weak_topics else "No major weak areas detected."}

# ## Strong Areas  
# {", ".join(strong_topics) if strong_topics else "Still developing."}

# ---

# Based on this data, write a concise, actionable **3-Step Personalized Study Plan** for {student_name}.

# Requirements:
# 1. Each step must be specific to their actual weak topics above.
# 2. Include concrete study techniques (e.g., flashcards, practice sets, specific strategies).
# 3. Suggest a realistic daily time commitment per step.
# 4. Keep the tone encouraging but honest.
# 5. Format as:

# **Step 1: [Title]**
# [2-3 sentences of actionable advice]

# **Step 2: [Title]**
# [2-3 sentences of actionable advice]

# **Step 3: [Title]**
# [2-3 sentences of actionable advice]

# **Estimated Timeline:** [X weeks]
# """


# def generate_study_plan(
#     student_name: str,
#     final_ability: float,
#     total_questions: int,
#     correct_count: int,
#     topic_breakdown: dict[str, dict],
# ) -> str:
#     """
#     Call Claude claude-sonnet-4-20250514 to generate a personalized study plan.
#     Returns the plan as a markdown-formatted string.
#     Falls back gracefully if the API is unavailable.
#     """
#     prompt = _build_prompt(
#         student_name, final_ability, total_questions, correct_count, topic_breakdown
#     )

#     try:
#         client = _get_client()
#         message = client.messages.create(
#             model="claude-sonnet-4-20250514",
#             max_tokens=800,
#             messages=[{"role": "user", "content": prompt}],
#         )
#         return message.content[0].text.strip()

#     except Exception as exc:
#         # Graceful fallback — never crash the session result endpoint
#         level = ability_label(final_ability)
#         return (
#             f"⚠️ AI study plan generation failed ({exc.__class__.__name__}: {exc}).\n\n"
#             f"**Fallback Summary:** You performed at the **{level}** level "
#             f"with {correct_count}/{total_questions} correct answers. "
#             f"Focus extra time on: {', '.join(topic_breakdown.keys()) or 'all topics'}."
#         )
