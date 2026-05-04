# 🚀 Deployment Guide — PokerSense AI

This guide explains how to deploy PokerSense AI to a production environment.

## 🏗️ Architecture Overview
- **Frontend:** Astro (React) - Recommended: **Vercel** or **Netlify**.
- **Backend:** FastAPI (Python) - Recommended: **Render**, **Railway**, or **DigitalOcean App Platform**.
- **Database:** PostgreSQL - Recommended: **Neon** (Serverless).
- **ML Engine:** XGBoost model loaded directly by the FastAPI backend.

---

## 🛠️ Database Setup (Neon)
1. Create a new PostgreSQL project on [Neon](https://neon.tech).
2. Get your `DATABASE_URL`.
3. Run the initialization script locally to set up the schema:
   ```bash
   pip install -r requirements.txt
   export DATABASE_URL=your_neon_url
   python scripts/init_postgres.py
   ```

---

## 🔌 Backend Deployment (FastAPI)
Deploy the root of the repository or the `apps/api` context.

**Environment Variables:**
- `DATABASE_URL`: Your Neon connection string.
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend origins (e.g., `https://your-frontend.vercel.app`).
- `PORT`: (Default: 8000)

**Startup Command:**
```bash
uvicorn apps.api.interfaces.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎨 Frontend Deployment (Astro)
Deploy the `apps/web` directory.

**Environment Variables:**
- `PUBLIC_API_URL`: The full URL of your deployed backend API (e.g., `https://your-backend.render.com/api/v1`).

**Build Command:**
```bash
npm install
npm run build
```

---

## 🧪 Verification
After deployment, verify the following:
1. **Health Check:** `GET https://your-backend.render.com/health` should return `{"status": "healthy"}`.
2. **CORS:** Open your deployed frontend and check the console. Ensure no CORS errors occur during API calls.
3. **ML Inference:** Start a game on the frontend and ensure the AI Advisor provides recommendations.

---

## 💡 Troubleshooting
- **Blank Page:** Ensure `PUBLIC_API_URL` is set correctly. Check browser console for runtime errors.
- **Database Connection:** Ensure `DATABASE_URL` includes `?sslmode=require` for Neon.
- **Hydration Errors:** If using Astro View Transitions, ensure React components are wrapped correctly with `client:load` or `client:only`.
