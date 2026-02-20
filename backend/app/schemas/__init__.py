from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Resume Schemas
class ResumeUploadResponse(BaseModel):
    id: str
    filename: str
    message: str


class ExtractedSkills(BaseModel):
    technical: List[str] = []
    soft: List[str] = []


class ProjectInfo(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = []


class WorkExperience(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None


class ResumeData(BaseModel):
    id: str
    student_id: str
    filename: str
    extracted_skills: Any = {}
    projects: Any = []
    work_experience: Any = []
    internships: Any = []
    certifications: Any = []
    education: Any = []
    domain_specialization: Optional[str] = None
    experience_level: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ResumeAnalysis(BaseModel):
    resume_id: str
    skill_summary: Dict[str, Any] = {}
    skill_gaps: List[str] = []
    recommendations: List[str] = []
    domain_match: Dict[str, float] = {}


# Interview Schemas
class InterviewCreate(BaseModel):
    student_id: str
    resume_id: Optional[str] = None
    interview_type: str = "mixed"


class InterviewSessionResponse(BaseModel):
    id: str
    student_id: str
    status: str
    interview_type: str
    difficulty: str = "mixed"
    total_questions: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: str
    question_number: int
    question_text: str
    question_type: str
    difficulty: str
    
    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    question_id: str
    response_text: str
    audio_path: Optional[str] = None


# Evaluation Schemas
class ScoreBreakdown(BaseModel):
    technical_accuracy: float = 0.0
    communication_score: float = 0.0
    confidence_level: float = 0.0
    problem_solving: float = 0.0
    domain_knowledge: float = 0.0
    overall_score: float = 0.0
    grade: Optional[str] = None


class PerformanceScoreResponse(BaseModel):
    id: str
    session_id: str
    scores: ScoreBreakdown
    strengths: List[str] = []
    weaknesses: List[str] = []
    improvement_suggestions: List[str] = []
    placement_ready: Optional[str] = None
    
    class Config:
        from_attributes = True


class VoiceAnalyticsResponse(BaseModel):
    average_speech_rate: Optional[float] = None
    filler_word_count: Optional[float] = None
    average_response_time: Optional[float] = None
    average_confidence: Optional[float] = None
    average_clarity: Optional[float] = None
    
    class Config:
        from_attributes = True


class CareerRecommendationResponse(BaseModel):
    recommended_roles: List[Dict[str, Any]] = []
    skill_gaps: List[Dict[str, Any]] = []
    suggested_courses: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


# WebSocket Schemas
class AudioChunk(BaseModel):
    data: bytes
    timestamp: float


class TranscriptionResult(BaseModel):
    text: str
    confidence: float
    is_final: bool
