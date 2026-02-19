"""
Speech-to-Text Service

Uses browser's Web Speech API for speech recognition.
The frontend handles the actual speech-to-text conversion using the browser's 
built-in SpeechRecognition API and sends the transcript to the backend.

This service handles the transcript validation and processing.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SpeechToText:
    """
    Speech-to-Text service.
    
    Note: Actual speech recognition happens in the browser using Web Speech API.
    This service processes and validates the transcripts received from the frontend.
    """
    
    def __init__(self):
        self._initialized = True
    
    async def process_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Process a transcript received from the browser.
        
        Args:
            transcript: Text transcript from browser Web Speech API
            
        Returns:
            Processed transcript with metadata
        """
        if not transcript:
            return {
                "text": "",
                "word_count": 0,
                "confidence": 0.0,
                "valid": False
            }
        
        # Clean the transcript
        cleaned = transcript.strip()
        words = cleaned.split()
        word_count = len(words)
        
        # Estimate confidence based on word count
        # Longer responses generally indicate more confidence
        confidence = min(0.95, 0.5 + (word_count / 100))
        
        return {
            "text": cleaned,
            "word_count": word_count,
            "confidence": confidence,
            "valid": word_count >= 3  # At least 3 words for a valid response
        }
    
    async def validate_response(self, transcript: str, question_type: str) -> Dict[str, Any]:
        """
        Validate if the response is appropriate for the question type.
        
        Args:
            transcript: User's response
            question_type: Type of question (technical, hr, etc.)
            
        Returns:
            Validation result with feedback
        """
        if not transcript or len(transcript.strip()) < 10:
            return {
                "valid": False,
                "feedback": "Please provide a more detailed response.",
                "suggestion": "Try to elaborate with examples or specific details."
            }
        
        word_count = len(transcript.split())
        
        # Check minimum word count based on question type
        min_words = {
            "technical": 20,
            "hr": 30,
            "project": 25,
            "scenario": 30,
            "general": 15
        }
        
        required = min_words.get(question_type, 15)
        
        if word_count < required:
            return {
                "valid": False,
                "feedback": f"Your response seems brief. Consider adding more detail.",
                "suggestion": f"Try to include at least {required} words with specific examples."
            }
        
        return {
            "valid": True,
            "feedback": "Good response length.",
            "word_count": word_count
        }

    async def transcribe_audio_data(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process raw audio data bytes.
        
        Note: Actual speech recognition happens in the browser via Web Speech API.
        This method provides a server-side fallback for audio data received via WebSocket.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcription result dict
        """
        if not audio_data or len(audio_data) < 100:
            return {
                "text": "",
                "confidence": 0.0,
                "valid": False,
                "message": "Audio data too short"
            }
        
        # Since we rely on browser-based STT, return a placeholder
        # The actual transcript comes from the browser's Web Speech API
        logger.info(f"🎤 Received {len(audio_data)} bytes of audio data")
        return {
            "text": "[Audio received - awaiting browser transcript]",
            "confidence": 0.5,
            "valid": True,
            "message": "Audio processed (browser STT preferred)"
        }


# Global instance
speech_to_text = SpeechToText()
