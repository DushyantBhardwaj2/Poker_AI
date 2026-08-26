# PokerSense AI frontend

Astro 6 with React islands. See the [root README](../../README.md) for what the
project is and how the pieces fit together.

## Layout

```
src/
├── pages/          file-based routes; theory/[id].astro renders one chapter
├── components/     React islands (table, advisor HUD, analytics) + Astro views
├── stores/         usePokerStore.ts: Zustand, holds live hand state
├── lib/
│   ├── api.ts      typed client, base-URL resolution, backend warmup
│   └── auth.ts     Neon Auth session + token retrieval
└── styles/
```

Only the interactive parts hydrate. The theory chapters and static pages ship no
client JavaScript, which is the reason for choosing Astro over a SPA.

`output: 'server'` with the Vercel adapter, so pages are server-rendered rather
than prerendered.

## Commands

| Command | Action |
| :--- | :--- |
| `npm install` | Install dependencies |
| `npm run dev` | Dev server on `localhost:4321`, proxying `/api` to `localhost:8000` |
| `npm run build` | Production build |
| `npm run preview` | Serve the build locally |

## Configuration

Both are read at build time via `import.meta.env`, so they must be set in the
Vercel project, not just at runtime.

| Variable | Purpose |
| :--- | :--- |
| `PUBLIC_API_URL` | Backend base URL including `/api/v1`. Omit for local dev and the Vite proxy handles it. |
| `PUBLIC_NEON_AUTH_URL` | Neon Auth project URL, for sign-in and token issuance. |
