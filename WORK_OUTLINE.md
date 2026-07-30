# Work Outline

## Phase 1 — Data Layer

### `db/session.py` (engine, session, connection plumbing)

- [ ] Set up engine
- [ ] Decide where `DATABASE_URL` lives (env var vs. hardcoded)
- [ ] Create the `sessionmaker`
- [ ] Write the `get_db()` dependency generator

### `db/base.py` (shared declarative base)

- [x] Define `Base` — nothing else goes in this file

### `db/models/plant.py`

- [x] Import `Base` from `db/base.py`
- [ ] Define the `Plant` model with all fields from the data model
- [ ] Decide nullable vs. required per field (`slug`, `common_name` required; care fields nullable)
- [ ] Add unique constraint + index on `slug`
- [ ] Optional: add `__repr__` for debugging

### `db/models/__init__.py` (registry)

- [ ] Import and re-export `Plant` (and every future model, so Alembic and the app can import from one place)

### Initialize Alembic

- [ ] Run Alembic init to scaffold `alembic/`
- [ ] Point `alembic.ini`'s `sqlalchemy.url` at the dev database
- [ ] Import `Base` (via `db.models`) into `env.py`, set `target_metadata`
- [ ] Confirm autogenerate can detect the `Plant` model

### First migration

- [ ] Generate migration with `--autogenerate`
- [ ] Review generated migration file before applying
- [ ] Apply migration (`alembic upgrade head`)
- [ ] Confirm table exists in the database

### Seed test plants

- [ ] Decide seeding method (script vs. fixtures file)
- [ ] Pick 4–5 plants with varied care needs
- [ ] Fill in every field for each seeded plant
- [ ] Decide if seed script is re-runnable or one-time

## Phase 2 — Routes (read path)

### `routes/plants.py`

- [ ] Set up `APIRouter`
- [ ] Directory route: query all plants
- [ ] Decide response shape (raw dicts vs. Pydantic schema)
- [ ] Detail route: query by slug
- [ ] Handle not-found case (404) on detail route
- [ ] Sketch `PlantOut` schema (and `PlantCreate`/`PlantUpdate` needs for Phase 4)

### `main.py`

- [ ] Instantiate FastAPI app
- [ ] Decide: keep `create_all()` as dev convenience, or Alembic-only
- [ ] Include the plants router
- [ ] Run dev server, confirm both routes return seeded data as JSON

## Phase 3 — Templates

### `templates/plant_detail.html`

- [ ] Register `Jinja2Templates` pointed at `templates/`
- [ ] Sketch page structure (header, growing conditions, care, timing, issues, notes)
- [ ] Mobile-first layout: single column, large type
- [ ] Handle null fields gracefully (skip row, don't show blank label)

### `templates/directory.html`

- [ ] List all plants with name + link to detail page
- [ ] Decide list vs. card-grid layout
- [ ] Leave placeholder space for Phase 6 filter UI

### Wire Jinja2 into routes

- [ ] Swap JSON responses for `TemplateResponse` in `plants.py`
- [ ] Pass `request` + plant data as context
- [ ] Test rendering on an actual mobile viewport

## Phase 4 — Admin / Write Path

### `routes/crud_factory.py`

- [ ] Write a factory function that takes a model class and returns standard routes (list, get-by-id, create, update, delete)
- [ ] Decide response/request shape the factory expects (e.g. matching `PlantOut`/`PlantCreate`/`PlantUpdate` schemas per model)
- [ ] Keep it generic — no `Plant`-specific logic inside the factory itself

### `routes/admin.py`

- [ ] Call the factory for `Plant` to register its CRUD routes
- [ ] Confirm list/get/create/update/delete all work against the seeded data
- [ ] Note: new models get admin CRUD for free by calling the factory again — no new hand-written routes needed

### Validation

- [ ] Required-field checks (`slug`, `common_name`)
- [ ] Slug uniqueness check on create/edit
- [ ] Decide slug generation: manual vs. auto-from-name
- [ ] Decide if admin routes need basic protection

## Phase 5 — QR + Cards

### `cards/generate_qr.py`

- [ ] Decide base URL (dev vs. eventual production — baked into every printed code)
- [ ] Build QR payload per plant (`base_url + /plant/ + slug`)
- [ ] Decide output naming/folder convention

### `cards/generate_card.py`

- [ ] Decide physical card size/format
- [ ] Sketch layout (QR placement, name text, icon/border)
- [ ] Decide font/sizing for print legibility
- [ ] Decide single-card-per-file vs. batched print sheet/PDF

### Batch generate + real-world test

- [ ] Run card generation over seeded plants
- [ ] Scan a real card with a phone (may need network-accessible dev server)
- [ ] Confirm scan → correct detail page end to end

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
- [ ] Finalize production domain before first real print run

## Parked (post-MVP)

Instance mode, agents, PWA support — held until scan → accurate info works end to end.
