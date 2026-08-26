import json
import os
import time
import traceback
import uuid
from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import Depends, Header, HTTPException

# Neon Auth issues the JWTs this API trusts. Deliberately not validated at import
# time: the module still has to load for local runs that set SKIP_AUTH=true, and a
# missing variable is better reported as a 503 on the first authenticated request
# than as a crash loop on boot.
NEON_AUTH_URL = os.getenv("NEON_AUTH_URL")

# JWKS is cached to avoid an outbound request per token verification, but the cache
# needs a TTL because signing keys rotate. Without one, a rotation locks every user
# out until the process is restarted.
_JWKS_TTL_SECONDS = 600
_jwks_keys_map: Dict[str, Any] = {}  # kid -> JWK
_jwks_fetched_at = 0.0


def _require_auth_base() -> str:
    """Return the Neon Auth base URL, or fail with a 503 explaining what is missing."""
    if not NEON_AUTH_URL:
        # Interpolating an unset variable yields "None/...", which fails deep inside
        # httpx as an unrelated-looking protocol error.
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured on this server (NEON_AUTH_URL is unset).",
        )
    return NEON_AUTH_URL.rstrip("/")


def _jwks_url() -> str:
    return f"{_require_auth_base()}/.well-known/jwks.json"


async def get_jwks(force_refresh: bool = False) -> Dict[str, Any]:
    """Return a kid -> JWK map, refetching when the cache is empty, stale or forced.

    A failed fetch leaves the previous cache in place on purpose. Caching the
    failure instead (as storing {"keys": []} did) is unrecoverable when the only
    refresh condition is an unset cache: one transient network blip then makes
    every subsequent request fail until the process restarts.
    """
    global _jwks_fetched_at

    is_fresh = bool(_jwks_keys_map) and (time.monotonic() - _jwks_fetched_at) < _JWKS_TTL_SECONDS
    if is_fresh and not force_refresh:
        return _jwks_keys_map

    url = _jwks_url()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
        response.raise_for_status()
        keys = {k["kid"]: k for k in response.json().get("keys", []) if k.get("kid")}
    except (httpx.HTTPError, ValueError) as e:
        # Keep serving the old keys; an empty map becomes a 503 in the caller.
        print(f"[Auth] Failed to fetch JWKS from {url}: {e}")
        return _jwks_keys_map

    if keys:
        _jwks_keys_map.clear()
        _jwks_keys_map.update(keys)
        _jwks_fetched_at = time.monotonic()
    return _jwks_keys_map


# Signature algorithm to assume per key type when a JWK omits "alg".
_KTY_DEFAULT_ALGS = {"RSA": {"RS256"}, "EC": {"ES256"}, "OKP": {"EdDSA"}}


def _allowed_algorithms(jwk: Dict[str, Any]) -> set[str]:
    """Algorithms a key may be used with, taken from the key and never the token.

    The `algorithms` argument to jwt.decode is what separates a valid token from a
    forged one, so it has to come from the trusted JWKS. Feeding the token's own
    "alg" header back in lets the caller pick how their token gets verified, which
    is the shape of the classic JWT algorithm-confusion bug.
    """
    alg = jwk.get("alg")
    if alg:
        return {alg}
    return _KTY_DEFAULT_ALGS.get(jwk.get("kty", ""), set())


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

            algo = OKPAlgorithm()
            return algo.from_jwk(json.dumps(jwk))
        else:
            print(f"[Auth] Unsupported key type: {kty}")
            return None
    except Exception as e:
        print(f"[Auth] Failed to convert JWK to key: {e}")
    return None


