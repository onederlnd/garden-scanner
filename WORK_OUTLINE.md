# Work Outline

## Phase 1 — Data Layer

### `db/session.py` (engine, session, connection plumbing)

- [x] Set up engine
- [x] Decide where `DATABASE_URL` lives (env var vs. hardcoded)
- [x] Create the `sessionmaker`
- [x] Write the `get_db()` dependency generator

### `db/base.py` (shared declarative base)

- [x] Define `Base` — nothing else goes in this file

### `db/models/plant.py`

- [x] Import `Base` from `db/base.py`
- [x] Define the `Plant` model with all fields from the data model
- [x] Decide nullable vs. required per field (`slug`, `common_name` required; care fields nullable)
- [x] Add unique constraint + index on `slug`
- [x] Optional: add `__repr__` for debugging

### `db/models/__init__.py` (registry)

- [x] Import and re-export `Plant` (and every future model, so Alembic and the app can import from one place)

### Initialize Alembic

- [x] Run Alembic init to scaffold `alembic/`
- [x] Point `alembic.ini`'s `sqlalchemy.url` at the dev database
- [x] Import `Base` (via `db.models`) into `env.py`, set `target_metadata`
- [x] Confirm autogenerate can detect the `Plant` model

### First migration

- [x] Generate migration with `--autogenerate`
- [x] Review generated migration file before applying
- [x] Apply migration (`alembic upgrade head`)
- [x] Confirm table exists in the database

### Seed test plants

- [x] Decide seeding method (script vs. fixtures file)
- [x] Pick 4–5 plants with varied care needs
- [x] Fill in every field for each seeded plant (real care data written for all six)
- [x] Decide if seed script is re-runnable or one-time

## Phase 2 — Routes

### `routes/plants/schema.py`

- [x] `PlantOut` — all fields, `Optional` for nullable ones, `from_attributes=True` config
- [x] `PlantCreate` — same as `PlantOut` minus `id`
- [x] `PlantUpdate` — partial update, all fields optional with `= None` defaults

### `routes/plants/router.py`

- [x] Set up `APIRouter`
- [x] Directory route: query all plants, return list of `PlantOut`
- [x] Detail route: query by slug, return `PlantOut`
- [x] Handle not-found case (404) on detail route

### `routes/plants/__init__.py`

- [x] Re-export the router (e.g. `from routes.plants.router import router`)

### `routes/__init__.py` (registry)

