"""
Unit tests for the IRT adaptive algorithm (no MongoDB required).
Run: pytest tests/
"""

import pytest
from app.services.adaptive import (
    irt_probability, update_ability, select_next_question,
    information, ability_label, IRTQuestion,
    MIN_ABILITY, MAX_ABILITY,
)


# ─── irt_probability ──────────────────────────────────────────────────────────

class TestIRTProbability:
    def test_equal_ability_difficulty_is_near_half(self):
        """P(θ=b) ≈ 0.5 for any ability equal to difficulty."""
        p = irt_probability(0.5, 0.5)
        assert abs(p - 0.5) < 0.01

    def test_higher_ability_than_difficulty_increases_p(self):
        """When θ > b, P(correct) > 0.5."""
        p = irt_probability(0.8, 0.3)
        assert p > 0.5

    def test_lower_ability_than_difficulty_decreases_p(self):
        """When θ < b, P(correct) < 0.5."""
        p = irt_probability(0.2, 0.8)
        assert p < 0.5

    def test_output_bounded_between_0_and_1(self):
        for theta in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for b in [0.1, 0.5, 0.9]:
                p = irt_probability(theta, b)
                assert 0.0 < p < 1.0


# ─── update_ability ───────────────────────────────────────────────────────────

class TestUpdateAbility:
    def test_correct_answer_increases_ability(self):
        theta = 0.5
        new_theta = update_ability(theta, is_correct=True, b=0.5)
        assert new_theta > theta

    def test_incorrect_answer_decreases_ability(self):
        theta = 0.5
        new_theta = update_ability(theta, is_correct=False, b=0.5)
        assert new_theta < theta

    def test_ability_stays_within_bounds(self):
        # Edge: very high ability + correct on easy question
        result = update_ability(MAX_ABILITY, is_correct=True, b=0.1)
        assert result <= MAX_ABILITY

        # Edge: very low ability + wrong on hard question
        result = update_ability(MIN_ABILITY, is_correct=False, b=0.9)
        assert result >= MIN_ABILITY

    def test_step_size_decreases_with_more_answers(self):
        """Later updates should move θ less than earlier updates."""
        theta = 0.5
        delta_early = abs(update_ability(theta, True, 0.5, questions_answered=1) - theta)
        delta_late = abs(update_ability(theta, True, 0.5, questions_answered=10) - theta)
        assert delta_late < delta_early


# ─── select_next_question ─────────────────────────────────────────────────────

class TestSelectNextQuestion:
    def _make_questions(self, difficulties: list[float]) -> list[IRTQuestion]:
        return [
            IRTQuestion(question_id=f"q{i}", difficulty=d, discrimination=1.0)
            for i, d in enumerate(difficulties)
        ]

    def test_selects_closest_difficulty_to_ability(self):
        candidates = self._make_questions([0.1, 0.3, 0.6, 0.9])
        chosen = select_next_question(0.55, candidates)
        assert chosen.difficulty == 0.6

    def test_returns_none_for_empty_pool(self):
        assert select_next_question(0.5, []) is None

    def test_tiebreak_by_higher_discrimination(self):
        candidates = [
            IRTQuestion("q1", difficulty=0.5, discrimination=0.8),
            IRTQuestion("q2", difficulty=0.5, discrimination=1.5),
        ]
        chosen = select_next_question(0.5, candidates)
        assert chosen.question_id == "q2"


# ─── information ──────────────────────────────────────────────────────────────

class TestInformation:
    def test_maximum_information_at_ability_equals_difficulty(self):
        """Fisher information is maximised when θ ≈ b."""
        info_at_target = information(0.5, 0.5)
        info_far = information(0.1, 0.9)
        assert info_at_target > info_far

    def test_information_always_positive(self):
        for theta in [0.1, 0.5, 0.9]:
            for b in [0.1, 0.5, 0.9]:
                assert information(theta, b) > 0


# ─── ability_label ────────────────────────────────────────────────────────────

class TestAbilityLabel:
    def test_labels_cover_full_range(self):
        labels = {ability_label(t) for t in [0.1, 0.3, 0.5, 0.65, 0.85]}
        assert len(labels) == 5   # 5 distinct labels
