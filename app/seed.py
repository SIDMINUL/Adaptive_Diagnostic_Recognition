"""
Seed the MongoDB `questions` collection with 25 GRE-style questions
spanning Algebra, Geometry, Vocabulary, Reading Comprehension, and
Data Interpretation.

Run:
    python -m app.seed
"""

from __future__ import annotations
import asyncio
import sys
from app.services.database import connect_db, questions_col, close_db

QUESTIONS = [
    # ─── Algebra (5) ──────────────────────────────────────────────────────────
    {
        "question_id": "q_alg_01",
        "text": "If 3x − 7 = 14, what is the value of x?",
        "options": [
            {"key": "A", "text": "5"},
            {"key": "B", "text": "7"},
            {"key": "C", "text": "9"},
            {"key": "D", "text": "3"},
        ],
        "correct_answer": "B",
        "difficulty": 0.15,
        "discrimination": 1.1,
        "topic": "Algebra",
        "tags": ["linear_equations", "gre_quant"],
    },
    {
        "question_id": "q_alg_02",
        "text": "What is the solution set of |2x − 4| ≤ 6?",
        "options": [
            {"key": "A", "text": "−1 ≤ x ≤ 5"},
            {"key": "B", "text": "x ≤ −1 or x ≥ 5"},
            {"key": "C", "text": "−1 < x < 5"},
            {"key": "D", "text": "x ≤ 5"},
        ],
        "correct_answer": "A",
        "difficulty": 0.45,
        "discrimination": 1.3,
        "topic": "Algebra",
        "tags": ["absolute_value", "inequalities", "gre_quant"],
    },
    {
        "question_id": "q_alg_03",
        "text": (
            "If f(x) = x² − 4x + 3, for which values of x does f(x) = 0?"
        ),
        "options": [
            {"key": "A", "text": "x = 1, x = 3"},
            {"key": "B", "text": "x = −1, x = −3"},
            {"key": "C", "text": "x = 1, x = −3"},
            {"key": "D", "text": "x = 2, x = 3"},
        ],
        "correct_answer": "A",
        "difficulty": 0.40,
        "discrimination": 1.2,
        "topic": "Algebra",
        "tags": ["quadratics", "factoring", "gre_quant"],
    },
    {
        "question_id": "q_alg_04",
        "text": (
            "A jar contains red and blue marbles in the ratio 3:5. "
            "If there are 24 red marbles, how many blue marbles are there?"
        ),
        "options": [
            {"key": "A", "text": "32"},
            {"key": "B", "text": "40"},
            {"key": "C", "text": "48"},
            {"key": "D", "text": "36"},
        ],
        "correct_answer": "B",
        "difficulty": 0.30,
        "discrimination": 1.1,
        "topic": "Algebra",
        "tags": ["ratios", "proportions", "gre_quant"],
    },
    {
        "question_id": "q_alg_05",
        "text": (
            "If p and q are roots of x² − 5x + 6 = 0, what is the value of p² + q²?"
        ),
        "options": [
            {"key": "A", "text": "13"},
            {"key": "B", "text": "25"},
            {"key": "C", "text": "12"},
            {"key": "D", "text": "17"},
        ],
        "correct_answer": "A",
        "difficulty": 0.70,
        "discrimination": 1.4,
        "topic": "Algebra",
        "tags": ["vietas_formulas", "advanced_algebra", "gre_quant"],
    },

    # ─── Geometry (5) ─────────────────────────────────────────────────────────
    {
        "question_id": "q_geo_01",
        "text": "A rectangle has a length of 12 and a width of 5. What is its diagonal?",
        "options": [
            {"key": "A", "text": "13"},
            {"key": "B", "text": "17"},
            {"key": "C", "text": "11"},
            {"key": "D", "text": "15"},
        ],
        "correct_answer": "A",
        "difficulty": 0.25,
        "discrimination": 1.0,
        "topic": "Geometry",
        "tags": ["pythagorean_theorem", "rectangles", "gre_quant"],
    },
    {
        "question_id": "q_geo_02",
        "text": (
            "Two parallel lines are cut by a transversal. "
            "If one interior angle is 65°, what is the co-interior (same-side interior) angle?"
        ),
        "options": [
            {"key": "A", "text": "65°"},
            {"key": "B", "text": "115°"},
            {"key": "C", "text": "125°"},
            {"key": "D", "text": "75°"},
        ],
        "correct_answer": "B",
        "difficulty": 0.35,
        "discrimination": 1.1,
        "topic": "Geometry",
        "tags": ["parallel_lines", "transversals", "gre_quant"],
    },
    {
        "question_id": "q_geo_03",
        "text": (
            "Circle O has radius 7. What is the area of a sector with central angle 90°? "
            "(Leave in terms of π.)"
        ),
        "options": [
            {"key": "A", "text": "49π/4"},
            {"key": "B", "text": "14π"},
            {"key": "C", "text": "49π/2"},
            {"key": "D", "text": "7π"},
        ],
        "correct_answer": "A",
        "difficulty": 0.50,
        "discrimination": 1.2,
        "topic": "Geometry",
        "tags": ["circles", "sectors", "gre_quant"],
    },
    {
        "question_id": "q_geo_04",
        "text": (
            "A cube has a surface area of 150 cm². What is the length of one edge?"
        ),
        "options": [
            {"key": "A", "text": "4 cm"},
            {"key": "B", "text": "5 cm"},
            {"key": "C", "text": "6 cm"},
            {"key": "D", "text": "25 cm"},
        ],
        "correct_answer": "B",
        "difficulty": 0.45,
        "discrimination": 1.2,
        "topic": "Geometry",
        "tags": ["surface_area", "cubes", "gre_quant"],
    },
    {
        "question_id": "q_geo_05",
        "text": (
            "In triangle ABC, AB = AC and the vertex angle A = 40°. "
            "What is the measure of angle B?"
        ),
        "options": [
            {"key": "A", "text": "40°"},
            {"key": "B", "text": "60°"},
            {"key": "C", "text": "70°"},
            {"key": "D", "text": "80°"},
        ],
        "correct_answer": "C",
        "difficulty": 0.35,
        "discrimination": 1.0,
        "topic": "Geometry",
        "tags": ["isosceles_triangles", "angle_sum", "gre_quant"],
    },

    # ─── Vocabulary (5) ───────────────────────────────────────────────────────
    {
        "question_id": "q_voc_01",
        "text": "Choose the word most similar in meaning to EPHEMERAL.",
        "options": [
            {"key": "A", "text": "Eternal"},
            {"key": "B", "text": "Transient"},
            {"key": "C", "text": "Robust"},
            {"key": "D", "text": "Ambiguous"},
        ],
        "correct_answer": "B",
        "difficulty": 0.30,
        "discrimination": 1.1,
        "topic": "Vocabulary",
        "tags": ["synonyms", "gre_verbal"],
    },
    {
        "question_id": "q_voc_02",
        "text": "Choose the word most nearly OPPOSITE to LOQUACIOUS.",
        "options": [
            {"key": "A", "text": "Garrulous"},
            {"key": "B", "text": "Verbose"},
            {"key": "C", "text": "Taciturn"},
            {"key": "D", "text": "Eloquent"},
        ],
        "correct_answer": "C",
        "difficulty": 0.55,
        "discrimination": 1.3,
        "topic": "Vocabulary",
        "tags": ["antonyms", "gre_verbal"],
    },
    {
        "question_id": "q_voc_03",
        "text": (
            "The professor's lecture was so _____ that even the most attentive students "
            "struggled to stay focused.\n(Select the word that best fits the blank.)"
        ),
        "options": [
            {"key": "A", "text": "Scintillating"},
            {"key": "B", "text": "Pedantic"},
            {"key": "C", "text": "Soporific"},
            {"key": "D", "text": "Trenchant"},
        ],
        "correct_answer": "C",
        "difficulty": 0.60,
        "discrimination": 1.2,
        "topic": "Vocabulary",
        "tags": ["sentence_completion", "gre_verbal"],
    },
    {
        "question_id": "q_voc_04",
        "text": "Which word best describes someone who is PARSIMONIOUS?",
        "options": [
            {"key": "A", "text": "Generous"},
            {"key": "B", "text": "Miserly"},
            {"key": "C", "text": "Reckless"},
            {"key": "D", "text": "Scholarly"},
        ],
        "correct_answer": "B",
        "difficulty": 0.40,
        "discrimination": 1.0,
        "topic": "Vocabulary",
        "tags": ["word_meaning", "gre_verbal"],
    },
    {
        "question_id": "q_voc_05",
        "text": (
            "Her writing style is best described as PROLIX, meaning it tends to be:"
        ),
        "options": [
            {"key": "A", "text": "Concise and clear"},
            {"key": "B", "text": "Unnecessarily long"},
            {"key": "C", "text": "Emotionally charged"},
            {"key": "D", "text": "Technically dense"},
        ],
        "correct_answer": "B",
        "difficulty": 0.65,
        "discrimination": 1.3,
        "topic": "Vocabulary",
        "tags": ["advanced_vocabulary", "gre_verbal"],
    },

    # ─── Reading Comprehension (5) ────────────────────────────────────────────
    {
        "question_id": "q_rc_01",
        "text": (
            "Passage: 'The Amazon rainforest absorbs roughly 2 billion tons of CO₂ "
            "annually, acting as a vital carbon sink. However, deforestation has reduced "
            "this capacity by nearly 30% over the past two decades.'\n\n"
            "The passage implies that deforestation has:"
        ),
        "options": [
            {"key": "A", "text": "Increased the Amazon's CO₂ absorption"},
            {"key": "B", "text": "Had no effect on carbon sequestration"},
            {"key": "C", "text": "Reduced the forest's ability to absorb CO₂"},
            {"key": "D", "text": "Doubled the forest's carbon output"},
        ],
        "correct_answer": "C",
        "difficulty": 0.20,
        "discrimination": 1.0,
        "topic": "Reading Comprehension",
        "tags": ["inference", "gre_verbal"],
    },
    {
        "question_id": "q_rc_02",
        "text": (
            "Passage: 'Cognitive load theory posits that working memory has limited "
            "capacity. Instructional designs that ignore this risk overwhelming learners, "
            "resulting in poor retention despite high engagement.'\n\n"
            "The author would most likely agree that:"
        ),
        "options": [
            {"key": "A", "text": "Engagement alone guarantees learning"},
            {"key": "B", "text": "Instructional design should account for memory limits"},
            {"key": "C", "text": "Working memory is effectively unlimited"},
            {"key": "D", "text": "Retention is unrelated to instructional design"},
        ],
        "correct_answer": "B",
        "difficulty": 0.40,
        "discrimination": 1.2,
        "topic": "Reading Comprehension",
        "tags": ["author_inference", "gre_verbal"],
    },
    {
        "question_id": "q_rc_03",
        "text": (
            "Passage: 'Historians have long debated whether the fall of Rome was "
            "primarily an internal collapse or the result of external invasions. Recent "
            "scholarship suggests the two forces were deeply intertwined, each accelerating "
            "the other.'\n\n"
            "The word 'intertwined' most nearly means:"
        ),
        "options": [
            {"key": "A", "text": "Contradictory"},
            {"key": "B", "text": "Independent"},
            {"key": "C", "text": "Inseparably connected"},
            {"key": "D", "text": "Historically irrelevant"},
        ],
        "correct_answer": "C",
        "difficulty": 0.35,
        "discrimination": 1.1,
        "topic": "Reading Comprehension",
        "tags": ["vocabulary_in_context", "gre_verbal"],
    },
    {
        "question_id": "q_rc_04",
        "text": (
            "Passage: 'While the placebo effect is often dismissed as mere suggestion, "
            "neuroimaging studies show measurable changes in brain activity following "
            "placebo treatment—including the release of endogenous opioids.'\n\n"
            "The passage challenges the idea that the placebo effect is:"
        ),
        "options": [
            {"key": "A", "text": "Physically real"},
            {"key": "B", "text": "Purely psychological with no physiological basis"},
            {"key": "C", "text": "Studied using brain imaging"},
            {"key": "D", "text": "Related to pain management"},
        ],
        "correct_answer": "B",
        "difficulty": 0.55,
        "discrimination": 1.3,
        "topic": "Reading Comprehension",
        "tags": ["critical_reasoning", "gre_verbal"],
    },
    {
        "question_id": "q_rc_05",
        "text": (
            "Passage: 'Schumpeter's concept of creative destruction holds that capitalism "
            "thrives through cycles of innovation that simultaneously render existing "
            "industries obsolete. This is not a flaw but the engine of long-run growth.'\n\n"
            "Schumpeter's view of capitalism is best described as:"
        ),
        "options": [
            {"key": "A", "text": "Pessimistic about its long-term viability"},
            {"key": "B", "text": "Neutral — neither positive nor negative"},
            {"key": "C", "text": "Cautiously critical of its disruptions"},
            {"key": "D", "text": "Optimistic, viewing disruption as integral to progress"},
        ],
        "correct_answer": "D",
        "difficulty": 0.75,
        "discrimination": 1.4,
        "topic": "Reading Comprehension",
        "tags": ["complex_inference", "gre_verbal"],
    },

    # ─── Data Interpretation (5) ──────────────────────────────────────────────
    {
        "question_id": "q_di_01",
        "text": (
            "A store's monthly revenues (in $000s) for Q1 were: Jan=120, Feb=90, Mar=150. "
            "What was the average monthly revenue for Q1?"
        ),
        "options": [
            {"key": "A", "text": "$110,000"},
            {"key": "B", "text": "$120,000"},
            {"key": "C", "text": "$130,000"},
            {"key": "D", "text": "$115,000"},
        ],
        "correct_answer": "B",
        "difficulty": 0.20,
        "discrimination": 1.0,
        "topic": "Data Interpretation",
        "tags": ["averages", "gre_quant"],
    },
    {
        "question_id": "q_di_02",
        "text": (
            "In a survey of 200 students, 60% preferred online learning. "
            "Of those, 25% also reported lower academic performance. "
            "How many students preferred online learning AND reported lower performance?"
        ),
        "options": [
            {"key": "A", "text": "25"},
            {"key": "B", "text": "30"},
            {"key": "C", "text": "45"},
            {"key": "D", "text": "50"},
        ],
        "correct_answer": "B",
        "difficulty": 0.40,
        "discrimination": 1.2,
        "topic": "Data Interpretation",
        "tags": ["percentages", "compound_percent", "gre_quant"],
    },
    {
        "question_id": "q_di_03",
        "text": (
            "A dataset has values: 4, 8, 15, 16, 23, 42. "
            "What is the median of this dataset?"
        ),
        "options": [
            {"key": "A", "text": "15"},
            {"key": "B", "text": "15.5"},
            {"key": "C", "text": "16"},
            {"key": "D", "text": "18"},
        ],
        "correct_answer": "B",
        "difficulty": 0.30,
        "discrimination": 1.1,
        "topic": "Data Interpretation",
        "tags": ["median", "statistics", "gre_quant"],
    },
    {
        "question_id": "q_di_04",
        "text": (
            "Company X had profits of $500,000 in Year 1 and $650,000 in Year 2. "
            "What was the percentage increase in profits?"
        ),
        "options": [
            {"key": "A", "text": "13%"},
            {"key": "B", "text": "23%"},
            {"key": "C", "text": "30%"},
            {"key": "D", "text": "15%"},
        ],
        "correct_answer": "C",
        "difficulty": 0.35,
        "discrimination": 1.0,
        "topic": "Data Interpretation",
        "tags": ["percent_change", "gre_quant"],
    },
    {
        "question_id": "q_di_05",
        "text": (
            "The standard deviation of dataset A is 3 and dataset B is 9. "
            "Which statement is correct?"
        ),
        "options": [
            {"key": "A", "text": "Dataset A has more variability than B"},
            {"key": "B", "text": "Dataset B has more variability than A"},
            {"key": "C", "text": "Both datasets have equal variability"},
            {"key": "D", "text": "Standard deviation does not measure variability"},
        ],
        "correct_answer": "B",
        "difficulty": 0.50,
        "discrimination": 1.2,
        "topic": "Data Interpretation",
        "tags": ["standard_deviation", "statistics", "gre_quant"],
    },
]


async def seed() -> None:
    await connect_db()
    col = questions_col()
    inserted = 0
    skipped = 0

    for q in QUESTIONS:
        existing = await col.find_one({"question_id": q["question_id"]})
        if existing:
            skipped += 1
            continue
        await col.insert_one(q)
        inserted += 1

    print(f"[Seed] Done — {inserted} inserted, {skipped} already existed.")
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
