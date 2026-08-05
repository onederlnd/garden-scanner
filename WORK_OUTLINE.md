# Work Outline

## Phase 1 — Data Layer

### `db/session.py` (engine, session, connection plumbing)

- [x] Set up engine
- [x] Decide where `DATABASE_URL` lives (env var vs. hardcoded)
- [x] Create the `sessionmaker`
- [x] Write the `get_db()` dependency generator

### `db/base.py` (shared declarative base)

- [x] Define `Base` — nothing else goes in this file

### `db/models/<resource>.py` (e.g. `plants.py`)

- [x] Import `Base` from `db/base.py`
- [x] Define the `<Resource>` model (e.g. `Plant`) with all fields from the data model
- [x] Decide nullable vs. required per field (`slug`, primary display-name field required; the rest nullable)
- [x] Add unique constraint + index on `slug`
- [x] Optional: add `__repr__` for debugging

### `db/models/__init__.py` (registry)

- [x] Import and re-export every model, so Alembic and the app can import from one place

### Initialize Alembic

- [x] Run Alembic init to scaffold `alembic/`
- [x] Point `alembic.ini`'s `sqlalchemy.url` at the dev database
- [x] Import `Base` (via `db.models`) into `env.py`, set `target_metadata`
- [x] Confirm autogenerate can detect each model

### First migration

- [x] Generate migration with `--autogenerate`
- [x] Review generated migration file before applying
- [x] Apply migration (`alembic upgrade head`)
- [x] Confirm table exists in the database

### Seed test data

- [x] Decide seeding method (script vs. fixtures file)
- [x] Pick a handful of items with varied attribute coverage
- [x] Fill in every field for each seeded item
- [x] Decide if seed script is re-runnable or one-time

## Phase 2 — Routes

### `schemas/<resource>.py` (e.g. `plants.py`)

- [x] `<Resource>Out` — all fields, `Optional` for nullable ones, `from_attributes=True` config
- [x] `<Resource>Create` — same as `Out` minus `id`
- [x] `<Resource>Update` — partial update, all fields optional with `= None` defaults
- [x] Top-level `schemas/` location (sibling of `db/models/`, not nested under `db/`)

### `schemas/__init__.py` (registry)

- [x] Re-export each resource's schema set, mirroring `db/models/__init__.py`

### `routes/<resource>.py`

- [x] Set up `APIRouter`
- [x] Directory route: query all items, return list of `<Resource>Out`
- [x] Detail route: query by slug, return `<Resource>Out`
- [x] Handle not-found case (404) on detail route
- [x] Import from `schemas` (e.g. `from schemas import PlantOut`)

### `routes/__init__.py` (registry)

- [x] Import each resource's router
- [x] Expose a collection `main.py` can loop over to `include_router()` each one

### `main.py`

- [x] Instantiate FastAPI app
- [x] Decide: keep `create_all()` as dev convenience, or Alembic-only (Alembic-only)
- [x] Loop the routes registry, `include_router()` each
- [x] Run dev server, confirm routes return seeded data as JSON

## Phase 3 — Templates

### `templates/<resource>_detail.html` (e.g. `plant_detail.html`)

