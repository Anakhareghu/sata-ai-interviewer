"""
WebSocket endpoint for real-time voice interview.

Flow:
1. Client connects to WebSocket
2. AI asks question via TTS
3. Client sends audio chunks
4. Server transcribes with Whisper
5. AI evaluates and asks follow-up
6. Repeat until interview complete
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
import asyncio
import uuid
import base64
from datetime import datetime
from typing import Optional

from app.services.speech_to_text import speech_to_text
from app.services.text_to_speech import text_to_speech
from app.services.question_generator import QuestionGenerator
from app.services.evaluator import Evaluator

router = APIRouter()
logger = logging.getLogger(__name__)

# Active interview sessions
active_sessions = {}


class InterviewManager:
    """Manages a single voice interview session."""
    
    def __init__(self, session_id: str, websocket: WebSocket):
        self.session_id = session_id
        self.websocket = websocket
        self.current_question_idx = 0
        self.questions = []
        self.responses = []
        self.audio_buffer = []
        self.is_recording = False
        self.question_generator = QuestionGenerator()
        self.evaluator = Evaluator()
    
    async def send_message(self, message_type: str, data: dict):
        """Send a message to the client."""
        await self.websocket.send_json({
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def start_interview(self, resume_data: dict, interview_type: str = "mixed"):
        """Initialize and start the interview."""
        logger.info(f"🎤 Starting interview: {self.session_id}")
        
        # Generate questions based on interview type
        self.questions = await self.question_generator.generate_questions(
            resume_data=resume_data,
            interview_type=interview_type,
            num_questions=10
        )
        
        # Send welcome message
        await self.send_message("status", {
            "message": "Interview starting...",
            "total_questions": len(self.questions)
        })
        
        # Ask first question
        await self.ask_current_question()
    
    async def ask_current_question(self):
        """Ask the current question."""
        if self.current_question_idx >= len(self.questions):
            await self.end_interview()
            return
        
        question = self.questions[self.current_question_idx]
        question_text = question["question_text"]
        
        logger.info(f"❓ Asking question {self.current_question_idx + 1}: {question_text[:50]}...")
        
        # Send question text
        await self.send_message("question", {
            "number": self.current_question_idx + 1,
            "total": len(self.questions),
            "text": question_text,
            "type": question.get("question_type", "general")
        })
        
        # Generate TTS audio
        try:
            audio_path = await text_to_speech.synthesize(question_text)
            
            # Read and send audio as base64
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            await self.send_message("audio", {
                "audio_data": audio_data,
                "format": "wav"
            })
        except Exception as e:
            logger.error(f"TTS error: {e}")
            # Continue without audio
        
        # Reset audio buffer for recording response
        self.audio_buffer = []
        self.is_recording = True
        
        await self.send_message("status", {
            "message": "Recording your response...",
            "recording": True
        })
    
    async def receive_audio_chunk(self, chunk_data: bytes):
        """Receive an audio chunk from the client."""
        if self.is_recording:
            self.audio_buffer.append(chunk_data)
    
    async def stop_recording(self):
        """Stop recording and process the response."""
        self.is_recording = False
        
        if not self.audio_buffer:
            await self.send_message("error", {"message": "No audio received"})
            return
        
        await self.send_message("status", {
            "message": "Processing your response...",
            "recording": False
        })
        
        # Transcribe audio
        try:
            combined_audio = b"".join(self.audio_buffer)
            transcription = await speech_to_text.transcribe_audio_data(combined_audio)
            
            response_text = transcription.get("text", "")
            
            await self.send_message("transcription", {
                "text": response_text,
                "confidence": transcription.get("confidence", 0)
            })
            
            # Store response
            self.responses.append({
                "question_idx": self.current_question_idx,
                "response_text": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Evaluate and move to next question
            await self.evaluate_and_continue(response_text)
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            await self.send_message("error", {"message": "Error processing audio"})
    
    async def evaluate_and_continue(self, response_text: str):
        """Evaluate response and continue to next question."""
        current_question = self.questions[self.current_question_idx]
        
        # Quick evaluation
        score = await self.evaluator.evaluate_answer(
            question=current_question["question_text"],
            answer=response_text,
            expected_keywords=current_question.get("expected_keywords", [])
        )
        
        await self.send_message("feedback", {
            "score": score.get("score", 0),
            "feedback": score.get("brief_feedback", "")
        })
        
        # Move to next question
        self.current_question_idx += 1
        
        # Small delay before next question
        await asyncio.sleep(1)
        
        await self.ask_current_question()
    
    async def end_interview(self):
        """End the interview and generate final report."""
        logger.info(f"✅ Interview completed: {self.session_id}")
        
        await self.send_message("status", {
            "message": "Interview completed! Generating your report..."
        })
        
        # Generate final evaluation
        final_report = await self.evaluator.generate_final_report(
            questions=self.questions,
            responses=self.responses
        )
        
        await self.send_message("complete", {
            "report": final_report,
            "total_questions": len(self.questions),
            "questions_answered": len(self.responses)
        })
        
        # Clean up
        if self.session_id in active_sessions:
            del active_sessions[self.session_id]


@router.websocket("/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for live voice interview."""
    await websocket.accept()
    
    logger.info(f"🔗 WebSocket connected: {session_id}")
    
    # Create interview manager
    manager = InterviewManager(session_id, websocket)
    active_sessions[session_id] = manager
    
    try:
        while True:
            # Receive message
            message = await websocket.receive()
            
            if "text" in message:
                data = json.loads(message["text"])
                message_type = data.get("type")
                
                if message_type == "start":
                    # Start interview with resume data
                    resume_data = data.get("resume_data", {})
                    interview_type = data.get("interview_type", "mixed")
                    await manager.start_interview(resume_data, interview_type)
                    
                elif message_type == "stop_recording":
                    await manager.stop_recording()
                    
                elif message_type == "skip_question":
                    manager.current_question_idx += 1
                    await manager.ask_current_question()
                    
                elif message_type == "end_interview":
                    await manager.end_interview()
                    break
                    
            elif "bytes" in message:
                # Receive audio chunk
                audio_chunk = message["bytes"]
                await manager.receive_audio_chunk(audio_chunk)
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if session_id in active_sessions:
            del active_sessions[session_id]
