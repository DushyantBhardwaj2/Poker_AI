# PokerSense AI

A decision-support tool for live No-Limit Hold'em. You log the action at a physical
table as it happens; it returns pot odds, hand equity, an opponent read, and a
fold/call/raise recommendation with the reasoning attached.

**Live:** [poker-ai-black.vercel.app](https://poker-ai-black.vercel.app)

It is not a bot and it does not play. It is closer to a HUD for a game that has no
telemetry, the kind of tracking online players get for free, reconstructed from
hand-entered actions at a home game.

The interesting half is the opponent model. Anyone can compute pot odds; the part
worth building was a bluff detector trained on real showdowns rather than on my own
guesses about what a bluff looks like. That's covered in
[ml_modules/MAKING_OF_ML_MODULE.md](ml_modules/MAKING_OF_ML_MODULE.md), including the
dead end I started from.

---

## What it does

**Math layer.** Deterministic, no model involved.

- Hand equity by Monte Carlo simulation (1,000 rollouts by default, configurable
  per request via `num_simulations`, capped at 10,000)
- Pot odds and required equity for the current call
- Implied odds for drawing hands
- `EV = (win% × pot) - (lose% × call)`

**Behavioral layer.** The trained part.

- Bluff probability from an XGBoost classifier over 16 narrative features
  (relative bet size, bet spike across streets, board dryness, and the
  tightness/bet interaction term that makes a big bet mean different things
  from a nit and from a maniac)
- Trained only on hands that reached a showdown, so the labels are the real cards
  rather than my guess about them
- Opponent profiling: VPIP, PFR, and aggression factor accumulated across sessions,
  blended toward a baseline until there are enough hands to trust it

**Recommendation layer.** Combines the two. Pot odds set the baseline; the bluff
read is what moves a marginal fold into a call.

**Theory reference.** 20 chapters distilled from Sklansky's *The Theory of Poker*,
served at `/theory`, so a recommendation can point at the concept behind it.

---

## Model performance

Measured on a held-out set of 123,000 showdown records. Full methodology,
feature list, and the labeling pivot are in
[MAKING_OF_ML_MODULE.md](ml_modules/MAKING_OF_ML_MODULE.md).

| Metric | Value | Why it's the metric that matters |
|---|---|---|
| River precision | 93.2% | A false "he's bluffing" costs a stack. Precision was optimized at the expense of recall. |
| Turn precision | 71.1% | Less board information, so a lower bar, still usable for a read. |
| ROC AUC | 0.750 | Separates bluffs from value bets across all thresholds. |
| PR AUC | 0.620 | The honest number for a rare positive class. |
| Log loss | 0.312 | Probabilities are calibrated, not just ranked. |
| Inference latency | ~12 ms | Fast enough to answer inside a hand. |

Training data: 615,000 ground-truth showdowns (cards revealed, so the label is
real) extracted from 5.8M parsed hands. The first version used heuristic weak
supervision and scored badly for an instructive reason: the labels encoded my
assumptions, so the model learned to agree with me instead of with the data.

Recall is deliberately low. The detector stays silent on roughly half of all
bluffs. That is the intended trade.

---

## Limitations

Worth knowing before you trust it at a table:

- **Free-tier cold start.** The API sleeps after 15 minutes idle on Render.
  First request after that takes up to ~40s while the container and model load.
  The frontend pings `/health` on page load to hide most of this, but it's still
  the first thing you'll notice.
- **Two players only, in practice.** The bluff features were engineered on
  heads-up-style betting narratives. Multiway pots are accepted but the read is
  weaker.
- **Manual entry is the bottleneck.** Everything depends on you logging actions
  correctly and in order. There is no card recognition.
- **Cash-game assumptions.** No ICM, no bubble factor, no tournament awareness.
- **Training data is online poker.** Live players at a home game are looser and
  more passive than the HandHQ population; profiles will drift.
- **The bluff threshold is a flat 0.4 on every street.** Turn and river precision
  differ by 22 points at that cutoff, which is exactly the argument for a per-street
  threshold. Training computes the calibrated one and only logs it; nothing persists
  it into the saved model.
- **Showdown-only training data is a biased sample.** A bluff that works is a bluff
  nobody sees, so the model learns the kind of bluff that gets called. That points in
  a useful direction for a tool about when to call, but it is still a bias.
- **The committed model needs a retrain.** The parser that built the training set
  credited every bet to the next player to act instead of the one who made it, and
  because hole cards are joined on player id, each bet also carried the wrong
  player's cards. On showdown hands that inverts the label rather than adding noise.
  It is fixed in `ml_modules/src/parsers/data_loader.py` and pinned by
  `tests/unit/test_phh_parser.py`, but the `.joblib` in `packages/ai/models/`
  predates the fix, so its reported precision describes a model fit on mislabeled
  rows. Details in
  [`ml_modules/MAKING_OF_ML_MODULE.md`](ml_modules/MAKING_OF_ML_MODULE.md).
- **1,000 rollouts is a variance/latency compromise.** Equity is accurate to
  roughly ±1.5%, which is fine for a fold/call line and not fine for anything
  that needs three decimal places.

---

## Architecture

```
Poker_AI/
├── apps/
│   ├── api/                        FastAPI service
│   │   ├── application/            use cases: start_game, process_action, showdown
│   │   ├── infrastructure/         JWT verification, structured logging
│   │   └── interfaces/             main.py + game/ai/stats controllers
│   └── web/                        Astro 6 + React islands, deployed to Vercel
│       └── src/{components,lib,pages,styles}
├── packages/
│   ├── ai/                         advisor, bluff detector, profiler, equity
│   │   └── models/                 bluff_detector_showdown_v3.joblib
│   └── domain/                     hand evaluator, deck, SQLAlchemy models, repos
├── ml_modules/                     offline pipeline (not deployed)
│   ├── src/{parsers,features,labeling,models,evaluation}
│   └── MAKING_OF_ML_MODULE.md      how the model was built
├── tests/{unit,integration}
├── Dockerfile                      what Render builds
└── render.yaml                     service definition
```

The split that matters: `ml_modules/` is the offline training pipeline and never
ships. The runtime only loads the serialized model from `packages/ai/models/`, so
the API image doesn't carry pandas, xgboost training deps, or 5.8M hands of data.

**Stack.** FastAPI on Python 3.11, SQLAlchemy against Neon serverless Postgres,
Neon Auth for JWT via JWKS. Frontend is Astro with React islands, Tailwind 4,
Zustand for game state, Framer Motion. Backend is Dockerized on Render, frontend
on Vercel.

---

## Running it locally

Requires Node 20+ and Python 3.11+. No database setup needed: `DATABASE_URL`
falls back to a local SQLite file, and the schema is dialect-portable.

```bash
git clone https://github.com/DushyantBhardwaj2/Poker_AI.git
cd Poker_AI
```

Backend, from the repository root, because the imports are absolute (`apps.api...`,
`packages...`), so running from inside `apps/api` will not work:

```bash
pip install -r requirements.txt
uvicorn apps.api.interfaces.main:app --reload --port 8000
```

Port 8000 is not arbitrary: the Astro dev server proxies `/api` there and the SSR
fallback in `apps/web/src/lib/api.ts` uses the same, so the frontend finds the
backend with no configuration. Production runs on 10000 because that's what
`render.yaml` sets. Override either side with `PUBLIC_API_URL` in `apps/web/.env`.

To skip authentication while developing, set both `SKIP_AUTH=true` and
`ENVIRONMENT=local`. The check requires both, so the flag can't accidentally do
anything in a deployed environment. Copy `.env.example` to `.env` for the rest;
every variable in it has a working default except `NEON_AUTH_URL`, which you only
need if you want real logins.

Frontend, in a second terminal:

```bash
cd apps/web
npm install
npm run dev
```

Tests:

```bash
python -m pytest
```

133 tests, about 13 seconds, no setup. `tests/conftest.py` points the app at a
throwaway SQLite file for the run, so the integration tests no longer need a
reachable Postgres or a hand-seeded database. To create a real schema for running
the app, `python scripts/init_db.py`.

To retrain the model instead of using the committed one, `ml_modules/` has its own
`requirements.txt` and its own pipeline entry point at
`ml_modules/pipeline/run_pipeline.py`; it is not needed to run the app. That path
needs the hand-history corpus, which is not in the repository.

---

## API

Interactive docs at `/docs` once the server is up. Routers are mounted under
`/api/v1`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness + version. Also the cold-start warmup target. |
| `POST` | `/api/v1/ai/analyze-full` | Everything at once: equity, pot odds, bluff read, recommendation. |
| `POST` | `/api/v1/ai/win-probability` | Monte Carlo equity for a hand and board. |
| `POST` | `/api/v1/ai/recommend-move` | Fold/call/raise with reasoning. |
| `POST` | `/api/v1/ai/analyze-bluff` | Bluff probability for one opponent action. |
| `POST` | `/api/v1/ai/profile-opponent` | VPIP/PFR/aggression for a player. |
| `POST` | `/api/v1/game/session/start` | Open a session. |
| `POST` | `/api/v1/game/session/record_action` | Log one action. |
| `POST` | `/api/v1/game/session/showdown` | Resolve the hand and side pots. |
| `GET` | `/api/v1/stats/session/{id}/analytics` | Session summary. |

Everything except `/health` and `/` requires a `Bearer` token from Neon Auth.
See [AUTH_SETUP.md](AUTH_SETUP.md).

---

## Design notes

A few decisions that took more than one attempt:

**Precision over recall, by construction.** The threshold sits where river
precision hits 93%. A false positive tells the user to call a value bet, which is
the most expensive mistake the tool can make. Staying quiet is cheap.

**Absolute imports and a root Docker context.** `apps/api` imports `packages/`
directly. It means the API cannot be started from its own directory, which is
surprising, but the alternative was duplicating the domain layer or publishing it
as a package for a two-app repo.

**Astro islands rather than a SPA.** The theory chapters are static content and
have no reason to ship a router. Only the table, advisor HUD, and analytics
hydrate.

**One schema, two dialects.** Production is Postgres and wants native `UUID` and
`JSONB`; a contributor cloning the repo wants to not install Postgres. Rather than
maintaining two model files, `packages/domain/db_models.py` defines a
`TypeDecorator` that emits `UUID` on Postgres and `CHAR(32)` elsewhere, and picks
`JSONB` or `JSON` by dialect. Same models, same migrations, either backend.

**Non-blocking warmup instead of a paid instance.** `wakeupBackend()` fires at
`/health` on first paint. By the time a user has entered player names, the
container is usually up.

---

## Roadmap

- WebSockets so several phones at the same table stay in sync
- Range analyzer, and hand-history replay
- Port the pure-math endpoints to Vercel Edge so pot odds never wait on a cold
  container
- Multiway-aware bluff features
- Retrain against live-game data once there's enough of it

---

## Credits

The strategy layer follows David Sklansky's *The Theory of Poker*. Training data
comes from the HandHQ, ACPC, and WSOP hand-history corpora; parsing uses
[pokerkit](https://github.com/uoftcprg/pokerkit).

MIT licensed, see [LICENSE](LICENSE).
