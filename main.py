from fastapi import FastAPI, WebSocket, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict
import asyncio
import numpy as np
import os
import sys
import json
import soundfile as sf
import io

from src.services.translation import MyMemoryTranslator
from src.services.storage_service import StorageService
from src.services.auth_service import AuthService
from src.database.supabase_client import SupabaseClient
from src.models.translation import TranslationResponse

app = FastAPI(title="AI Translator")

# Get the frontend URL from environment or use a default for development
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    db_client = SupabaseClient()
    auth_service = AuthService(db_client.client)
    storage_service = StorageService(db_client.client)
    translator = MyMemoryTranslator()
except Exception as e:
    print(f"Error initializing services: {e}")
    sys.exit(1)

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        await websocket.accept()
        active_connections[client_id] = websocket
        print(f"WebSocket client connected: {client_id}")
        
        while True:
            try:
                # Receive audio data from the client
                audio_data = await websocket.receive_bytes()
                print(f"Received audio data from client: {client_id}")
                
                # Convert audio bytes to numpy array
                with io.BytesIO(audio_data) as audio_buffer:
                    audio_array, sample_rate = sf.read(audio_buffer)
                
                # Convert to mono if stereo
                if len(audio_array.shape) > 1:
                    audio_array = audio_array.mean(axis=1)
                
                # For now, we'll just return an empty response since we're not doing STT
                response = TranslationResponse(
                    original_text="Speech-to-text not implemented",
                    translated_text="Please type your text instead",
                    speaker_id="system",
                    error="Speech-to-text is not available in the free tier"
                )
                
                await websocket.send_json(response.dict())
                print(f"Sent response to client: {client_id}")
                
            except Exception as e:
                print(f"Error processing audio: {e}")
                error_response = TranslationResponse(
                    original_text="",
                    translated_text="",
                    speaker_id="error",
                    error=str(e)
                )
                await websocket.send_json(error_response.dict())
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]
            print(f"WebSocket client disconnected: {client_id}")

@app.get("/translate")
async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str
):
    """
    Translate text using MyMemory Translation API
    Authentication disabled for development
    """
    try:
        if not text.strip():
            return {"error": "Please enter text to translate"}
            
        translated_text = translator.translate(text, source_lang, target_lang)
        
        if translated_text == text and source_lang != target_lang:
            return {"error": "Translation service is rate limited. Please try again in a few seconds."}
        
        return {
            "original_text": text,
            "translated_text": translated_text
        }
    except Exception as e:
        print(f"Translation error: {e}")
        return {"error": str(e)}

@app.get("/translations")
async def get_translations(user_id: str = Depends(auth_service.get_current_user)):
    """
    Get user's translation history
    """
    try:
        result = await db_client.client \
            .from_("translations") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        return result.data
    except Exception as e:
        print(f"Error fetching translations: {e}")
        return []

@app.get("/")
async def root():
    return {"message": "AI Translator API is running"}

if __name__ == "__main__":
    # Configure uvicorn for Windows compatibility
    if sys.platform == 'win32':
        # Use these settings for Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            loop="asyncio",
            reload_excludes=["node_modules/*"]  # Exclude node_modules from reload
        )
    else:
        # Default settings for other platforms
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_excludes=["node_modules/*"]  # Exclude node_modules from reload
        )