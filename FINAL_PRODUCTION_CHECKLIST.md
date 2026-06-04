# Final Production Checklist

## Application Security
- [x] Hardcoded `SKIP_AUTH` logic gated explicitly behind local environment vars.
- [x] Specific CORS Origins mapped for explicit frontend URLs (`poker-ai-black...`).
- [x] Wildcard cross-site attack vectors blocked (`allow_credentials=True` paired with wildcard regex removed).
- [x] Authentication gracefully handles 3rd-party IDP (Neon) availability issues.

## Reliability & Deployment
- [x] `.dockerignore` filters out `ml_modules/` to drastically reduce memory usage, caching sizes, and container build times on Render.
- [x] Local editable install (`-e ./packages/domain`) swapped for stable directory install inside container.
- [x] Health check explicitly returns application versions and environment details for observability.
- [x] In-memory active game sessions tracking (Known accepted limitation for MVP).

## Analytics & Data Integrity
- [x] DB schema drift fixes inside `stats_repository.py` to match `GameSession` Pydantic models.
- [x] Missing parameter crashing `/hand_result` resolved.
- [x] Fallback analytics APIs gracefully handle "new user" flow.

## Required Final Verifications
1. Ensure `PUBLIC_API_URL` is set in Vercel.
2. Ensure Vercel is connected to the Main branch.
3. Ensure Render service runs with `ENVIRONMENT=production`.