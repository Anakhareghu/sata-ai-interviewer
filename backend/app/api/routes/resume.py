from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import os
import logging

from app.core.database import get_db
from app.core.config import settings
from app.schemas import ResumeUploadResponse, ResumeData, ResumeAnalysis
from app.services.resume_parser import ResumeParser

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize resume parser
resume_parser = ResumeParser()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    student_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse a resume (PDF or DOCX).
    
    Extracts:
    - Skills (technical & soft)
    - Projects
    - Work experience
    - Internships
    - Certifications
    - Education
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename — use str since model columns are String(36)
    resume_id = str(uuid.uuid4())
    safe_filename = f"{resume_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)
    
    logger.info(f"📄 Resume uploaded: {file.filename} -> {safe_filename}")
    
    try:
        # Parse resume
        parsed_data = await resume_parser.parse_resume(file_path)
        
        # Create database record — keys match what _analyze_text returns
        from app.models import Resume
        resume = Resume(
            id=resume_id,
            student_id=student_id if student_id else str(uuid.uuid4()),
            filename=file.filename,
            file_path=file_path,
            file_type=file_ext.replace(".", ""),
            raw_text=parsed_data.get("raw_text", ""),
            extracted_skills=parsed_data.get("extracted_skills", {}),
            projects=parsed_data.get("projects", []),
            work_experience=parsed_data.get("work_experience", []),
            internships=parsed_data.get("internships", []),
            certifications=parsed_data.get("certifications", []),
            education=parsed_data.get("education", []),
            contact_info=parsed_data.get("contact_info", {}),
            domain_specialization=parsed_data.get("domain_specialization", None),
            experience_level=parsed_data.get("experience_level", None)
        )
        
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        
        logger.info(f"✅ Resume parsed and saved: {resume_id}")
        
        return ResumeUploadResponse(
            id=resume_id,
            filename=file.filename,
            message="Resume uploaded and parsed successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error parsing resume: {e}")
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")


@router.get("/{resume_id}", response_model=ResumeData)
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get parsed resume data by ID."""
    from sqlalchemy import select
    from app.models import Resume
    
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysis)
async def get_resume_analysis(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get skill analysis and recommendations for a resume."""
    from sqlalchemy import select
    from app.models import Resume
    
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Analyze skills and generate recommendations
    analysis = await resume_parser.analyze_skills(resume)
    
    return ResumeAnalysis(
        resume_id=resume_id,
        skill_summary=analysis.get("summary", {}),
        skill_gaps=analysis.get("gaps", []),
        recommendations=analysis.get("recommendations", []),
        domain_match=analysis.get("domain_match", {})
    )


@router.get("/student/{student_id}")
async def get_student_resumes(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all resumes for a student."""
    from sqlalchemy import select
    from app.models import Resume
    
    result = await db.execute(
        select(Resume).where(Resume.student_id == student_id).order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()
    
    return {"resumes": resumes, "count": len(resumes)}


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a resume."""
    from sqlalchemy import select, delete
    from app.models import Resume
    
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete record
    await db.execute(delete(Resume).where(Resume.id == resume_id))
    await db.commit()
    
    return {"message": "Resume deleted successfully"}
