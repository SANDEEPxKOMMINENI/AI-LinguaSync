from pydantic import BaseModel
from typing import Optional
from typing import List

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    speaker_id: Optional[str] = None

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    speaker_id: Optional[str] = None
    audio_data: Optional[bytes] = None
    error: Optional[str] = None

    def dict(self, *args, **kwargs):
        # Convert to a JSON-serializable dictionary
        base_dict = super().dict(*args, **kwargs)
        # Convert bytes to base64 if present
        if base_dict.get("audio_data"):
            import base64
            base_dict["audio_data"] = base64.b64encode(base_dict["audio_data"]).decode()
        return base_dict

class Language(BaseModel):
    code: str
    name: str

class TranslationHistory(BaseModel):
    id: str
    user_id: str
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    created_at: str