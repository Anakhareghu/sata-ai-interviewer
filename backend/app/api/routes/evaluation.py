from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.schemas import VoiceAnalyticsResponse
from app.services.evaluator import evaluator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{session_id}/score")
async def get_performance_score(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get performance scores for an interview session."""
    from sqlalchemy import select
    from app.models import PerformanceScore, InterviewSession, InterviewQuestion
    
    # Check for existing score
    result = await db.execute(
        select(PerformanceScore).where(PerformanceScore.session_id == session_id)
    )
    score = result.scalar_one_or_none()
    
    if score:
        return {
            "id": score.id,
            "session_id": score.session_id,
            "scores": {
                "technical_accuracy": score.technical_accuracy,
                "communication_score": score.communication_score,
                "confidence_level": score.confidence_level,
                "problem_solving": score.problem_solving,
                "domain_knowledge": score.domain_knowledge,
                "overall_score": score.overall_score,
                "grade": score.grade,
            },
            "strengths": score.strengths or [],
            "weaknesses": score.weaknesses or [],
            "improvement_suggestions": score.improvement_suggestions or [],
            "placement_ready": score.placement_ready,
        }
    
    # Generate score if not exists
    session_result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Get questions and responses
    questions_result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
        .order_by(InterviewQuestion.question_number)
    )
    questions = questions_result.scalars().all()
    
    # Prepare data for evaluation
    questions_data = [{
        "question_text": q.question_text,
        "question_type": q.question_type,
        "expected_keywords": q.expected_keywords or []
    } for q in questions]
    
    responses_data = [{
        "question_idx": i,
        "response_text": q.student_response_text or ""
    } for i, q in enumerate(questions) if q.student_response_text]
    
    # Generate report
    report = await evaluator.generate_final_report(questions_data, responses_data)
    
    # Save to database
    from app.models import PerformanceScore as PerformanceScoreModel
    
    new_score = PerformanceScoreModel(
        session_id=session_id,
        student_id=session.student_id,
        technical_accuracy=report.get("category_scores", {}).get("technical", 70),
        communication_score=70,
        confidence_level=70,
        problem_solving=report.get("category_scores", {}).get("scenario", 70),
        domain_knowledge=report.get("category_scores", {}).get("project", 70),
        overall_score=report.get("overall_score", 70),
        grade=report.get("grade", "B"),
        strengths=report.get("strengths", []),
        weaknesses=report.get("weaknesses", []),
        improvement_suggestions=report.get("improvement_suggestions", []),
        placement_ready=report.get("placement_ready", "Needs Work")
    )
    
    db.add(new_score)
    await db.flush()
    
    logger.info(f"📊 Score generated for session: {session_id}")
    
    return {
        "id": new_score.id,
        "session_id": new_score.session_id,
        "scores": {
            "technical_accuracy": new_score.technical_accuracy,
            "communication_score": new_score.communication_score,
            "confidence_level": new_score.confidence_level,
            "problem_solving": new_score.problem_solving,
            "domain_knowledge": new_score.domain_knowledge,
            "overall_score": new_score.overall_score,
            "grade": new_score.grade,
        },
        "strengths": new_score.strengths or [],
        "weaknesses": new_score.weaknesses or [],
        "improvement_suggestions": new_score.improvement_suggestions or [],
        "placement_ready": new_score.placement_ready,
    }


@router.get("/{session_id}/voice-analytics")
async def get_voice_analytics(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get voice analytics for an interview session."""
    from sqlalchemy import select
    from app.models import VoiceAnalytics
    
    result = await db.execute(
        select(VoiceAnalytics).where(VoiceAnalytics.session_id == session_id)
    )
    analytics = result.scalar_one_or_none()
    
    if not analytics:
        # Return default values if no analytics available
        return {
            "average_speech_rate": 120.0,
            "filler_word_count": 5,
            "average_response_time": 15.0,
            "average_confidence": 70.0,
            "average_clarity": 75.0
        }
    
    return {
        "average_speech_rate": analytics.average_speech_rate,
        "filler_word_count": analytics.filler_word_count,
        "average_response_time": analytics.average_response_time,
        "average_confidence": analytics.average_confidence,
        "average_clarity": analytics.average_clarity,
    }


@router.get("/{session_id}/career-recommendations")
async def get_career_recommendations(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get career recommendations based on interview performance."""
    from sqlalchemy import select
    from app.models import InterviewSession, PerformanceScore, Resume
    
    # Get session
    session_result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Get resume data if available
    resume = None
    if session.resume_id:
        resume_result = await db.execute(
            select(Resume).where(Resume.id == session.resume_id)
        )
        resume = resume_result.scalar_one_or_none()
    
    # Get performance score
    score_result = await db.execute(
        select(PerformanceScore).where(PerformanceScore.session_id == session_id)
    )
    score = score_result.scalar_one_or_none()
    
    # Generate recommendations based on skills and score
    skills = resume.extracted_skills if resume else {}
    technical_skills = skills.get("technical", []) if isinstance(skills, dict) else []
    domain = resume.domain_specialization if resume else "General Technology"
    
    # Recommend roles based on skills
    role_mappings = {
        "AI/ML": ["Machine Learning Engineer", "Data Scientist", "AI Researcher"],
        "Web Development": ["Full Stack Developer", "Frontend Engineer", "Backend Developer"],
        "Data Science": ["Data Analyst", "Business Intelligence Analyst", "Data Engineer"],
        "Mobile Development": ["Mobile App Developer", "iOS Developer", "Android Developer"],
        "DevOps": ["DevOps Engineer", "Site Reliability Engineer", "Cloud Architect"],
        "General Technology": ["Software Engineer", "Technical Analyst", "IT Consultant"]
    }
    
    recommended_roles = []
    for role in role_mappings.get(domain, role_mappings["General Technology"]):
        recommended_roles.append({
            "role": role,
            "match_score": min(95, 70 + (score.overall_score / 10 if score else 0) * 0.3),
            "requirements": technical_skills[:3] if technical_skills else ["Programming", "Problem Solving"]
        })
    
    # Identify skill gaps
    skill_gaps = []
    if domain == "AI/ML" and "pytorch" not in [s.lower() for s in technical_skills]:
        skill_gaps.append({"skill": "PyTorch", "importance": "High"})
    if domain == "Web Development" and "react" not in [s.lower() for s in technical_skills]:
        skill_gaps.append({"skill": "React", "importance": "High"})
    
    # Suggest courses
    suggested_courses = [
        {"course": "System Design Interview Prep", "platform": "Coursera"},
        {"course": "Data Structures and Algorithms", "platform": "LeetCode"},
    ]
    
    if domain == "AI/ML":
        suggested_courses.append({"course": "Deep Learning Specialization", "platform": "Coursera"})
    
    return {
        "recommended_roles": recommended_roles,
        "skill_gaps": skill_gaps,
        "suggested_courses": suggested_courses,
        "internship_suggestions": [
            {"company": "Tech Startups", "role": recommended_roles[0]["role"] if recommended_roles else "Software Intern"}
        ]
    }


@router.get("/{session_id}/report")
async def get_full_report(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get complete interview report including all evaluations."""
    from sqlalchemy import select
    from app.models import InterviewSession, InterviewQuestion
    
    # Get session
    session_result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Get questions
    questions_result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
        .order_by(InterviewQuestion.question_number)
    )
    questions = questions_result.scalars().all()
    
    # Get performance score
    score_data = await get_performance_score(session_id, db)
    
    # Get career recommendations
    career = await get_career_recommendations(session_id, db)
    
    return {
        "session": {
            "id": str(session.id),
            "status": session.status,
            "interview_type": session.interview_type,
            "difficulty": session.difficulty,
            "duration_seconds": session.duration_seconds,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None
        },
        "questions": [{
            "number": q.question_number,
            "text": q.question_text,
            "type": q.question_type,
            "response": q.student_response_text,
            "score": q.score,
            "feedback": q.feedback
        } for q in questions],
        "performance": {
            "overall_score": score_data.get("scores", {}).get("overall_score", 70),
            "grade": score_data.get("scores", {}).get("grade", "B"),
            "placement_ready": score_data.get("placement_ready", "Needs Work")
        },
        "career_recommendations": career
    }
