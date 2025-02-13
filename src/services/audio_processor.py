import numpy as np
import soundfile as sf
import io
import base64
import wave

class AudioProcessor:
    @staticmethod
    def bytes_to_audio(audio_bytes: bytes) -> tuple[np.ndarray, int]:
        """Convert audio bytes to numpy array and sample rate."""
        try:
            # Create an in-memory buffer
            with io.BytesIO(audio_bytes) as audio_buffer:
                # Read the WAV file directly from the buffer
                with wave.open(audio_buffer, 'rb') as wav_file:
                    # Get audio parameters
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    sample_rate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()
                    
                    # Read raw audio data
                    raw_data = wav_file.readframes(n_frames)
                    
                    # Convert to numpy array
                    if sample_width == 2:  # 16-bit audio
                        dtype = np.int16
                    else:  # Assume 32-bit float
                        dtype = np.float32
                    
                    audio_data = np.frombuffer(raw_data, dtype=dtype)
                    
                    # Reshape if stereo
                    if channels == 2:
                        audio_data = audio_data.reshape(-1, 2).mean(axis=1)
                    
                    # Convert to float32 and normalize
                    audio_data = audio_data.astype(np.float32)
                    if audio_data.size > 0:
                        audio_data = audio_data / np.max(np.abs(audio_data))
                    
                    return audio_data, sample_rate
                    
        except Exception as e:
            print(f"Error processing audio: {e}")
            # Return empty audio data with default sample rate
            return np.array([], dtype=np.float32), 16000

    @staticmethod
    def audio_to_bytes(audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """Convert numpy array audio data to bytes."""
        try:
            # Ensure audio data is float32
            audio_data = audio_data.astype(np.float32)
            
            # Create a temporary buffer
            with io.BytesIO() as audio_buffer:
                # Write WAV data to the buffer
                sf.write(audio_buffer, audio_data, sample_rate, format='WAV')
                return audio_buffer.getvalue()
        except Exception as e:
            print(f"Error converting audio to bytes: {e}")
            return bytes()