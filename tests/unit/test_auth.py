"""Regression tests for JWT verification in apps/api/infrastructure/auth.py.

Each test here corresponds to a bug that was live: an unset NEON_AUTH_URL silently
produced the URL "None/.well-known/jwks.json"; a single failed JWKS fetch was cached
permanently, so one network blip rejected every request until restart; rotated
signing keys were never picked up; the verification algorithm was read from the
token's own header; and the deliberate "auth service unavailable" response was
caught by a broad `except Exception` and rewritten into a 401 that echoed the
internal message back to an unauthenticated caller.
"""
import asyncio
import time

import httpx
import pytest
from fastapi import HTTPException

from apps.api.infrastructure import auth

RSA_KEY = {"kid": "k1", "kty": "RSA", "alg": "RS256", "n": "x", "e": "AQAB"}
ROTATED_KEY = {"kid": "k2", "kty": "RSA", "alg": "RS256", "n": "y", "e": "AQAB"}

# Structurally valid JWTs; only the header is ever parsed in these tests.
TOKEN_KID_K1 = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImsxIn0.e30.sig"
TOKEN_KID_UNKNOWN = "eyJhbGciOiJSUzI1NiIsImtpZCI6Inp6eiJ9.e30.sig"
TOKEN_ALG_HS256 = "eyJhbGciOiJIUzI1NiIsImtpZCI6ImsxIn0.e30.sig"


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def _stub_client(behaviour):
    """Build a drop-in httpx.AsyncClient whose get() delegates to `behaviour`."""

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url, timeout=None):
            return behaviour()

    return _Client


@pytest.fixture
def jwks(monkeypatch):
    """Isolate the module-level JWKS cache and stub out network access."""
    monkeypatch.setattr(auth, "NEON_AUTH_URL", "https://auth.example.com")
    monkeypatch.setattr(auth, "_jwks_keys_map", {})
    monkeypatch.setattr(auth, "_jwks_fetched_at", 0.0)

    def serve(*keys):
        monkeypatch.setattr(
            auth.httpx, "AsyncClient", _stub_client(lambda: _Response({"keys": list(keys)}))
        )

    def fail():
        def boom():
            raise httpx.ConnectError("network down")

        monkeypatch.setattr(auth.httpx, "AsyncClient", _stub_client(boom))

    def expire():
        monkeypatch.setattr(auth, "_jwks_fetched_at", time.monotonic() - auth._JWKS_TTL_SECONDS - 1)

    serve.fail = fail
    serve.expire = expire
    return serve


def test_unset_auth_url_reports_configuration_error(monkeypatch):
    monkeypatch.setattr(auth, "NEON_AUTH_URL", None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.get_jwks())
    assert exc.value.status_code == 503
    assert "NEON_AUTH_URL" in exc.value.detail


def test_failed_fetch_does_not_discard_cached_keys(jwks):
    jwks(RSA_KEY)
    assert set(asyncio.run(auth.get_jwks())) == {"k1"}

    jwks.expire()
    jwks.fail()
    assert set(asyncio.run(auth.get_jwks())) == {"k1"}, "a transient failure emptied the cache"


def test_rotated_keys_are_picked_up_after_ttl(jwks):
    jwks(RSA_KEY)
    asyncio.run(auth.get_jwks())

    jwks(ROTATED_KEY)
    assert set(asyncio.run(auth.get_jwks())) == {"k1"}, "refetched while still fresh"

    jwks.expire()
    assert set(asyncio.run(auth.get_jwks())) == {"k2"}


def test_force_refresh_bypasses_the_ttl(jwks):
    jwks(RSA_KEY)
    asyncio.run(auth.get_jwks())
    jwks(ROTATED_KEY)
    assert set(asyncio.run(auth.get_jwks(force_refresh=True))) == {"k2"}


@pytest.mark.parametrize(
    "jwk,expected",
    [
        ({"kty": "RSA", "alg": "RS256"}, {"RS256"}),
        ({"kty": "RSA"}, {"RS256"}),
        ({"kty": "EC"}, {"ES256"}),
        ({"kty": "OKP"}, {"EdDSA"}),
        ({"kty": "oct"}, set()),
    ],
)
def test_allowed_algorithms_come_from_the_key(jwk, expected):
    assert auth._allowed_algorithms(jwk) == expected


def test_symmetric_algorithm_never_allowed_for_asymmetric_key():
    """Guards the algorithm-confusion shape: an RSA public key used as an HMAC secret."""
    assert "HS256" not in auth._allowed_algorithms(RSA_KEY)


def test_token_algorithm_must_match_the_key(jwks):
    jwks(RSA_KEY)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.verify_neon_token(authorization=f"Bearer {TOKEN_ALG_HS256}"))
    assert exc.value.status_code == 401
    assert "algorithm is not permitted" in exc.value.detail.lower()


def test_unknown_kid_is_rejected_as_unauthorized(jwks):
    jwks(RSA_KEY)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.verify_neon_token(authorization=f"Bearer {TOKEN_KID_UNKNOWN}"))
    assert exc.value.status_code == 401
    assert "signing key not found" in exc.value.detail.lower()


def test_configuration_error_is_not_rewritten_as_unauthorized(monkeypatch):
    monkeypatch.setattr(auth, "NEON_AUTH_URL", None)
    monkeypatch.setattr(auth, "_jwks_keys_map", {})
    monkeypatch.setattr(auth, "_jwks_fetched_at", 0.0)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.verify_neon_token(authorization=f"Bearer {TOKEN_KID_K1}"))
    assert exc.value.status_code == 503, "the broad handler swallowed a deliberate status"
    assert "Reason:" not in str(exc.value.detail), "internal detail leaked to the caller"


@pytest.mark.parametrize("header", [None, "", "Basic abc", "Bearer", "Bearer "])
def test_malformed_authorization_header_is_unauthorized(header):
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.verify_neon_token(authorization=header))
    assert exc.value.status_code == 401
    assert exc.value.headers.get("WWW-Authenticate") == "Bearer"
