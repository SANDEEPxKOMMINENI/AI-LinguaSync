import os
from supabase import Client
from typing import Optional
import uuid

class StorageService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.bucket_name = "translations-audio"
    
    async def upload_audio(self, audio_data: bytes, user_id: str) -> Optional[str]:
        """
        Upload audio file to Supabase Storage and return the URL
        """
        try:
            file_name = f"{user_id}/{uuid.uuid4()}.wav"
            
            # Upload file to Supabase Storage
            result = await self.supabase.storage \
                .from_(self.bucket_name) \
                .upload(file_name, audio_data)
            
            if result.get("Key"):
                # Get public URL
                url = self.supabase.storage \
                    .from_(self.bucket_name) \
                    .get_public_url(file_name)
                return url
            
            return None
        except Exception as e:
            print(f"Error uploading audio: {e}")
            return None