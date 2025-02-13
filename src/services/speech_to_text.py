import whisper
import numpy as np
from typing import Optional

class WhisperSTTService:
    def __init__(self, model_name: str = "small"):  # Using small model for better accuracy
        try:
            self.model = whisper.load_model(model_name)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe audio data to text using Whisper
        """
        try:
            if self.model is None:
                return ""

            # Ensure audio is in the correct format for Whisper
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)  # Convert stereo to mono
            
            # Normalize audio data
            if audio_data.size > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Transcribe audio with more options for better accuracy
            result = self.model.transcribe(
                audio_data,
                fp16=False,  # Disable FP16 on CPU
                language="en",  # Default to English but can be changed
                task="transcribe",
                best_of=5  # Increase beam search for better results
            )
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""