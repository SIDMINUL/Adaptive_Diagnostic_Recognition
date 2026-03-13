"""
Adaptive Algorithm — 1-Parameter Logistic IRT (1PL Rasch model).

Key concepts
------------
θ  (theta)  : Student ability estimate, mapped to [0, 1].
b           : Item difficulty parameter, mapped to [0, 1].

IRT probability of a correct response:
    P(correct | θ, b) = 1 / (1 + exp(-D * a * (θ - b)))
where D = 1.702 (scaling constant) and a = discrimination (default 1.0).

Ability update (MLE-inspired gradient step)
-------------------------------------------
After each response, we update θ using a simplified Bayesian / EAP step:
    error = is_correct - P(correct | θ, b)
    θ_new = θ + learning_rate * error

The learning_rate decreases as more questions are answered, providing
convergence similar to the Newton–Raphson update used in full MLE-CAT.

Question selection
------------------
Select the question whose difficulty is CLOSEST to the current θ,
from the pool of unanswered questions.  Ties broken by highest discrimination.
"""

from __future__ import annotations
import math
from dataclasses import dataclass

D_CONSTANT = 1.702   # IRT scaling constant
INITIAL_ABILITY = 0.5
MAX_QUESTIONS = 10
MIN_ABILITY = 0.05
MAX_ABILITY = 0.95


@dataclass
class IRTQuestion:
    question_id: str
    difficulty: float        # b-parameter
    discrimination: float    # a-parameter


def irt_probability(theta: float, b: float, a: float = 1.0) -> float:
    """
    Compute P(correct) under the 2PL IRT model.
    θ and b are both in [0, 1] but we centre them around 0 for the logistic.
    """
    # Map [0,1] → [−2, +2] so the logistic has meaningful range
    theta_c = (theta - 0.5) * 4
    b_c = (b - 0.5) * 4
    exponent = -D_CONSTANT * a * (theta_c - b_c)
    return 1.0 / (1.0 + math.exp(exponent))


def update_ability(
    theta: float,
    is_correct: bool,
    b: float,
    a: float = 1.0,
    questions_answered: int = 1,
) -> float:
    """
    MLE gradient-step update for ability.
    Learning rate decays with number of answered questions.
    """
    p = irt_probability(theta, b, a)
    response = 1.0 if is_correct else 0.0
    # Decaying step size — starts at 0.15, halves every 5 items
    learning_rate = 0.15 * (0.5 ** ((questions_answered - 1) // 5))
    delta = learning_rate * (response - p)
    new_theta = theta + delta
    return max(MIN_ABILITY, min(MAX_ABILITY, new_theta))


def select_next_question(
    current_ability: float,
    candidate_questions: list[IRTQuestion],
) -> IRTQuestion | None:
    """
    Maximum Information criterion (simplified):
    Choose the question closest in difficulty to current θ.
    Break ties by highest discrimination.
    """
    if not candidate_questions:
        return None
    return min(
        candidate_questions,
        key=lambda q: (abs(q.difficulty - current_ability), -q.discrimination),
    )


def information(theta: float, b: float, a: float = 1.0) -> float:
    """Fisher information of an item at ability level θ."""
    p = irt_probability(theta, b, a)
    q = 1.0 - p
    return (D_CONSTANT * a) ** 2 * p * q


def ability_label(theta: float) -> str:
    """Human-readable label for a given θ value."""
    if theta < 0.25:
        return "Beginner"
    elif theta < 0.45:
        return "Developing"
    elif theta < 0.60:
        return "Intermediate"
    elif theta < 0.75:
        return "Proficient"
    else:
        return "Advanced"
