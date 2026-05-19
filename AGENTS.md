# AGENTS.md

## Project overview

Two independent packages in a monorepo — work in each directory separately. No shared scripts, no workspace-level tooling.

- `web/` — Vue 3 + Vite SPA (Chart.js, Vue Router). Supports all LTH programmes via a programme selector.
- `scraper/` — Python CLI that fetches all LTH programmes and their course/evaluation data, exports a unified JSON.

The web app is deployed via rsync on push to `main`. The scraper runs on the server via manual workflow dispatch and auto-copies the output JSON to the web directory.

## Commands

### web (from `web/`)

```bash
npm install      # dependencies (uses npm, NOT yarn/pnpm)
npm run dev      # Vite dev server
npm run build    # production build → web/dist/
npm run preview  # preview production build
```

No lint, typecheck, or test scripts configured.

### scraper (from `scraper/`)

```bash
uv sync                  # install dependencies
uv run scraper.py        # full pipeline: fetch all programmes → DB → JSON
uv run scraper.py <CODE> # single programme (e.g. MMSR, D, C)
```

Python 3.13. Uses `uv` as package manager. No tests or lint tools.

## Data pipeline

1. `uv run scraper.py` → `scraper/output/courses_data.json` + `scraper/lth_data.db`
2. The `run_scraper.yml` workflow auto-copies `scraper/output/courses_data.json` → web's public directory on the server.
3. For local dev, place a mock `courses_data.json` in `web/public/` (gitignored).

**DB is rebuilt from scratch on every run** — `init_db()` drops all 5 tables and recreates them. No data persists between runs.

### Database schema (5 tables)

| Table | Purpose |
|---|---|
| `programmes` | LTH programme list (code, name_sv, name_en) |
| `courses` | Course info (code, name, credits, grading, URLs) |
| `program_courses` | Many-to-many junction (programme_code, course_code) |
| `course_offerings` | Offering periods and years per course |
| `course_evaluations` | CEQ scores per course per semester |

### JSON structure

```json
{
  "courses": [{ "course_code": "EDAN15", "name": "...", "evaluations": [...], ... }],
  "programs": {
    "MMSR": { "name_sv": "...", "name_en": "...", "course_codes": ["EDAN15", ...] }
  },
  "metadata": { "generated_at": "...", "total_courses": ..., "total_evaluations": ... }
}
```

Courses appear once in the `courses` array even if shared across multiple programmes. Programme membership is tracked via the `programs.{code}.course_codes` arrays.

## CI / Deploy

- **deploy.yml** (on push to `main`): builds web, rsyncs `web/dist/` and `scraper/` to server, runs `uv sync`.
- **run_scraper.yml** (manual dispatch): SSHs to server (port 32384), runs `uv run scraper.py` (all programmes), copies output JSON to web public dir.

Do NOT add a scraper step to the deploy workflow — the scraper is intentionally manual-only to avoid hammering LTH servers on every push.

## Important gitignore rules

- `web/public/courses_data.json` is gitignored — generated, never committed.
- `scraper/lth_data.db` and `scraper/output/` are gitignored at root level.
- `node_modules/`, `.venv/`, `dist/` are all gitignored.

## Architecture notes

### Web

- `web/src/composables/useCourseData.js` is a singleton — fetches data once on first `onMounted`, caches in module-level `ref`. Exposes `programmes`, `getCourse()`, `getProgrammeCourses()`, `getProgrammeMetadata()`.
- Router uses `createWebHistory()` (no hash mode). Server must serve `index.html` for all routes. Routes are programme-prefixed (`/programme/:programmeCode/course/:code`); legacy routes redirect to MMSR.
- `<router-view>` uses `:key="$route.fullPath"` to force component recreation on navigation, preventing stale-state issues.
- Programme selector in `App.vue` navbar; `document.title` updates reactively per programme.
- `WelcomeView` has dual mode: programme grid at `/`, programme stats at `/:programmeCode`.
- `CourseSidebar` filters courses by the current programme (received as prop from `App.vue`).
- `CourseDetail` compare dropdown is scoped to the same programme.
- `TrendChart` is purely data-driven — no programme awareness needed.
- `web/src/components/` holds the 6 components; router maps directly to 5 of them (TrendChart is imported by CourseDetail).

### Scraper

- `SCRIP_DIR` pattern means it always writes files relative to `scraper.py` location — safe to invoke from any working directory.
- Rate-limiting: `time.sleep(0.5)` after each course fetch and each evaluation fetch.
- `get_courses()` skips re-fetching year info and offerings for courses already in the DB (shared across programmes), only records the `program_courses` mapping.
- The LTH programme API is at `https://api.lth.lu.se/lot/courses/programmes`.
