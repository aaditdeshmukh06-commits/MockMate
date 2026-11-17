"""
MockMate - Question Bank
Role and difficulty specific interview questions.
Adapted from mock-server.js
"""

from typing import Dict, List

# Question bank organized by difficulty and role
QUESTIONS: Dict[str, Dict[str, List[str]]] = {
    "easy": {
        "Software Engineer": [
            "Tell me about yourself and your background.",
            "What programming languages are you most comfortable with?",
            "Describe a project you worked on recently.",
            "How do you approach debugging a difficult issue?",
            "What do you know about our company?",
        ],
        "Data Scientist": [
            "Tell me about your experience with data analysis.",
            "What tools do you use for data visualization?",
            "Explain a machine learning project you've worked on.",
            "How do you handle missing data in a dataset?",
            "What interests you about this role?",
        ],
        "Product Manager": [
            "Tell me about a product you launched.",
            "How do you prioritize features?",
            "Describe a time you had to say no to a stakeholder.",
            "How do you measure product success?",
            "What's your favorite product and why?",
        ],
    },
    "medium": {
        "Software Engineer": [
            "Explain the difference between REST and GraphQL.",
            "How would you design a URL shortener service?",
            "Describe a time you optimized a slow database query.",
            "What are the trade-offs of microservices vs monolith?",
            "How do you ensure code quality in your team?",
        ],
        "Data Scientist": [
            "Explain bias-variance tradeoff.",
            "How would you detect fraud in credit card transactions?",
            "Describe a time your model failed in production.",
            "What's the difference between L1 and L2 regularization?",
            "How do you explain technical results to non-technical stakeholders?",
        ],
        "Product Manager": [
            "How do you handle competing priorities from different teams?",
            "Describe a product decision you made based on data.",
            "How would you improve our onboarding flow?",
            "Tell me about a time you failed and what you learned.",
            "How do you balance technical debt vs new features?",
        ],
    },
    "hard": {
        "Software Engineer": [
            "Design a distributed rate limiter.",
            "How would you implement eventual consistency?",
            "Explain the CAP theorem with real-world examples.",
            "Design a system like Uber's dispatch.",
            "How do you handle distributed transactions?",
        ],
        "Data Scientist": [
            "Design an A/B testing framework.",
            "How would you build a recommendation system from scratch?",
            "Explain transformer architecture attention mechanism.",
            "How do you handle concept drift in production models?",
            "Design an experiment to measure feature impact.",
        ],
        "Product Manager": [
            "How would you enter a new market with an existing product?",
            "Design a pricing strategy for a SaaS product.",
            "How do you manage a product through its lifecycle?",
            "Describe a strategic pivot you led.",
            "How do you align engineering and business goals?",
        ],
    },
}

# Default fallback questions
DEFAULT_QUESTIONS = [
    "Tell me about a challenging problem you solved.",
    "Describe your greatest professional achievement.",
    "How do you handle tight deadlines?",
    "What's your approach to learning new technologies?",
    "Where do you see yourself in 5 years?",
]


def get_question(role: str, difficulty: str, question_number: int) -> str:
    """
    Get a specific question for the given role, difficulty, and question number (1-indexed).
    """
    difficulty = difficulty.lower()
    role_questions = QUESTIONS.get(difficulty, {}).get(role, [])

    if not role_questions:
        # Fallback to Software Engineer questions for the difficulty
        role_questions = QUESTIONS.get(difficulty, {}).get("Software Engineer", [])

    if not role_questions:
        # Final fallback
        role_questions = DEFAULT_QUESTIONS

    # question_number is 1-indexed
    index = question_number - 1
    if 0 <= index < len(role_questions):
        return role_questions[index]

    # If we've exhausted the questions, return a generic one
    return DEFAULT_QUESTIONS[index % len(DEFAULT_QUESTIONS)]


def get_total_questions() -> int:
    """Return the standard number of questions per interview."""
    return 5


def get_all_questions_for_role(role: str, difficulty: str) -> List[str]:
    """Get all 5 questions for a role/difficulty combination."""
    return [get_question(role, difficulty, i) for i in range(1, 6)]