# PokerSense AI - Performance & Infrastructure Notes

## 1. The Rendering Strategy (Frontend)
**Provider:** Vercel
**Architecture:** Astro + React component islands (`client:load` / `client:idle`).

**Optimization Notes:**
- **Zero-JavaScript base:** Astro successfully strips out JavaScript from the outer shells of `index.astro`, significantly improving First Contentful Paint (FCP).
- **Client Hydration:** Heavy components like `VirtualTable` or `AdvisorHUD` are hydrated only on the client via `client:load`.
- **CSS Handling:** Tailwind compiles down nicely. The site relies on minimal CSS variables. Look out for `framer-motion` bundle sizes over time, but for this scale, it remains within acceptable limits.

## 2. API Backend & ML Serving
**Provider:** Render (Free Tier)
**Architecture:** FastAPI Python container with Neon PostgreSQL backend.

**Optimization Notes:**
- **Cold-Start Latency:** Render free-tier containers inevitably spin down after 15 minutes of inactivity. When a user requests data, the container reboot can take up to 30-50 seconds.
- **The "Wakeup" Solution:** Implemented a non-blocking background fetch (`wakeupBackend`) that hits the `/health` endpoint as soon as the client bundle initializes. This effectively starts the server spin-up process while the user is still on the splash screen, drastically reducing perceived wait time.
- **Docker Image Diet:** 
  - Reduced container size by removing unneeded development packages and strict `.dockerignore` enforcement.
  - Eliminated `pip install -e` which dramatically delayed startup and rebuild times.

## 3. Database Layer
**Provider:** Neon (Serverless Postgres)

**Optimization Notes:**
- **Scale-to-Zero:** Neon also scales to zero, meaning the first database query (often the authentication check or session retrieval) will take 1-3 seconds longer. 
- **Connection Safety:** Verified that the SQLAlchemy engine does not aggressively pool connections in a way that blocks serverless environments.

## Future Recommendations
- **Edge Deployment for API:** If traffic increases, consider migrating the FastAPI layer to Vercel Serverless Functions or a paid Render tier to eliminate Cold Starts entirely.
- **Pre-computed ML Dependencies:** Ensure any large `joblib` files are either heavily compressed or served from AWS S3, as memory overhead during boot directly impacts execution speed.