from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging
from datetime import datetime

from app.core.database import get_db
from app.schemas import InterviewCreate, InterviewSessionResponse, QuestionResponse, AnswerSubmit
from app.services.question_generator import QuestionGenerator
from app.models import InterviewSession, InterviewQuestion, InterviewStatus

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize question generator
question_generator = QuestionGenerator()


@router.post("/create", response_model=InterviewSessionResponse)
async def create_interview(
    data: InterviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new interview session.
    
    Generates personalized questions based on:
    - Resume data
    - Interview configuration
    """
    from sqlalchemy import select
    from app.models import Resume
    
    # Get resume data if provided
    resume_data = {}
    resume_id_str = str(data.resume_id) if data.resume_id else None
    if resume_id_str:
        result = await db.execute(select(Resume).where(Resume.id == resume_id_str))
        resume = result.scalar_one_or_none()
        if resume:
            resume_data = {
                "extracted_skills": resume.extracted_skills or {},
                "projects": resume.projects or [],
                "work_experience": resume.work_experience or [],
                "domain": resume.domain_specialization
            }
    
    # Create interview session
    session_id = str(uuid.uuid4())
    student_id_str = str(data.student_id)
    
    session = InterviewSession(
        id=session_id,
        student_id=student_id_str,
        resume_id=resume_id_str,
        interview_type=data.interview_type,
        difficulty=data.difficulty,
        status=InterviewStatus.PENDING.value
    )
    
    db.add(session)
    await db.flush()
    
    # Generate questions
    questions = await question_generator.generate_questions(
        resume_data=resume_data,
        difficulty=data.difficulty,
        num_questions=10
    )
    
    # Save questions to database
    for q in questions:
        question = InterviewQuestion(
            session_id=session_id,
            question_number=q["question_number"],
            question_text=q["question_text"],
            question_type=q["question_type"],
            difficulty=q.get("difficulty", data.difficulty),
            expected_keywords=q.get("expected_keywords", []),
            expected_answer_guide=q.get("expected_answer_guide", "")
        )
        db.add(question)
    
    session.total_questions = len(questions)
    await db.flush()
    
    logger.info(f"✅ Interview session created: {session.id} with {len(questions)} questions")
    
    return session


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get interview session by ID."""
    from sqlalchemy import select
    
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    return session


@router.post("/{session_id}/start")
async def start_interview(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start an interview session."""
    from sqlalchemy import select
    
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != InterviewStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Interview already started or completed")
    
    session.status = InterviewStatus.IN_PROGRESS.value
    session.started_at = datetime.utcnow()
    
    logger.info(f"🎤 Interview started: {session_id}")
    
    return {"message": "Interview started", "session_id": session_id}


@router.get("/{session_id}/questions")
async def get_questions(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all questions for an interview session."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
        .order_by(InterviewQuestion.question_number)
    )
    questions = result.scalars().all()
    
    # Serialize questions manually for JSON compatibility
    questions_list = []
    for q in questions:
        questions_list.append({
            "id": q.id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
        })
    
    return {"questions": questions_list, "count": len(questions_list)}


@router.get("/{session_id}/current-question")
async def get_current_question(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the current unanswered question."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
        .where(InterviewQuestion.student_response_text.is_(None))
        .order_by(InterviewQuestion.question_number)
    )
    question = result.scalars().first()
    
    if not question:
        return {"message": "All questions answered", "completed": True}
    
    # Mark as asked
    question.asked_at = datetime.utcnow()
    
    return {
        "id": question.id,
        "question_number": question.question_number,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "difficulty": question.difficulty,
    }


@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    answer: AnswerSubmit,
    db: AsyncSession = Depends(get_db)
):
    """Submit an answer to a question."""
    from sqlalchemy import select
    
    question_id_str = str(answer.question_id)
    result = await db.execute(
        select(InterviewQuestion).where(InterviewQuestion.id == question_id_str)
    )
    question = result.scalars().first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question.session_id != session_id:
        raise HTTPException(status_code=400, detail="Question does not belong to this session")
    
    # Save answer
    question.student_response_text = answer.response_text
    question.response_audio_path = answer.audio_path
    question.answered_at = datetime.utcnow()
    
    # Calculate response time
    if question.asked_at:
        question.response_time_seconds = int((question.answered_at - question.asked_at).total_seconds())
    
    # Update session progress
    session_result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = session_result.scalar_one()
    session.questions_answered += 1
    
    # Check if all questions answered
    if session.questions_answered >= session.total_questions:
        return {
            "message": "Answer submitted",
            "completed": True,
            "redirect": f"/evaluation/{session_id}"
        }
    
    return {"message": "Answer submitted", "completed": False}


@router.post("/{session_id}/end")
async def end_interview(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """End an interview session."""
    from sqlalchemy import select
    
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session.status = InterviewStatus.COMPLETED.value
    session.ended_at = datetime.utcnow()
    
    if session.started_at:
        session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
    
    logger.info(f"✅ Interview completed: {session_id}")
    
    return {
        "message": "Interview completed",
        "session_id": session_id,
        "duration_seconds": session.duration_seconds
    }


@router.get("/student/{student_id}/history")
async def get_student_interviews(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get interview history for a student."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.student_id == student_id)
        .order_by(InterviewSession.created_at.desc())
    )
    sessions = result.scalars().all()
    
    # Serialize for JSON
    interviews_list = []
    for s in sessions:
        interviews_list.append({
            "id": s.id,
            "student_id": s.student_id,
            "status": s.status,
            "interview_type": s.interview_type,
            "difficulty": s.difficulty,
            "total_questions": s.total_questions,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    
    return {"interviews": interviews_list, "count": len(interviews_list)}