async def verify_neon_token(
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Verifies the Bearer token from Neon Auth using PyJWT + cryptography.
    Returns the user data (dict with sub, email, name) on success.
    Raises HTTPException (401) if authentication fails.
    """
    # DEVELOPMENT OVERRIDE: Allow skipping auth ONLY if explicitly requested AND environment is strictly local
    if os.getenv("SKIP_AUTH", "").lower() == "true" and os.getenv("ENVIRONMENT", "").lower() in ["local", "development"]:
        test_id = "00000000-0000-0000-0000-000000000000"
        print(f"[Auth] SKIP_AUTH enabled in local environment; returning test user {test_id}")
        return {
            "user_id": test_id,
            "sub": test_id,
            "email": "test@poker-sense.ai",
            "name": "Test Operator",
        }

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

        # 2. Look the key up by kid. A miss usually means the provider rotated its
        #    keys since the last fetch, so retry once against a fresh JWKS before
        #    rejecting an otherwise valid token.
        keys = await get_jwks()
        signing_key = keys.get(kid)
        if not signing_key:
            keys = await get_jwks(force_refresh=True)
            signing_key = keys.get(kid)

        if not keys:
            print("[Auth] JWKS unavailable or empty")
            raise HTTPException(
                status_code=503,
                detail="Authentication service temporarily unavailable.",
            )

        if not signing_key:
            print(f"[Auth] Key with kid '{kid}' not found in JWKS")
            raise HTTPException(
                status_code=401,
                detail="Token signing key not found. Possibly from a different auth provider.",
            )

        # 3. Pin the algorithm to what the *key* permits, then convert it.
        allowed_algs = _allowed_algorithms(signing_key)
        if not allowed_algs:
            print(f"[Auth] Unsupported key type for kid={kid}: {signing_key.get('kty')}")
            raise HTTPException(
                status_code=401,
                detail="Unable to process signing key. Unsupported key type.",
            )
        if token_alg not in allowed_algs:
            print(f"[Auth] Token alg '{token_alg}' not permitted for kid={kid} ({allowed_algs})")
            raise HTTPException(
                status_code=401,
                detail="Token algorithm is not permitted for its signing key.",
            )

        public_key = jwk_to_public_key(signing_key)
        if not public_key:
            print(f"[Auth] Failed to convert JWK (kid={kid}) to public key")
            raise HTTPException(
                status_code=401,
                detail="Unable to process signing key. Invalid key format.",
            )

        # 4. Verify and decode JWT with PyJWT
        payload = jwt.decode(
            token,
            public_key,
            algorithms=sorted(allowed_algs),
            options={"verify_aud": False},
        )

        user_id = payload.get("sub")
        if not user_id:
            print("[Auth] Token payload missing 'sub' claim")
            raise HTTPException(
                status_code=401,
                detail="Token missing required 'sub' claim.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Success: Return payload subset
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
            # Also keep raw sub for compatibility
            "sub": user_id,
        }

    # Must precede `except Exception`: HTTPException is an Exception, so without
    # this the deliberate 503/401 raised above were caught below and rewritten as a
    # 401 whose detail embedded the original status ("Reason: 503: ...").
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        print("[Auth] Token expired")
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
    except Exception as e:
        # Anything reaching here is a server-side fault, not a bad credential, so
        # it is a 500, and the message stays server-side rather than being echoed
        # back to an unauthenticated caller.
        print(f"[Auth] Unexpected error during token verification: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Token verification failed due to a server error.",
        )


from packages.domain.database import SessionLocal
from packages.domain.stats_repository import StatsRepository


def get_current_user_id(user_data: Dict[str, Any] = Depends(verify_neon_token)) -> str:
    """
    Validates user_id and syncs user info (email/name) to the local database.
    Returns the user_id string for use in endpoints.
    """
    user_id = user_data.get("user_id")
    email = user_data.get("email")
    name = user_data.get("name")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="No user ID in token.",
        )

    # Every table keys users by a UUID, so a `sub` that is not one cannot be stored
    # or queried. Rejecting it here turns what used to be a swallowed sync failure
    # followed by an opaque database error further down into one clear 401.
    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError, TypeError):
        print(f"[Auth] Token 'sub' is not a UUID: {user_id!r}")
        raise HTTPException(
            status_code=401,
            detail="Token subject is not a valid user identifier.",
        )

    # Sync User to Local Database (Background-ish sync during each request)
    try:
        with SessionLocal() as db:
            repo = StatsRepository(db)
            repo._ensure_user_exists(user_id=user_uuid, email=email, name=name)
            db.commit()
    except Exception as e:
        # Don't fail the request if sync fails, but log it
        print(f"[Auth] User sync failed for {user_id}: {e}")

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
    auth_endpoint = f"{_require_auth_base()}/sign-in/email"
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
                print(
                    f"[Auth] Neon auth failed: {response.status_code} {response.text}"
                )
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
