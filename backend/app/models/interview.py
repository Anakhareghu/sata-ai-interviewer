import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewType(str, enum.Enum):
    TECHNICAL = "technical"
    HR = "hr"
    MIXED = "mixed"
    PROJECT_VIVA = "project_viva"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    ADVANCED = "advanced"


class QuestionType(str, enum.Enum):
    TECHNICAL = "technical"
    HR = "hr"
    SCENARIO = "scenario"
    PROJECT = "project"
    PROBLEM_SOLVING = "problem_solving"


class InterviewSession(Base):
    """Interview session model tracking each interview."""
    __tablename__ = "interview_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), nullable=False, index=True)
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=True)
    
    # Interview configuration
    status = Column(String(20), default=InterviewStatus.PENDING.value)
    interview_type = Column(String(20), default=InterviewType.MIXED.value)
    difficulty = Column(String(20), default=DifficultyLevel.MEDIUM.value)
    
    # Interview metadata
    total_questions = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Recording
    recording_path = Column(String(500), nullable=True)
    full_transcript = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InterviewSession {self.id} - {self.status}>"


class InterviewQuestion(Base):
    """Individual question within an interview session."""
    __tablename__ = "interview_questions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    
    # Question details
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(30), default=QuestionType.TECHNICAL.value)
    difficulty = Column(String(20), default=DifficultyLevel.MEDIUM.value)
    
    # Expected answer hints (for evaluation)
    expected_keywords = Column(JSON, default=list)  # Key concepts to look for
    expected_answer_guide = Column(Text, nullable=True)
    
    # Student response
    student_response_text = Column(Text, nullable=True)
    response_audio_path = Column(String(500), nullable=True)
    
    # Timing
    asked_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)
    
    # Scoring
    score = Column(Float, nullable=True)  # 0-10
    feedback = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    
    def __repr__(self):
        return f"<InterviewQuestion {self.id} - Q{self.question_number}>"
