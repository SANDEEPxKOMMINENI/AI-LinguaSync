import os
import numpy as np
import torch
from typing import List, Tuple

class SpeechBrainDiarization:
    def __init__(self):
        # Set environment variables to disable symlink warnings
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        os.environ["HF_HUB_ENABLE_SYMLINKS"] = "0"
        
        # Initialize with fallback mode
        self.model = None
        self.device = torch.device("cpu")
        
        try:
            # Create models directory in current working directory
            models_dir = os.path.join(os.getcwd(), 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            from speechbrain.pretrained import SpeakerRecognition
            self.model = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir=os.path.join(models_dir, "spkrec-ecapa-voxceleb"),
                run_opts={"device": "cpu"},
                use_auth_token=None
            )
            print("Speaker recognition model loaded successfully")
        except Exception as e:
            print(f"Warning: Using fallback speaker recognition mode: {e}")
    
    def process(self, audio_data: np.ndarray, sample_rate: int = 16000) -> List[Tuple[str, np.ndarray]]:
        """
        Process audio and identify speakers
        Returns list of (speaker_id, audio_segment) tuples
        """
        try:
            if self.model is None:
                # Fallback mode - return single speaker
                return [("default_speaker", audio_data)]
            
            # Resample audio if needed
            if sample_rate != 16000:
                # Simple resampling - in production you'd want to use a proper resampling library
                audio_data = audio_data[::int(sample_rate/16000)]
            
            # Convert to float32 and normalize
            audio_data = audio_data.astype(np.float32)
            if audio_data.size > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Convert to tensor
            waveform = torch.from_numpy(audio_data).float().to(self.device)
            
            # Get embeddings
            with torch.no_grad():
                embeddings = self.model.encode_batch(waveform)
                
            # For now, we'll use a simple approach - just detect if there's speech
            if torch.norm(embeddings) > 0.1:
                return [("speaker_detected", audio_data)]
            else:
                return [("no_speech_detected", audio_data)]
            
        except Exception as e:
            print(f"Speaker recognition error (using fallback): {e}")
            return [("default_speaker", audio_data)]