# Gardener Plant Info

A QR-code-driven plant reference for gardeners. Printed cards carry a QR code
per plant/variety; scanning one opens a mobile-friendly page with care info —
life cycle, light needs, pH, watering, spacing, planting season, and more.

## Concept

1. Each plant/variety has a record in the catalog (name, care details, etc.)
2. A QR code is generated per plant, encoding a URL like `/plant/roma-tomato`
3. The QR code is printed on a physical card (stake tag, seed packet insert, etc.)
4. Scanning the code opens a lightweight web page rendering that plant's info

No native app is required for this — the QR code just points to a web page, so any phone camera can scan it and open the page in a browser. A PWA layer (add-to-home-screen, offline caching) is a possible later enhancement; see Roadmap. A true native/mobile app was considered and set aside for now in favor of this simpler web-based approach.

## Why this approach

- **No install friction** — gardeners scan and see info immediately, no app store, no download.
- **One codebase** — a single web app serves everyone, regardless of phone
  OS.
- **Cheap to update** — care info can be corrected or expanded without
  reprinting cards, since the QR code always points to the same URL.
- **Print-agnostic** — the same catalog can back multiple card formats
  (stakes, seed packet inserts, signage) without changing the backend.

## Tech Stack

- **Backend:** FastAPI
- **ORM:** SQLAlchemy (sync, with `sessionmaker`/`declarative_base`)
- **Migrations:** Alembic
- **Templates:** Jinja2 (server-rendered HTML, mobile-first)
- **Database:** SQLite (dev) / Postgres (prod)
- **QR generation:** `qrcode` package
- **Card layout:** Pillow (image cards) or ReportLab (print-ready PDFs)

## Project Structure

```bash
app/
├── main.py              # FastAPI app entrypoint
├── routes/
│   ├── plants.py        # Plant detail + directory routes
│   ├── crud_factory.py  # Generic CRUD route factory, called per model
│   └── admin.py         # Registers CRUD factory for each model
├── templates/
│   ├── plant_detail.html
│   └── directory.html
├── static/
│   └── ...
├── cards/
│   ├── generate_qr.py   # QR code generation per plant
│   └── generate_card.py # Card layout/export for printing
├── db/
│   ├── session.py        # Engine, sessionmaker, get_db()
│   ├── base.py            # Shared declarative Base
│   └── models/
│       ├── __init__.py    # Registry — re-exports every model
│       └── plant.py       # Plant model
└── alembic/
    ├── env.py            # Alembic migration environment
    └── versions/         # generated migration scripts
```

## Data Model (MVP)

**Plant / Variety**

- `id` — primary key
- `slug` — used in the QR/detail page URL (e.g. `roma-tomato`)
- `common_name`, `scientific_name`
- `life_cycle` — annual / biennial / perennial
- `light_needs`
- `ph_min`, `ph_max`
- `soil_type`
- `watering_frequency`
- `spacing`
- `planting_season`
- `days_to_harvest`
- `common_pests`, `common_diseases`
- `notes`

This model favors the **catalog** approach (see Open Questions) — one row
per species/variety, shared across every printed card of that plant. If the
**instance** model is adopted later, a separate `garden_plants` table would
track a specific gardener's specific plant (tied to a user and a planting
date), referencing this catalog rather than replacing it.

## Features

### Core (MVP)

- [ ] Plant catalog (CRUD)
- [ ] QR code generation per plant, linked to detail page URL
- [ ] Mobile-friendly plant detail page
- [ ] Printable card generator (QR + name + quick-glance icon)
- [ ] Basic admin entry flow for adding/editing plants

### Near-term

- [ ] Searchable/browsable plant directory
- [ ] Filters (light needs, difficulty, category, indoor/outdoor)
- [ ] Companion planting / "similar plants" suggestions
- [ ] Regional planting windows (hardiness zone aware)
- [ ] Multiple card templates/sizes for different print stock

### Instance mode (optional direction)

- [ ] User accounts
- [ ] "My garden" — plants a user owns, tied to their own QR tags
- [ ] Planting date, watering log, photo history
- [ ] Reminders (watering, fertilizing, harvest window)

### Later / nice-to-have

- [ ] PWA support (offline caching, add-to-home-screen)
- [ ] Multi-language pages
- [ ] Community-contributed corrections/data
- [ ] Weather integration (local conditions → care flags)
- [ ] Scan analytics (which plants/cards get scanned most)

## Agents (Upcoming)

Potential agent-assisted features to layer in after the core MVP is stable:

- **Catalog enrichment agent** — researches a plant and drafts a catalog
  record (light needs, pH, watering, pests, etc.) for human review before
  publishing. Speeds up populating the catalog; not intended to auto-publish
  unreviewed care info.
- **On-page Q&A agent** — a "ask about this plant" box on the detail page,
  grounded in that plant's catalog record, for follow-up questions beyond
  the static fields.
- **Photo diagnosis agent** — gardener uploads a photo of a struggling
  plant; agent suggests likely pests/diseases/deficiencies, referencing that
  species' known issues.
- **Personalized care agent** (depends on instance mode) — given a
  gardener's logged plants, zone, and planting dates, proactively suggests
  care actions (watering, fertilizing, harvest timing).
- **Companion planting / layout agent** — reasons over the catalog to
  suggest planting layouts or companion plants for a given set of plants.

Simple lookups/filters (e.g. "show plants that need full sun") stay as
plain queries rather than agent calls — agents are reserved for tasks that
need research, reasoning, or open-ended interpretation.

## Open Questions

- **Catalog vs. instance model:** are QR codes tied to a species/variety
  (static, shared across all cards of that plant) or to an individual
  gardener's specific plant (dynamic, needs accounts)? This affects the
  schema significantly — decide before scaling past MVP.
- **Card distribution:** self-printed and bundled with seeds, sold
  standalone, or user-generated on demand?
- **Pest/disease data:** flat text fields for now, or normalize into their
  own tables later to support structured filtering (e.g. "show all plants
  vulnerable to aphids")?

## Setup

```bash
# clone and enter the repo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# apply migrations
alembic upgrade head

# run the dev server
uvicorn app.main:app --reload
```

To generate a new migration after changing `models.py`:

```bash
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

## Roadmap

1. Finalize catalog data model and seed it with an initial set of plants
2. Build plant detail page + directory
3. Add QR generation tied to each plant's slug
4. Build card layout/export for printing
5. Decide on catalog vs. instance model before adding user accounts
6. Evaluate PWA support once the core flow is stable

## License

TBD
