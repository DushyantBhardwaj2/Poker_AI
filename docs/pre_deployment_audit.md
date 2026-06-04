# Pre-Deployment Audit Checklist

## Priority: SECURITY > ANALYTICS > DEPLOYMENT > CODE QUALITY

## 🔴 SECURITY
- [ ] `.env` — No live credentials. DB password rotated.
- [ ] `.env.example` — Placeholder values only.
- [ ] `apps/web/.env` — PUBLIC_API_URL points to production, not localhost.
- [ ] `apps/web/.env` — PUBLIC_NEON_AUTH_URL uses placeholder (not real endpoint).
- [ ] `SKIP_AUTH=true` — Removed from any production-adjacent .env.
- [ ] `localhost.har` — Deleted from disk. Added to .gitignore if not covered.
- [ ] `poker_ai.db` — Deleted from disk. Confirmed in .gitignore.
- [ ] `git log` — Checked for any committed secrets. Use `git filter-branch` if found.
- [ ] CORS — `allow_origin_regex` restricted to known domains only.
- [ ] CORS — `ALLOWED_ORIGINS` env var properly set on Render.
- [ ] No hardcoded API keys, tokens, or passwords in any source file.

## 🔴 ANALYTICS
- [ ] `AnalyticsView.tsx` — Session ID handling fixed (not passing empty string).
- [ ] `api.ts` — `getSessionAnalytics` properly distinguishes "no param" vs "empty string".
- [ ] `stats_controller.py` — Session lookup edge cases handled.
- [ ] `stats_repository.py` — `get_session_analytics` returns meaningful empty state.
- [ ] Frontend → backend session flow works end-to-end.
- [ ] `GameSession.name` vs `session_name` mismatch resolved.
- [ ] `_run_column_migrations()` — Idempotent, not running on every startup.

## 🟡 DEPLOYMENT
- [ ] Vercel project linked to correct Git account.
- [ ] `poker-ai-black.vercel.app` → deployed from `main` branch.
- [ ] `vercel.json` or Astro config — no hardcoded secrets.
- [ ] Render service linked to GitHub repo, auto-deploys on push.
- [ ] `/api/v1/version` endpoint returns commit hash + version.
- [ ] `render.yaml` — ALLOWED_ORIGINS set to production frontend URL.
- [ ] `.dockerignore` — excludes ml_modules/, .env, *.har, *.db, docs/, tests/, archive/.
- [ ] `Dockerfile` — No `-e` editable install. Uses proper pinned dependencies.

## 🟢 CODE QUALITY
- [ ] `requirements.txt` — Remove `-e ./packages/domain`, pin versions.
- [ ] `bluff_detector` global singleton — Safe for async/multi-worker.
- [ ] API endpoints — Input validation on all routes.
- [ ] No hardcoded timeouts that could break in production.
- [ ] Package-lock.json is up to date.
- [ ] All imports work correctly (Python path / sys.path).
- [ ] `npm run build` succeeds.
- [ ] `pytest` passes (or known failures documented).

## ✅ VERIFICATION
- [ ] Frontend: `https://poker-ai-black.vercel.app` loads correctly.
- [ ] Backend: `https://pokersense-api.onrender.com/health` returns 200.
- [ ] Version: `https://pokersense-api.onrender.com/api/v1/version` returns valid data.
- [ ] Analytics page displays data after playing hands.
- [ ] Auth works (or SKIP_AUTH documented for dev mode).
- [ ] CORS: frontend can make API requests without errors.
- [ ] `docker build -t pokersense-api .` succeeds.
- [ ] Git status is clean (no untracked secrets).
