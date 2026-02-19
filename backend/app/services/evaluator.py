"""
Interview Evaluation Service

Evaluates:
- Technical accuracy of answers
- Communication quality
- Problem-solving ability
- Domain knowledge
- Overall performance

Generates:
- Interview scorecard
- Strengths & weaknesses
- Improvement suggestions
- Career recommendations
"""

import logging
from typing import Dict, List, Any, Optional
import asyncio
import re

logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluates interview responses and generates performance reports."""
    
    def __init__(self):
        self.model = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Initialize the evaluator."""
        self._initialized = True
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_keywords: List[str] = None,
        question_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Evaluate a single answer.
        
        Args:
            question: The interview question
            answer: Student's response
            expected_keywords: Keywords expected in the answer
            question_type: Type of question
            
        Returns:
            Evaluation with score and feedback
        """
        await self._ensure_initialized()
        
        if not answer or len(answer.strip()) < 10:
            return {
                "score": 2.0,
                "brief_feedback": "Response too short",
                "detailed_feedback": "Please provide a more detailed answer."
            }
        
        # Calculate keyword match score
        keyword_score = 0
        if expected_keywords:
            answer_lower = answer.lower()
            matches = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
            keyword_score = (matches / len(expected_keywords)) * 10 if expected_keywords else 5
        else:
            keyword_score = 5  # Default if no keywords
        
        # Calculate length score (longer, more detailed answers are better)
        word_count = len(answer.split())
        length_score = min(10, word_count / 10)  # Max at 100 words
        
        # Calculate structure score (presence of examples, explanations)
        structure_score = 5
        if any(word in answer.lower() for word in ["for example", "such as", "because", "therefore"]):
            structure_score += 2
        if any(word in answer.lower() for word in ["first", "second", "third", "step"]):
            structure_score += 2
        if "?" in answer:  # Engaging with follow-up
            structure_score += 1
        
        # Question type specific evaluation
        type_bonus = 0
        if question_type == "technical":
            # Look for technical terms
            technical_terms = ["algorithm", "function", "class", "method", "database", "api", "server", "client"]
            type_bonus = sum(1 for term in technical_terms if term in answer.lower())
        elif question_type == "hr":
            # Look for STAR method elements
            star_elements = ["situation", "task", "action", "result", "we", "team", "i"]
            type_bonus = sum(0.5 for elem in star_elements if elem in answer.lower())
        
        # Calculate final score
        raw_score = (keyword_score * 0.4 + length_score * 0.2 + structure_score * 0.3 + type_bonus * 0.1)
        final_score = round(max(1, min(10, raw_score)), 1)
        
        # Generate feedback
        feedback = self._generate_feedback(final_score, word_count, expected_keywords, answer)
        
        return {
            "score": final_score,
            "brief_feedback": self._get_brief_feedback(final_score),
            "detailed_feedback": feedback,
            "keyword_matches": sum(1 for kw in (expected_keywords or []) if kw.lower() in answer.lower())
        }
    
    def _get_brief_feedback(self, score: float) -> str:
        """Get brief feedback based on score."""
        if score >= 8:
            return "Excellent response!"
        elif score >= 6:
            return "Good answer, could add more detail."
        elif score >= 4:
            return "Adequate, but needs improvement."
        else:
            return "Needs significant improvement."
    
    def _generate_feedback(
        self,
        score: float,
        word_count: int,
        expected_keywords: List[str],
        answer: str
    ) -> str:
        """Generate detailed feedback."""
        feedback_parts = []
        
        if score >= 8:
            feedback_parts.append("Great job! Your response was comprehensive and well-structured.")
        elif score >= 6:
            feedback_parts.append("Good response.")
        else:
            feedback_parts.append("Your response could be improved.")
        
        if word_count < 30:
            feedback_parts.append("Try to provide more detailed explanations.")
        
        if expected_keywords:
            missed = [kw for kw in expected_keywords if kw.lower() not in answer.lower()]
            if missed:
                feedback_parts.append(f"Consider mentioning: {', '.join(missed[:3])}")
        
        return " ".join(feedback_parts)
    
    async def generate_final_report(
        self,
        questions: List[Dict],
        responses: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate final interview evaluation report.
        
        Args:
            questions: List of interview questions
            responses: List of student responses
            
        Returns:
            Complete evaluation report
        """
        await self._ensure_initialized()
        
        # Calculate scores
        scores = []
        question_scores = []
        
        for i, response in enumerate(responses):
            question = questions[response.get("question_idx", i)] if i < len(questions) else {}
            
            eval_result = await self.evaluate_answer(
                question=question.get("question_text", ""),
                answer=response.get("response_text", ""),
                expected_keywords=question.get("expected_keywords", []),
                question_type=question.get("question_type", "general")
            )
            
            scores.append(eval_result["score"])
            question_scores.append({
                "question_number": i + 1,
                "question_text": question.get("question_text", "")[:100],
                "score": eval_result["score"],
                "feedback": eval_result["brief_feedback"]
            })
        
        # Calculate overall scores
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Categorize scores by question type
        type_scores = {"technical": [], "hr": [], "project": [], "scenario": []}
        for i, response in enumerate(responses):
            if i < len(questions):
                q_type = questions[i].get("question_type", "general")
                if q_type in type_scores:
                    type_scores[q_type].append(scores[i])
        
        # Calculate category averages
        category_scores = {}
        for q_type, type_score_list in type_scores.items():
            if type_score_list:
                category_scores[q_type] = round(sum(type_score_list) / len(type_score_list), 1)
        
        # Determine strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for q_type, avg in category_scores.items():
            if avg >= 7:
                strengths.append(f"Strong {q_type} skills")
            elif avg < 5:
                weaknesses.append(f"Needs improvement in {q_type} areas")
        
        if avg_score >= 7:
            strengths.append("Good overall communication")
        elif avg_score < 5:
            weaknesses.append("Focus on providing more comprehensive answers")
        
        # Grade calculation
        grade = self._calculate_grade(avg_score)
        
        # Improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            avg_score, category_scores, weaknesses
        )
        
        # Placement readiness
        placement_ready = "Ready" if avg_score >= 7 else "Needs Work" if avg_score >= 5 else "Not Ready"
        
        return {
            "overall_score": round(avg_score * 10, 1),  # Convert to 0-100
            "grade": grade,
            "question_scores": question_scores,
            "category_scores": {k: v * 10 for k, v in category_scores.items()},
            "strengths": strengths if strengths else ["Participated in the interview"],
            "weaknesses": weaknesses if weaknesses else ["No major weaknesses identified"],
            "improvement_suggestions": suggestions,
            "placement_ready": placement_ready,
            "total_questions": len(questions),
            "questions_answered": len(responses)
        }
    
    def _calculate_grade(self, avg_score: float) -> str:
        """Calculate letter grade from average score."""
        if avg_score >= 9:
            return "A+"
        elif avg_score >= 8:
            return "A"
        elif avg_score >= 7:
            return "B+"
        elif avg_score >= 6:
            return "B"
        elif avg_score >= 5:
            return "C+"
        elif avg_score >= 4:
            return "C"
        elif avg_score >= 3:
            return "D"
        else:
            return "F"
    
    def _generate_improvement_suggestions(
        self,
        avg_score: float,
        category_scores: Dict[str, float],
        weaknesses: List[str]
    ) -> List[str]:
        """Generate personalized improvement suggestions."""
        suggestions = []
        
        if avg_score < 7:
            suggestions.append("Practice answering questions out loud to improve fluency")
        
        if category_scores.get("technical", 10) < 6:
            suggestions.append("Review core technical concepts and practice coding problems")
        
        if category_scores.get("hr", 10) < 6:
            suggestions.append("Prepare STAR method responses for behavioral questions")
        
        if category_scores.get("project", 10) < 6:
            suggestions.append("Be ready to discuss your projects in detail with concrete examples")
        
        if avg_score < 5:
            suggestions.append("Consider taking mock interviews to build confidence")
            suggestions.append("Focus on providing structured, detailed responses")
        
        if not suggestions:
            suggestions.append("Continue practicing to maintain your skills")
            suggestions.append("Stay updated with industry trends and new technologies")
        
        return suggestions[:5]  # Limit to 5 suggestions


# Global instance
evaluator = Evaluator()
