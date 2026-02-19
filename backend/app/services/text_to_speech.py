"""
Text-to-Speech Service

Uses pyttsx3 as a lightweight, cross-platform TTS solution.
Falls back to simple audio generation if TTS is not available.
"""

import os
import logging
import asyncio
import hashlib
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-Speech service using pyttsx3."""
    
    def __init__(self):
        self.engine = None
        self._initialized = False
        self.cache_dir = None
    
    async def _ensure_initialized(self):
        """Lazy load TTS engine."""
        if self._initialized:
            return
        
        try:
            import pyttsx3
            from app.core.config import settings
            
            logger.info("🔊 Initializing TTS engine...")
            
            # Initialize pyttsx3 engine
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Set up cache directory
            self.cache_dir = Path(settings.MODELS_DIR) / "tts_cache"
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            logger.info("✅ TTS engine initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize TTS: {e}")
            self._initialized = True
    
    async def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file
        """
        await self._ensure_initialized()
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Generate cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # Generate output path if not provided
        if not output_path:
            from app.core.config import settings
            output_path = os.path.join(settings.RECORDINGS_DIR, f"tts_{cache_key}.wav")
        
        # Check cache first
        cache_path = self.cache_dir / f"{cache_key}.wav" if self.cache_dir else None
        if cache_path and cache_path.exists():
            logger.info(f"🎵 Using cached audio: {cache_key}")
            return str(cache_path)
        
        try:
            if self.engine:
                logger.info(f"🎙️ Synthesizing speech: {len(text)} characters")
                
                # Run synthesis in executor to avoid blocking
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._generate_audio(text, output_path)
                )
                
                # Cache the result
                if cache_path and self.cache_dir and os.path.exists(output_path):
                    import shutil
                    shutil.copy(output_path, cache_path)
                
                logger.info(f"✅ Speech generated: {output_path}")
                return output_path
            else:
                # Fallback: create a placeholder file
                logger.warning("TTS not available, creating placeholder")
                return await self._create_placeholder(text, output_path)
                
        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
            return await self._create_placeholder(text, output_path)
    
    def _generate_audio(self, text: str, output_path: str):
        """Generate audio file from text (blocking)."""
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            raise
    
    async def synthesize_to_bytes(self, text: str) -> bytes:
        """
        Convert text to speech and return audio bytes.
        
        Args:
            text: Text to convert
            
        Returns:
            Audio data as bytes
        """
        audio_path = await self.synthesize(text)
        
        if os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                return f.read()
        return b""
    
    async def _create_placeholder(self, text: str, output_path: str) -> str:
        """Create a placeholder audio file when TTS is not available."""
        import wave
        import struct
        
        # Create a simple silence
        sample_rate = 16000
        duration = min(len(text) / 20, 5)  # Approximate duration based on text length
        num_samples = int(sample_rate * duration)
        
        # Generate silence
        audio_data = [0] * num_samples
        
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack(f'{num_samples}h', *audio_data))
        
        return output_path
    
    def clear_cache(self):
        """Clear the TTS audio cache."""
        if self.cache_dir and self.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("🗑️ TTS cache cleared")


# Global instance
text_to_speech = TextToSpeech()
