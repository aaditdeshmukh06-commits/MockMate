"""
MockMate - Report Generation
Aggregates QA evaluations and body language metrics into final reports.
Adapted from mock-server.js
"""

import time
from typing import Dict, List, Any, Optional


def calculate_category_scores(avg_score: float) -> Dict[str, int]:
    """Calculate category scores based on average QA score."""
    return {
        "technical": round(avg_score * 0.95),
        "communication": round(avg_score * 1.05),
        "confidence": round(avg_score * 0.9),
        "problemSolving": round(avg_score * 0.88),
        "bodyLanguage": round(avg_score * 0.92),
    }


def calculate_body_language_summary(metrics: List[Dict]) -> Dict[str, Any]:
    """Calculate body language summary from metrics list."""
    if not metrics:
        return {
            "averageEyeContact": 80,
            "averagePosture": 75,
            "averageGestures": 70,
            "averageAttention": 85,
            "presencePercentage": 90,
            "feedback": [
                "Good eye contact maintained",
                "Good posture",
            ],
        }

    bl_scores = {
        "eyeContact": sum(m.get("eyeContactScore", 0) for m in metrics) / len(metrics),
        "posture": sum(m.get("postureScore", 0) for m in metrics) / len(metrics),
        "gestures": sum(m.get("gestureScore", 0) for m in metrics) / len(metrics),
        "attention": sum(m.get("attentionScore", 0) for m in metrics) / len(metrics),
        "presence": sum(1 for m in metrics if m.get("presenceDetected", False)) / len(metrics) * 100,
    }

    feedback = []
    if bl_scores["eyeContact"] > 75:
        feedback.append("Good eye contact maintained")
    else:
        feedback.append("Work on maintaining eye contact")

    if bl_scores["posture"] > 70:
        feedback.append("Good posture")
    else:
        feedback.append("Improve posture during interview")

    return {
        "averageEyeContact": round(bl_scores["eyeContact"]),
        "averagePosture": round(bl_scores["posture"]),
        "averageGestures": round(bl_scores["gestures"]),
        "averageAttention": round(bl_scores["attention"]),
        "presencePercentage": round(bl_scores["presence"]),
        "feedback": feedback,
    }


def generate_ai_summary(
    overall_score: int,
    role: str,
    category_scores: Dict[str, int],
    qa_history: List[Dict],
) -> Dict[str, Any]:
    """Generate AI summary based on scores and QA history."""

    # Determine candidate level
    if overall_score > 80:
        candidate_level = "senior"
        overall_feedback = f"Excellent performance in {role} interview. Strong technical and communication skills demonstrated."
    elif overall_score > 60:
        candidate_level = "intermediate"
        overall_feedback = f"Good performance in {role} interview. Solid foundation with room for growth."
    else:
        candidate_level = "junior"
        overall_feedback = f"Needs improvement in {role} interview. Focus on elaborating answers and technical depth."

    # Extract common strengths from evaluations
    all_strengths = []
    all_improvements = []
    for qa in qa_history:
        eval_data = qa.get("evaluation", {})
        all_strengths.extend(eval_data.get("strengths", []))
        all_improvements.extend(eval_data.get("improvements", []))

    # Deduplicate and limit
    unique_strengths = list(dict.fromkeys(all_strengths))[:3]
    unique_improvements = list(dict.fromkeys(all_improvements))[:3]

    if not unique_strengths:
        unique_strengths = ["Technical knowledge", "Clear communication", "Problem-solving approach"]
    if not unique_improvements:
        unique_improvements = ["Add more specific examples", "Slow down speech pace", "Elaborate on technical decisions"]

    return {
        "overallFeedback": overall_feedback,
        "strengths": unique_strengths,
        "improvements": unique_improvements,
        "recommendations": [
            "Practice STAR method for behavioral questions",
            "Record yourself answering common questions",
            "Review system design fundamentals",
        ],
        "candidateLevel": candidate_level,
    }


def generate_report(
    session_id: str,
    user_id: str,
    role: str,
    difficulty: str,
    qa_history: List[Dict],
    body_language_metrics: List[Dict],
    start_time: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate complete interview report from session data.
    """
    # Calculate average score from evaluations
    scores = [qa.get("evaluation", {}).get("score", 0) for qa in qa_history]
    avg_score = sum(scores) / len(scores) if scores else 75

    # Category scores
    category_scores = calculate_category_scores(avg_score)

    # Overall score
    overall_score = round(sum(category_scores.values()) / len(category_scores))

    # Body language summary
    body_language_summary = calculate_body_language_summary(body_language_metrics)

    # AI summary
    ai_summary = generate_ai_summary(overall_score, role, category_scores, qa_history)

    # Duration
    duration_minutes = 15
    if start_time:
        duration_minutes = max(1, round((time.time() * 1000 - start_time) / 60000))

    return {
        "sessionId": session_id,
        "userId": user_id,
        "role": role,
        "difficulty": difficulty,
        "overallScore": overall_score,
        "categoryScores": category_scores,
        "qaHistory": qa_history,
        "bodyLanguageSummary": body_language_summary,
        "aiSummary": ai_summary,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "durationMinutes": duration_minutes,
    }