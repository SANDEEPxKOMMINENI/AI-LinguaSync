from supabase import create_client, Client
import os
from dotenv import load_dotenv
from src.models.translation import TranslationResponse

load_dotenv()

class SupabaseClient:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase environment variables")
            
        # Initialize Supabase client with older version syntax
        self.client: Client = create_client(supabase_url, supabase_key)
    
    async def store_translation(self, translation: TranslationResponse):
        """
        Store translation record in Supabase
        """
        try:
            data = {
                "original_text": translation.original_text,
                "translated_text": translation.translated_text,
                "speaker_id": translation.speaker_id,
            }
            
            return await self.client.table("translations").insert(data).execute()
        except Exception as e:
            print(f"Error storing translation: {e}")
            return None