- [x] Import the plants router (and every future resource's router)
- [x] Expose a collection `main.py` can loop over to `include_router()` each one

### `main.py`

- [x] Instantiate FastAPI app
- [x] Decide: keep `create_all()` as dev convenience, or Alembic-only (Alembic-only)
- [x] Loop the routes registry, `include_router()` each
- [x] Run dev server, confirm both routes return seeded data as JSON

## Phase 3 — Templates

### `templates/plant_detail.html`

- [x] Register `Jinja2Templates` pointed at `templates/`
- [x] Sketch page structure (header, growing conditions, care, timing, issues, notes)
- [x] Mobile-first layout: single column, large type
- [x] Handle null fields gracefully (skip row, don't show blank label)

### `templates/directory.html`

- [x] List all plants with name + link to detail page
- [x] Decide list vs. card-grid layout
- [x] Leave placeholder space for Phase 6 filter UI

### Wire Jinja2 into routes

- [x] Swap JSON responses for `TemplateResponse` in `routes/plants/router.py`
- [x] Pass `request` + plant data as context
- [x] Test rendering on an actual mobile viewport

### `app/templating.py` (shared Jinja2Templates instance)

- [x] Create standalone file so both `main.py` (static mount) and `router.py` (rendering) can share one instance without circular imports

## Phase 4 — Admin / Write Path

### `app/resources.py` (single resource registry)

- [x] Build one list of dicts — `model`, `out_schema`, `create_schema`, `update_schema`, `url_path` — as the single source of truth per resource
- [x] `url_path` derived from `model.__tablename__` rather than typed manually
- [x] Confirm this stays a "top layer" file — imports from `db.models` and `routes.plants.schema`, but nothing imports back from it (avoids circular imports)

### `routes/crud_factory.py`

- [x] Write a factory function that takes a model class and returns standard routes (list, get-by-id, create, update, delete)
- [x] Decide response/request shape the factory expects (matching each resource's `Out`/`Create`/`Update` schemas)
- [x] Keep it generic — no `Plant`-specific logic inside the factory itself

### `routes/admin_auth.py`

- [x] Shared-secret header dependency (`require_admin_key`), reading `ADMIN_KEY` from `.env`
- [x] Kept in its own file so `crud_factory.py` can import it without a circular dependency on `admin.py`

### `routes/admin.py`

- [x] Loop `resources` (from `app/resources.py`) instead of a locally-defined registry
- [x] Call the factory per resource to register its CRUD routes
- [x] Confirm list/get/create/update/delete all work against the seeded data
- [x] Note: new models get admin CRUD for free by adding one entry to `resources.py` — no new hand-written routes needed

### Validation

- [x] Required-field checks (`slug`, `common_name`)
- [x] Slug uniqueness check on create/edit
- [x] Decide slug generation: manual vs. auto-from-name (auto-generated from `common_name` — not yet implemented in `create`, since `slug` is still required on `PlantCreate`)
- [x] Decide if admin routes need basic protection (shared-secret header via `require_admin_key`, applied to every `CrudFactory` router)

## Phase 5 — QR + Cards

### `cards/generate_qr.py`

- [x] Decide base URL — local network IP for now, stored as `BASE_URL` in `.env` (swap to production domain later)
- [x] Decide output naming/folder convention — `cards/output/{url_path}/{slug}.png`, namespaced by resource to avoid collisions
- [x] Loop `resources` (not hardcoded to `Plant`) so future resources with a `slug` get QR generation for free
- [x] Build QR payload per row (`base_url + / + url_path + / + slug`)
- [x] Write the actual generation/save logic (`qrcode.make(...)`, error correction level, box size/border for print legibility)

### `cards/generate_card.py`

- [x] Decide physical card size/format (stake/tag size, e.g. 3"×2", adjustable later)
- [x] Sketch layout (QR placement, name text, icon/border)
- [x] Decide font/sizing for print legibility
- [x] Decide single-card-per-file vs. batched print sheet/PDF

### Batch generate + real-world test

- [x] Run card generation over seeded plants
- [x] Scan a real card with a phone (same wifi network as dev server, using `BASE_URL`)
- [x] Confirm scan → correct detail page end to end

## Phase 6 — Polish for MVP

### Directory filters/search

- [ ] Decide filterable fields (start with light needs, life cycle)
- [ ] Implement query-param filtering on `/plants`
- [ ] Add filter UI controls to `directory.html`

### Error handling

- [ ] Invalid slug → real "not found" page
- [ ] Empty catalog → friendly empty state
- [ ] Admin form → inline validation errors

### `requirements.txt`

- [x] Pin versions for fastapi, sqlalchemy, alembic, jinja2, qrcode, pillow, uvicorn
- [x] Decide if dev-only tools need a separate requirements file

### Deploy target decision

- [ ] Pick app hosting
- [ ] Pick database hosting (managed Postgres recommended)
- [ ] Finalize production domain before first real print run (replaces local `BASE_URL` — every printed QR code depends on this being final)

## Repo / Tooling

- [x] `.gitignore` — secrets, venv, SQLite dev DB, IDE/OS cruft, generated card output; migrations explicitly NOT ignored
- [x] `ship.sh` — commit + push helper (add all, prompt for message, commit, push)
- [ ] `.env.example` — same keys as `.env` with placeholder values, safe to commit, documents required env vars for anyone else touching the repo

## Parked (post-MVP)

Instance mode, agents (catalog enrichment agent will fill in the placeholder seed data), PWA support — held until scan → accurate info works end to end.
