from typing import Optional
from src.services.speech_to_text import WhisperSTTService
from src.services.translation import DeepSeekTranslator
from src.services.text_to_speech import VITSService
from src.services.speaker_recognition import SpeechBrainDiarization
from src.services.storage_service import StorageService
from src.database.supabase_client import SupabaseClient
from src.models.translation import TranslationResponse
import numpy as np
import base64

class TranslationService:
    def __init__(
        self,
        stt_service: WhisperSTTService,
        translator: DeepSeekTranslator,
        tts_service: VITSService,
        diarization_service: SpeechBrainDiarization,
        storage_service: StorageService,
        db_client: SupabaseClient
    ):
        self.stt_service = stt_service
        self.translator = translator
        self.tts_service = tts_service
        self.diarization_service = diarization_service
        self.storage_service = storage_service
        self.db_client = db_client
    
    async def process_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        source_lang: str,
        target_lang: str,
        user_id: Optional[str] = None
    ) -> TranslationResponse:
        """
        Process audio through the complete translation pipeline
        Returns a TranslationResponse object
        """
        try:
            # Process audio with speaker diarization
            speakers = self.diarization_service.process(audio_data, sample_rate)
            
            results = []
            for speaker_id, speaker_audio in speakers:
                # Convert speech to text
                text = self.stt_service.transcribe(speaker_audio, sample_rate)
                
                if not text.strip():
                    continue
                
                # Translate text
                translated_text = self.translator.translate(
                    text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                
                # Convert translated text to speech
                audio_output = self.tts_service.synthesize(
                    translated_text,
                    lang=target_lang
                )
                
                # Convert audio to base64
                audio_bytes = self.audio_to_bytes(audio_output)
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Create TranslationResponse object
                response = TranslationResponse(
                    original_text=text,
                    translated_text=translated_text,
                    speaker_id=speaker_id,
                    audio_data=audio_base64
                )
                
                # Store translation if user is authenticated
                if user_id:
                    await self.db_client.store_translation(response)
                
                results.append(response)
            
            # Return the first result or a default response
            if results:
                return results[0]
            else:
                return TranslationResponse(
                    original_text="",
                    translated_text="",
                    speaker_id="no_speech_detected",
                    audio_data=None
                )
                
        except Exception as e:
            print(f"Error in translation service: {e}")
            return TranslationResponse(
                original_text="",
                translated_text="",
                speaker_id="error",
                error=str(e)
            )
    
    def audio_to_bytes(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """Convert numpy array audio data to WAV bytes"""
        import soundfile as sf
        import io
        
        with io.BytesIO() as audio_buffer:
            sf.write(audio_buffer, audio_data, sample_rate, format='WAV')
            return audio_buffer.getvalue()