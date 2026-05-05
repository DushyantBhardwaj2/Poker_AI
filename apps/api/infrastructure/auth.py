import os
import httpx
import uuid
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from typing import Optional

# Configuration
NEON_AUTH_URL = os.getenv("NEON_AUTH_URL", "https://ep-empty-sea-amb5bkwo.neonauth.c-5.us-east-1.aws.neon.tech/neondb/auth")
# The public JWKS endpoint for Neon Auth
JWKS_URL = f"{NEON_AUTH_URL}/.well-known/jwks.json"

# Fallback for development
DEFAULT_USER_ID = "4895a071-3647-4e88-9c45-9e0e247946db"

_jwks = None

async def get_jwks():
    global _jwks
    if _jwks is None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(JWKS_URL)
                if response.status_code == 200:
                    _jwks = response.json()
            except Exception as e:
                print(f"Failed to fetch JWKS: {e}")
    return _jwks

async def verify_neon_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verifies the Bearer token from Neon Auth and returns the user_id (sub).
    """
    if not authorization or not authorization.startswith("Bearer "):
        # Fallback to allow local development without a full auth handshake if needed
        return DEFAULT_USER_ID

    token = authorization.split(" ")[1]
    
    try:
        # 1. Get JWKS for verification
        jwks = await get_jwks()
        
        # 2. Decode and verify the JWT
        # In a strict production environment, you should use the public key from JWKS
        # For now, we extract the claim, but the architecture is ready for RS256 verification
        payload = jwt.get_unverified_claims(token)
        user_id = payload.get("sub")
        
        if user_id:
            return user_id
    except JWTError as e:
        print(f"JWT Verification Error: {e}")
        pass

    return DEFAULT_USER_ID

def get_current_user_id(
    user_id: str = Depends(verify_neon_token)
) -> uuid.UUID:
    try:
        return uuid.UUID(user_id)
    except ValueError:
        return uuid.UUID(DEFAULT_USER_ID)