- [x] Register `Jinja2Templates` pointed at `templates/`
- [x] Sketch page structure (header, key attributes, care/specs, timing, issues, notes)
- [x] Mobile-first layout: single column, large type
- [x] Handle null fields gracefully (skip row, don't show blank label)

### `templates/directory.html`

- [x] List all items with name + link to detail page
- [x] Decide list vs. card-grid layout
- [x] Leave placeholder space for Phase 6 filter UI

### Wire Jinja2 into routes

- [x] Swap JSON responses for `TemplateResponse` in each resource's router
- [x] Pass `request` + item data as context
- [x] Test rendering on an actual mobile viewport

### `app/templating.py` (shared Jinja2Templates instance)

- [x] Create standalone file so both `main.py` (static mount) and routers (rendering) can share one instance without circular imports

## Phase 4 — Admin / Write Path

### `app/resources.py` (single resource registry)

- [x] Build one list of dicts — `model`, `out_schema`, `create_schema`, `update_schema`, `url_path` — as the single source of truth per resource
- [x] `url_path` derived from `model.__tablename__` rather than typed manually
- [x] Confirm this stays a "top layer" file — imports from `db.models` and `schemas`, but nothing imports back from it (avoids circular imports)
- [x] Import from `schemas` package for each resource's `Out`/`Create`/`Update` set
- [x] Add `label_field` to each resource dict — the field name card generation displays under the QR code (e.g. `"common_name"` for a plant resource); optional per-resource since `generate_card_image()` defaults to `"common_name"` if omitted, but explicit is preferred so the registry stays self-documenting

### `routes/crud_factory.py`

- [x] Write a factory function that takes a model class and returns standard routes (list, get-by-id, create, update, delete)
- [x] Decide response/request shape the factory expects (matching each resource's `Out`/`Create`/`Update` schemas)
- [x] Keep it generic — no resource-specific logic inside the factory itself

### `routes/admin_auth.py`

- [x] Shared-secret header dependency (`require_admin_key`), reading `ADMIN_KEY` from `.env`
- [x] Kept in its own file so `crud_factory.py` can import it without a circular dependency on `admin.py`

### `routes/admin.py`

- [x] Loop `resources` (from `app/resources.py`) instead of a locally-defined registry
- [x] Call the factory per resource to register its CRUD routes
- [x] Confirm list/get/create/update/delete all work against the seeded data
- [x] Note: new models get admin CRUD for free by adding one entry to `resources.py` — no new hand-written routes needed

### Validation

- [x] Required-field checks (`slug`, primary display-name field)
- [x] Slug uniqueness check on create/edit
- [x] Decide slug generation: manual vs. auto-from-name (auto-generated from the primary name field — not yet implemented in `create`, since `slug` is still required on `Create` schemas)
- [x] Decide if admin routes need basic protection (shared-secret header via `require_admin_key`, applied to every `CrudFactory` router)
- [x] Admin form dropped — content is agent-managed, not human-entered via a form

## Phase 5 — QR + Cards

### `cards/generate_qr.py`

- [x] Decide base URL — local network IP for now, stored as `BASE_URL` in `.env` (swap to production domain later)
- [x] Decide output naming/folder convention — `cards/output/{url_path}/{slug}.png`, namespaced by resource to avoid collisions
- [x] Loop `resources` (not hardcoded to one resource) so every resource with a `slug` gets QR generation for free
- [x] Build QR payload per row (`base_url + / + url_path + / + slug`)
- [x] Write the actual generation/save logic (`qrcode.make(...)`, error correction level, box size/border for print legibility)

### `cards/generate_card.py`

- [x] Decide physical card size/format (stake/tag size, e.g. 3"×2", adjustable later)
- [x] Sketch layout (QR placement, name text) — placeholder PIL version; icon/border and HTML-template rebuild deferred
- [x] Decide font/sizing for print legibility (Pillow default font for now)
- [x] Decide single-card-per-file vs. batched print sheet/PDF (single file per card)
- [x] Refactor into `generate_card_image(row, url_path, label_field)` — one function, one card; callable in isolation, not trapped inside `if __name__ == "__main__":`
- [x] `generate_all_cards()` — orchestrator only: opens session, loops `resources`, delegates per-row to `generate_card_image()` (no duplicate logic between this and `__main__`)
- [x] Missing QR file → log and skip per row, not a crash (consistent with Phase 7's log-and-skip pattern)
- [x] Label text pulled from each resource's `label_field` (falls back to `"common_name"` if a resource doesn't define one) instead of hardcoding a specific field name — keeps the file generic across resources
- [x] `render_card_html(item, url_path)` — defined and reads from `cards/{url_path}.html` via the shared `templates` instance, but not yet wired into `generate_card_image()`; reserved for the deferred HTML-template rebuild
- [ ] Decide HTML → image/PDF renderer for the eventual template rebuild (weasyprint vs. playwright vs. imgkit) before writing `cards/*.html` templates, since layout/CSS choices depend on which renderer is used

### Batch generate + real-world test

- [x] Run card generation over seeded data
- [x] Scan a real card with a phone (same wifi network as dev server, using `BASE_URL`)
- [x] Confirm scan → correct detail page end to end

## Phase 6 — Polish for MVP

### Directory filters/search

- [ ] Decide filterable fields (start with a couple attributes relevant to the first resource, e.g. light needs, life cycle for a plant resource)
- [ ] Implement query-param filtering on each resource's directory route
- [ ] Add filter UI controls to `directory.html`

### Error handling

- [x] Invalid slug → real "not found" page
- [x] Empty catalog → friendly empty state

### `requirements.txt`

- [x] Pin versions for fastapi, sqlalchemy, alembic, jinja2, qrcode, pillow, uvicorn
- [x] Decide if dev-only tools need a separate requirements file
- [x] Add `requests` (or confirm stdlib-only) once the Ollama client HTTP approach is decided

## Phase 7 — Catalog Enrichment Agents

Everything here is category-agnostic — no file in this phase should ever
reference a specific resource or category by name. Category data lives only
in `app/agents/queues/`, one file per category; the script picks which
queue to run by which one it imports.

All Ollama calls are hand-built HTTP requests — no third-party LLM SDKs or
wrapper libraries. All parsing, validation, and orchestration logic runs
server-side in plain Python — never delegated to the LLM itself.

### `app/config.py`

- [x] Add Ollama base URL and model name(s) as config values (drafting model, review model)
- [x] Add request timeout value (seconds) for Ollama calls

### `app/agents/queues/` (category data — not shared code)

- [x] One file per category, e.g. `flowers.py` — list of item names queued for enrichment (alphabetized by sub-category, verified no duplicates/slug collisions)
- [x] Future category files (vegetables, herbs, etc.) added here the same way — one file, one list, nothing else

### `app/agents/ollama_client.py`

- [x] Decide HTTP approach: stdlib `urllib.request` vs. `requests` (`requests` is a plain HTTP library, not an LLM SDK — still counts as "building the calls yourself"; pin it in `requirements.txt` if chosen)
- [x] `call_ollama(prompt, model, ...)` — POST to `/api/generate` (or `/api/chat`), return raw text response or `None` on failure
- [x] Timeout handling — catch connection errors / timeouts, return `None` rather than raising
- [x] Keep this file dumb: no parsing, no validation, no retry logic — just "send prompt, get text back"

### `app/agents/parsing.py` (shared JSON-extraction)

- [x] `parse_json(raw)` — slice from the first `{` to the last `}` (handles markdown fences / stray preamble), then `json.loads()`; return parsed dict or `None` on `json.JSONDecodeError`
- [x] No knowledge of any resource or schema — pure string-to-dict utility, shared by both the enrichment and manager agents

### `app/agents/enrichment_agent.py` (generic — works for any category)

- [x] `run_research(item_name, model, resource)` — builds the drafting prompt, calls `call_ollama`, delegates JSON extraction to `parse_json`, returns parsed dict or `None` on failure
- [x] Prompt instructs the model to return `null` for any field it isn't confident about, rather than guess
- [x] `validate_draft(draft, schema)` — constructs `schema(**draft)` in a try/except, catches `ValidationError`, returns the validated instance or `None`; takes `schema` as a parameter so it stays resource-agnostic
- [x] `orchestrator(queue, draft_model, review_model, resource)` — loops the queue, chains `run_research` → `validate_draft` → `review_draft`, skipping (`continue`) on any `None` result; collects instances approved by the manager agent into a list and returns it after the loop completes

### `app/agents/manager_agent.py` (generic — works for any category)

- [x] `review_draft(draft, model, resource)` — builds the review prompt, calls `call_ollama` (a different model than the drafter), uses `parse_json` for extraction, returns a verdict (e.g. `{"approved": bool, "issues": [...]}`) or `None` on failure
- [x] Scope: factual plausibility only — not schema shape, which validation already covers

### `scripts/run_enrichment.py`

- [x] `queue = ` at the top, importing from a single `app/agents/queues/*.py` file — this is the only place category selection happens; swap the import to run a different category
- [x] Skip-if-exists check — before drafting, query DB for an existing row with the same slug (or derived slug from name) and skip if found, so the script is safely re-runnable and won't collide with the unique constraint
- [x] Orchestrates: loop `queue` → draft → validate → manager review → write-or-skip
- [x] On Ollama call failure (`None` returned) → log and skip, don't halt the batch
- [x] On rejection: log and skip (no auto-retry loop yet)
- [x] Decide log destination — console only, or a log file so a large run can be audited afterward

### Decisions still open

- [ ] Write path: direct DB insert vs. POST through each resource's admin route (with `X-Admin-Key`)
- [ ] Which Ollama models to use for drafting vs. review

## Repo / Tooling

- [x] `.gitignore` — secrets, venv, SQLite dev DB, IDE/OS cruft, generated card output; migrations explicitly NOT ignored
- [x] `ship.sh` — commit + push helper (add all, prompt for message, commit, push)
- [ ] `.env.example` — same keys as `.env` with placeholder values, safe to commit, documents required env vars for anyone else touching the repo (include Ollama timeout var once added to `app/config.py`)

## Parked (post-MVP)

Instance mode, on-page Q&A agent, photo diagnosis agent, personalized care agent, companion planting agent, PWA support — held until the enrichment pipeline is producing reliable catalog data.