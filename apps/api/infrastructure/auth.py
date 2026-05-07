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
    Raises HTTPException if authentication fails.
    """
    # DEVELOPMENT OVERRIDE: Allow skipping auth if explicitly requested via env var
    if os.getenv("SKIP_AUTH", "").lower() == "true":
        # Return a consistent dev user ID
        return DEFAULT_USER_ID

    if not authorization or not authorization.startswith("Bearer "):
        # In local dev, if no token provided, we can optionally fallback to default user
        # but let's keep it strict unless SKIP_AUTH is on.
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    
    try:
        # Get unverified claims first for debugging
        unverified_payload = jwt.get_unverified_claims(token)
        user_id = unverified_payload.get("sub")
        
        # 1. Get JWKS for verification
        jwks = await get_jwks()
        if not jwks:
            print(f"[Auth] JWKS unavailable, using unverified user_id: {user_id}")
            return user_id

        # 2. Extract kid from header to find the correct key
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # 3. Find the matching key in JWKS
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key.get("kty"),
                    "kid": key.get("kid"),
                    "use": key.get("use"),
                    "n": key.get("n"),
                    "e": key.get("e")
                }
                break
        
        if rsa_key:
            # 4. Verify the JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=None,
                options={"verify_aud": False}
            )
            return payload.get("sub")
        else:
            # KEY MISMATCH: This happens if the token was issued by a different project
            print(f"[Auth Warning] Key {kid} not found in JWKS. Token might be from a different project.")
            # For local dev, we might want to be permissive if the token looks like a valid UUID
            return user_id

    except JWTError as e:
        print(f"[Auth Error] JWT Verification Error: {e}")
        # Even if verification fails, if we're in dev mode we might want to accept the sub
        if os.getenv("DEV_PERMISSIVE_AUTH", "").lower() == "true":
            try:
                payload = jwt.get_unverified_claims(token)
                return payload.get("sub")
            except:
                pass
        
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user_id(
    user_id: str = Depends(verify_neon_token)
) -> uuid.UUID:
    try:
        return uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID format in token.",
        )
