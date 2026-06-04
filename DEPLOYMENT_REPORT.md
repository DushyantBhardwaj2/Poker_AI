# Deployment & Infrastructure Report

## Overview
PokerSense AI utilizes a decoupled modern web stack:
- **Frontend:** Astro (SSR + React Components) hosted on **Vercel**.
- **Backend:** FastAPI (Python) wrapped in **Docker**, deployed on **Render** (free-tier constraint compliant).
- **Database:** Neon Serverless PostgreSQL.

## Stabilized Configurations
1. **Container Image Operations:** Removed massive model artifacts and legacy training notebooks (`ml_modules/`) out of the container image via a rigorous `.dockerignore`. Boot times on Render will see significant improvements, and storage saturation alerts resolved.
2. **Requirements Resolution:** Switched from `editable` local package installations (`-e ./packages...`) in Docker, ensuring reproducible independent builds.
3. **Vercel Routing:** The API lib respects `PUBLIC_API_URL` to route correctly from edge functions directly to Render's backend, handling Astro's SSR flow vs Browser hydration paths intelligently.

## Recommended Architectural Uplift (Future)
- **In-Memory Tracking:** Current real-time sessions are mapped via a global dictionary (`active_sessions`) running in `main.py`. Because Render free instances spool down randomly, active players will lose sessions on cold starts. Recommend moving this into Redis caching via Upstash or directly inside Postgres to achieve stateless scaling.