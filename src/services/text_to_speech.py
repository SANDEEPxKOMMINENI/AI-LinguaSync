import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import numpy as np

class VITSService:
    def __init__(self):
        self.model_name = "microsoft/speecht5_tts"
        self.vocoder_name = "microsoft/speecht5_hifigan"
        self.model = None
        self.processor = None
        self.vocoder = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            self.processor = SpeechT5Processor.from_pretrained(self.model_name)
            self.model = SpeechT5ForTextToSpeech.from_pretrained(self.model_name)
            self.vocoder = SpeechT5HifiGan.from_pretrained(self.vocoder_name)
            
            self.model.to(self.device)
            self.vocoder.to(self.device)
        except Exception as e:
            print(f"Error loading TTS model: {e}")
    
    def synthesize(self, text: str, lang: str = "en") -> np.ndarray:
        """
        Convert text to speech using SpeechT5
        Returns audio data as numpy array
        """
        try:
            if not text.strip() or self.model is None or self.processor is None or self.vocoder is None:
                return np.zeros(0, dtype=np.float32)
            
            # Prepare input
            inputs = self.processor(text=text, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate speech
            with torch.no_grad():
                speech = self.model.generate_speech(inputs["input_ids"], self.vocoder)
                if isinstance(speech, torch.Tensor):
                    speech = speech.cpu().numpy()
            
            # Convert to numpy and normalize
            if speech.size > 0:
                speech = speech / np.max(np.abs(speech))
            
            return speech.astype(np.float32)
            
        except Exception as e:
            print(f"TTS error: {e}")
            return np.zeros(0, dtype=np.float32)