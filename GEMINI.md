# ♠️ PokerSense AI — AI Poker Advisor & Turn-Based Poker Tracker

## 1. Project Overview
**PokerSense AI** is a real-time poker intelligence system. Its primary goal is to provide high-speed, actionable advice during live poker games, deeply rooted in the foundational principles of David Sklansky's "The Theory of Poker".

**Current Status:** Priority 2 (ML Integration & Decision Engine) is 100% complete. The system can now perform real-time bluff detection using XGBoost, calculate range-aware win probability, and synthesize them into actionable advice with theoretical explanations.

## 2. System Behavior Expectations
- **Decision Usefulness over Metrics:** The system's primary directive is to provide the best possible *actionable* advice.
- **Explainable AI:** Recommendations include theoretical context (Pot Odds, Implied Odds, Fundamental Theorem).
- **Production Persistence:** Historical stats are stored in PostgreSQL with multi-tenant isolation via `user_id`.
- **Cold-Start Resilience:** New players are seeded with table-averaged stats for immediate inference accuracy.

## 3. Architecture Overview
- **Database (PostgreSQL/Neon)**: JSONB-powered storage for `opponent_stats`.
- **Backend (FastAPI)**: Stateless endpoints with repository-pattern data access.
- **Frontend (Astro + React)**: 
  - **AdvisorHUD**: Tactical UI for real-time win/bluff analysis.
  - **ActionTracker**: Real-time game state input.
- **AI Domain**: 
  - `bluff_detector.py`: Real-time XGBoost v3 inference.
  - `smart_advisor.py`: Synthesizes math and behavior into strategic advice.

**Current Status:** Priority 2 (ML & Frontend Integration) is 100% complete. The system is fully operational from database to UI.

## 4. Design Aesthetics & UX
- **Advanced Interface**: Dark-themed, high-contrast 'Black and Gold' aesthetic inspired by tactical HUDs.
- **Responsive & Tactile**: Full mobile support with optimized touch targets and tactile scale feedback on all interactive elements.
- **Minimal Clicks**: Real-time updates and simplified input flows to keep pace with live gameplay.
- **Automated Showdown & Pot Distribution**: 
  - The UI removes manual pot distribution entirely. Dealers only need to mark players as "SHOW" or "MUCK" and input the revealed hole cards.
  - The Python backend automatically evaluates all 5-card hands, determines the hierarchy, correctly computes side pots based on varying player stacks, and instantly returns the payouts.
  - Multi-winner split pots and complex side-pot resolutions are displayed dynamically in the `PostHandAnalysis` component, ensuring the tracking experience doesn't halt during complex multi-way all-ins.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)

## 5. Authentication & Security (Updated May 8, 2026)

### Neon Auth JWT Verification Upgrade
**Problem Solved:** 401 Unauthorized errors and 500 Internal Server crashes due to JWT algorithm mismatch.

**Root Cause:** Backend used `python-jose` which only supported RSA-256, but Neon Auth issued tokens with different algorithms (EC, EdDSA). When the library encountered an unsupported algorithm, it crashed with 500 instead of gracefully rejecting the token.

**Solution Implemented:**
1. **Replaced `python-jose` with `PyJWT[crypto]`** (commit `ab08297`)
   - Supports RSA, EC, EdDSA, and all modern JWT algorithms
   - Removed all permissive fallbacks — tokens must be cryptographically valid or return clean 401

2. **File Changes:**
   - `requirements.txt`: Swapped `python-jose[cryptography]` → `PyJWT[crypto]` + `cryptography`
   - `apps/api/infrastructure/auth.py`: Complete rewrite:
     - `verify_neon_token()`: Strict JWT verification using PyJWT's algorithm-agnostic decoder
     - `jwk_to_public_key()`: Converts JWK to crypto key for RSA/EC/EdDSA/OKP key types
     - `create_neon_auth_token_for_user()`: Helper for email/password login (future `/auth/login` endpoint)
   - `Dockerfile`: Fixed to use `requirements.txt` instead of hardcoded pip command (commit `5855516`)

3. **Error Handling (Production-Safe):**
   - Expired tokens → 401 "Token has expired"
   - Invalid signature → 401 "Invalid authentication token"
   - Missing JWKS → 502 "Authentication service temporarily unavailable"
   - Unsupported key type → 401 "Unable to process signing key"
   - No fallback to unverified tokens — all requests must pass cryptographic verification

4. **Frontend Email Login (Already Enabled):**
   - `apps/web/src/components/auth/LoginForm.tsx` handles sign-in via `authClient.signIn.email()`
   - `apps/web/src/components/auth/SignupForm.tsx` handles registration via `authClient.signUp.email()`, capturing operator name and experience level.
   - Google OAuth also available via `authClient.signIn.social(provider='google')`
   - Both flows issue Neon Auth tokens which backend now correctly validates

### JWT Verification Flow
```
Client Request
    ↓
Authorization: Bearer <token>
    ↓
verify_neon_token() extracts kid, alg from token header
    ↓
Fetch JWKS from Neon Auth /.well-known/jwks.json (cached)
    ↓
Find matching JWK by kid
    ↓
Convert JWK to crypto public key (supports RSA/EC/EdDSA)
    ↓
PyJWT.decode(token, public_key, algorithms=[alg])
    ↓
Return user_id (sub claim) on success
    ↓
Raise HTTPException(401) on any verification failure
```

### Deployment Status
- **Commit `ab08297`**: Auth refactor (PyJWT, no permissive fallback)
- **Commit `5855516`**: Dockerfile fix (use requirements.txt for correct dependencies)
- **Next Step**: Redeploy backend on Render from `master` branch
