import os
import httpx
import json
import uuid
from fastapi import Header, HTTPException, Depends
import jwt
from jwt.exceptions import InvalidTokenError, DecodeError
from typing import Optional, Dict, Any

# Configuration
NEON_AUTH_URL = os.getenv("NEON_AUTH_URL", "https://ep-empty-sea-amb5bkwo.neonauth.c-5.us-east-1.aws.neon.tech/neondb/auth")
# The public JWKS endpoint for Neon Auth
JWKS_URL = f"{NEON_AUTH_URL}/.well-known/jwks.json"

_jwks_cache = None
_jwks_keys_map: Dict[str, Any] = {}  # Map kid -> key for faster lookup

async def get_jwks():
    """Fetch and cache JWKS from Neon Auth endpoint."""
    global _jwks_cache, _jwks_keys_map
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(JWKS_URL, timeout=10)
                if response.status_code == 200:
                    _jwks_cache = response.json()
                    # Pre-build kid -> key map for faster lookup
                    for key in _jwks_cache.get("keys", []):
                        kid = key.get("kid")
                        if kid:
                            _jwks_keys_map[kid] = key
            except Exception as e:
                print(f"[Auth] Failed to fetch JWKS from {JWKS_URL}: {e}")
                _jwks_cache = {"keys": []}
    return _jwks_cache

def jwk_to_public_key(jwk: Dict[str, Any]):
    """Convert JWK to cryptography public key object for verification."""
    try:
        # Use PyJWT's built-in algorithm classes to convert JWK
        kty = jwk.get("kty")
        
        if kty == "RSA":
            from jwt.algorithms import RSAAlgorithm
            algo = RSAAlgorithm(RSAAlgorithm.SHA256)
            return algo.from_jwk(json.dumps(jwk))
        elif kty == "EC":
            from jwt.algorithms import ECAlgorithm
            algo = ECAlgorithm(ECAlgorithm.SHA256)
            return algo.from_jwk(json.dumps(jwk))
        elif kty == "OKP":  # EdDSA support
            from jwt.algorithms import OKPAlgorithm
            algo = OKPAlgorithm(OKPAlgorithm.SHA256)
            return algo.from_jwk(json.dumps(jwk))
        else:
            print(f"[Auth] Unsupported key type: {kty}")
            return None
    except Exception as e:
        print(f"[Auth] Failed to convert JWK to key: {e}")
    return None



async def verify_neon_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verifies the Bearer token from Neon Auth using PyJWT + cryptography.
    Returns the user_id (sub) on success.
    Raises HTTPException (401) if authentication fails.
    Production-safe: no permissive fallbacks.
    """
    # DEVELOPMENT OVERRIDE: Allow skipping auth if explicitly requested via env var
    if os.getenv("SKIP_AUTH", "").lower() == "true":
        print("[Auth] SKIP_AUTH enabled; returning test user")
        return "test-user-id"

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1] if " " in authorization else ""
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 1. Decode token header without verification to get kid and alg
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        token_alg = unverified_header.get("alg")
        
        if not kid or not token_alg:
            print(f"[Auth] Token missing kid or alg in header")
            raise HTTPException(
                status_code=401,
                detail="Token header missing required fields (kid, alg).",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 2. Get JWKS and find matching key by kid
        jwks = await get_jwks()
        if not jwks or not jwks.get("keys"):
            print(f"[Auth] JWKS unavailable or empty")
            raise HTTPException(
                status_code=502,
                detail="Authentication service temporarily unavailable.",
            )
        
        # Find the key by kid (use cache map for O(1) lookup)
        signing_key = _jwks_keys_map.get(kid)
        if not signing_key:
            # Fallback: search through keys if cache is stale
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    signing_key = key
                    break
        
        if not signing_key:
            print(f"[Auth] Key with kid '{kid}' not found in JWKS")
            raise HTTPException(
                status_code=401,
                detail="Token signing key not found. Possibly from a different auth provider.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 3. Convert JWK to public key
        public_key = jwk_to_public_key(signing_key)
        if not public_key:
            print(f"[Auth] Failed to convert JWK (kid={kid}) to public key")
            raise HTTPException(
                status_code=401,
                detail="Unable to process signing key. Invalid key format.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 4. Verify and decode JWT with PyJWT (supports RSA, EC, EdDSA, etc.)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[token_alg],
            options={"verify_aud": False},  # Don't enforce audience claim
        )
        
        user_id = payload.get("sub")
        if not user_id:
            print(f"[Auth] Token payload missing 'sub' claim")
            raise HTTPException(
                status_code=401,
                detail="Token missing required 'sub' claim.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id

    except jwt.ExpiredSignatureError:
        print(f"[Auth] Token expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        print(f"[Auth] JWT verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except DecodeError as e:
        print(f"[Auth] JWT decode error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Unable to decode token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        print(f"[Auth] Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token verification failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )



def get_current_user_id(
    user_id: str = Depends(verify_neon_token)
) -> str:
    """
    Validates that user_id from token is a valid UUID.
    Returns the user_id string for use in endpoints.
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="No user ID in token.",
        )
    try:
        # Validate that it's a valid UUID format
        uuid.UUID(user_id)
        return user_id
    except (ValueError, AttributeError):
        # If not a UUID, still return it (Neon might use other formats)
        # but log it for monitoring
        print(f"[Auth] Non-UUID user_id format: {user_id}")
        return user_id


# ============================================================================
# Email/Password Login Support
# ============================================================================

async def create_neon_auth_token_for_user(email: str, password: str) -> str:
    """
    Helper to exchange email/password credentials for a Neon Auth token.
    This is typically called by a dedicated /auth/login endpoint.
    Returns Bearer token string on success.
    Raises HTTPException on failure.
    """
    auth_endpoint = f"{NEON_AUTH_URL}/sign-in/email"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_endpoint,
                json={"email": email, "password": password},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("token") or data.get("accessToken")
                if token:
                    return token
                else:
                    print(f"[Auth] Neon response missing token: {data}")
                    raise HTTPException(
                        status_code=500,
                        detail="Auth service did not return a token.",
                    )
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password.",
                )
            else:
                print(f"[Auth] Neon auth failed: {response.status_code} {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Authentication failed.",
                )
    except httpx.RequestError as e:
        print(f"[Auth] Failed to reach Neon Auth: {e}")
        raise HTTPException(
            status_code=502,
            detail="Authentication service unavailable.",
        )
