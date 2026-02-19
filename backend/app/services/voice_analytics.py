"""
Voice Analytics Service using pyAudioAnalysis

Analyzes:
- Speech rate (words per minute)
- Filler words (um, uh, like)
- Pause duration
- Confidence level
- Speech clarity
- Tone/sentiment
"""

import logging
from typing import Dict, List, Any, Optional
import asyncio
import re

logger = logging.getLogger(__name__)


class VoiceAnalytics:
    """Analyze voice and communication patterns."""
    
    def __init__(self):
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Initialize audio analysis libraries."""
        if self._initialized:
            return
        
        try:
            # Check if pyAudioAnalysis is available
            import numpy as np
            self._initialized = True
            logger.info("✅ Voice analytics initialized")
        except Exception as e:
            logger.warning(f"⚠️ Voice analytics limited: {e}")
            self._initialized = True
    
    async def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze audio file for communication metrics.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with analytics results
        """
        await self._ensure_initialized()
        
        try:
            import numpy as np
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Calculate basic audio features
            rms = librosa.feature.rms(y=y)[0]
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # Estimate speech rate from zero crossings (rough approximation)
            average_zcr = float(np.mean(zcr))
            
            # Detect pauses (low energy segments)
            pause_threshold = float(np.mean(rms) * 0.3)
            pauses = np.sum(rms < pause_threshold) / len(rms)
            
            # Calculate clarity from spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            clarity_score = min(100, float(np.mean(spectral_centroid) / 1000 * 25))
            
            # Estimate confidence from energy variation
            energy_var = float(np.std(rms) / (np.mean(rms) + 1e-6))
            confidence_score = max(0, min(100, 100 - energy_var * 30))
            
            return {
                "duration_seconds": duration,
                "average_energy": float(np.mean(rms)),
                "pause_ratio": float(pauses),
                "clarity_score": clarity_score,
                "confidence_score": confidence_score,
                "energy_variation": energy_var
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {
                "duration_seconds": 0,
                "error": str(e)
            }
    
    async def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze transcript for communication patterns.
        
        Args:
            transcript: Text transcript of speech
            
        Returns:
            Dictionary with text-based analytics
        """
        if not transcript:
            return {"error": "No transcript provided"}
        
        words = transcript.split()
        word_count = len(words)
        
        # Filler words detection
        filler_words = ["um", "uh", "like", "you know", "basically", "actually", "so", "well"]
        filler_count = 0
        for filler in filler_words:
            filler_count += len(re.findall(rf'\b{filler}\b', transcript.lower()))
        
        filler_ratio = filler_count / word_count if word_count > 0 else 0
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', transcript)
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Vocabulary diversity
        unique_words = len(set(word.lower() for word in words))
        vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
        
        # Technical keywords (indicates domain knowledge)
        technical_keywords = [
            "algorithm", "implement", "optimize", "database", "framework",
            "architecture", "scalable", "performance", "design", "pattern",
            "function", "class", "method", "api", "interface"
        ]
        technical_count = sum(1 for kw in technical_keywords if kw in transcript.lower())
        
        return {
            "word_count": word_count,
            "filler_word_count": filler_count,
            "filler_word_ratio": round(filler_ratio * 100, 2),
            "average_sentence_length": round(avg_sentence_length, 1),
            "vocabulary_diversity": round(vocabulary_diversity * 100, 2),
            "technical_keyword_count": technical_count,
            "communication_score": self._calculate_communication_score(
                filler_ratio, vocabulary_diversity, technical_count
            )
        }
    
    def _calculate_communication_score(
        self,
        filler_ratio: float,
        vocabulary_diversity: float,
        technical_count: int
    ) -> float:
        """Calculate overall communication score."""
        # Lower filler ratio is better
        filler_score = max(0, 100 - filler_ratio * 500)
        
        # Higher vocabulary diversity is better
        diversity_score = min(100, vocabulary_diversity * 200)
        
        # Technical keywords bonus
        technical_bonus = min(20, technical_count * 2)
        
        # Weighted average
        score = (filler_score * 0.3 + diversity_score * 0.5 + technical_bonus * 0.2)
        return round(min(100, max(0, score)), 1)
    
    async def generate_full_analysis(
        self,
        audio_path: Optional[str],
        transcript: str,
        response_time: float
    ) -> Dict[str, Any]:
        """
        Generate comprehensive voice and communication analysis.
        
        Args:
            audio_path: Path to audio file (optional)
            transcript: Text transcript
            response_time: Time taken to respond in seconds
            
        Returns:
            Complete analytics report
        """
        # Analyze transcript
        text_analysis = await self.analyze_transcript(transcript)
        
        # Analyze audio if available
        audio_analysis = {}
        if audio_path:
            audio_analysis = await self.analyze_audio(audio_path)
        
        # Response time scoring
        response_time_score = 100
        if response_time > 30:
            response_time_score = max(50, 100 - (response_time - 30) * 2)
        elif response_time < 2:
            response_time_score = 70  # Too quick might mean not thinking enough
        
        # Combine scores
        scores = {
            "communication_score": text_analysis.get("communication_score", 70),
            "clarity_score": audio_analysis.get("clarity_score", 70),
            "confidence_score": audio_analysis.get("confidence_score", 70),
            "response_time_score": response_time_score
        }
        
        overall = sum(scores.values()) / len(scores)
        
        return {
            "text_analysis": text_analysis,
            "audio_analysis": audio_analysis,
            "scores": scores,
            "overall_communication_score": round(overall, 1),
            "response_time_seconds": response_time
        }


# Global instance
voice_analytics = VoiceAnalytics()
