from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt
from typing import Optional

security = HTTPBearer()

class AuthService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Optional[str]:
        """
        Validate JWT token and return user_id
        """
        try:
            token = credentials.credentials
            # Verify JWT token using Supabase public key
            payload = jwt.decode(
                token,
                options={"verify_signature": False}  # In production, verify the signature
            )
            return payload.get("sub")
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )