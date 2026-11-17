"""
MockMate - Answer Evaluation Logic
Improved scoring algorithm with gibberish detection.
Adapted from mock-server.js with enhanced detection.
"""

import re
from typing import Dict, List


def evaluate_answer(answer: str, question_number: int = 1) -> Dict:
    """
    Evaluate an interview answer and return scoring metrics.

    Improved algorithm:
    - Word counting with validation
    - Gibberish detection (repeated chars, low diversity, no vowels)
    - Positive signal detection (examples, technical terms, structure)
    - Base score based on word count with penalties for gibberish
    """
    trimmed = answer.strip()
    words = trimmed.split()
    word_count = len(words)
    char_count = len(trimmed)

    # Gibberish detection
    unique_chars = len(set(trimmed.lower()))
    char_diversity = unique_chars / max(1, char_count)
    has_vowels = bool(re.search(r'[aeiou]', trimmed, re.IGNORECASE))
    has_repeated_chars = bool(re.search(r'(.)\1{3,}', trimmed))  # 4+ same chars in a row
    avg_word_length = char_count / max(1, word_count)

    # Gibberish penalty calculation
    gibberish_penalty = 0
    if not has_vowels:
        gibberish_penalty += 30
    if has_repeated_chars:
        gibberish_penalty += 25
    if char_diversity < 0.15:
        gibberish_penalty += 20
    if avg_word_length > 15:
        gibberish_penalty += 15
    if word_count < 3:
        gibberish_penalty += 20

    # Positive signals
    has_examples = bool(re.search(
        r'example|instance|project|experience|built|created|developed|implemented|solved',
        trimmed, re.IGNORECASE
    ))
    has_technical = bool(re.search(
        r'api|database|algorithm|framework|architecture|system|design|scale|performance|optimize|debug|test|deploy|ci/cd|docker|kubernetes|aws|cloud',
        trimmed, re.IGNORECASE
    ))
    has_structure = bool(re.search(
        r'first|second|then|finally|because|therefore|however|additionally|furthermore',
        trimmed, re.IGNORECASE
    ))

    # Base score: 20-50 based on word count (capped at 30 words)
    base_score = min(20 + word_count, 50)

    # Bonuses
    if has_examples:
        base_score += 10
    if has_technical:
        base_score += 10
    if has_structure:
        base_score += 5
    if word_count >= 20:
        base_score += 5
    if word_count >= 50:
        base_score += 5

    # Apply gibberish penalty
    base_score = max(10, base_score - gibberish_penalty)
    base_score = min(base_score, 95)

    # Generate feedback
    if gibberish_penalty > 30:
        feedback = "Answer appears to be gibberish or too short. Please provide a meaningful response."
    elif gibberish_penalty > 15:
        feedback = "Answer needs more substance. Try to elaborate with specific examples."
    elif base_score >= 70:
        feedback = "Strong answer with good detail and relevant examples."
    elif base_score >= 50:
        feedback = "Decent answer. Consider adding more specific examples or technical details."
    else:
        feedback = "Answer is too brief. Please elaborate more on your experience."

    # Determine strengths and improvements
    strengths = []
    improvements = []

    if has_examples:
        strengths.append("Good use of examples")
        strengths.append("Clear communication")
    elif has_technical:
        strengths.append("Technical knowledge shown")
    else:
        strengths.append("Attempted to answer")

    if gibberish_penalty > 15:
        improvements.extend([
            "Provide a coherent, meaningful answer",
            "Use real words and sentences",
        ])
    elif has_technical:
        improvements.extend([
            "Add more technical depth",
            "Include specific examples",
        ])
    else:
        improvements.extend([
            "Add specific examples",
            "Include technical details",
            "Elaborate more on your experience",
        ])

    return {
        "score": round(base_score),
        "confidence": round(base_score * 0.9),
        "clarity": round(base_score * 0.95),
        "relevance": round(base_score * 0.9),
        "technicalAccuracy": round(base_score * 0.85),
        "communication": round(base_score * 0.9),
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback,
        "wordCount": word_count,
        "gibberishPenalty": gibberish_penalty,
    }


def evaluate_batch(answers: List[str]) -> List[Dict]:
    """Evaluate multiple answers at once."""
    return [evaluate_answer(answer, i + 1) for i, answer in enumerate(answers)]