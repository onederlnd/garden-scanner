# Gardener Plant Info

A QR-code-driven plant reference for gardeners. Printed cards carry a QR code
per plant/variety; scanning one opens a mobile-friendly page with care info —
life cycle, light needs, pH, watering, spacing, planting season, and more.

## Concept

1. Each plant/variety has a record in the catalog (name, care details, etc.)
2. A QR code is generated per plant, encoding a URL like `/plants/roma-tomato`
3. The QR code is printed on a physical card (stake tag, seed packet insert, etc.)
4. Scanning the code opens a lightweight web page rendering that plant's info

No native app is required for this — the QR code just points to a web page, so any phone camera can scan it and open the page in a browser. A PWA layer (add-to-home-screen, offline caching) is a possible later enhancement; see Roadmap. A true native/mobile app was considered and set aside for now in favor of this simpler web-based approach.

## Status

Core MVP loop is working end to end: catalog → QR generation → printed card → phone scan → rendered detail page. Catalog enrichment (draft → validate → review → retry → write) is built and has been run against the full 206-item flowers queue, plus a personal reference queue. Card generation has been rebuilt as an HTML/CSS template rendered via WeasyPrint, replacing the earlier Pillow placeholder.

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
- **Card layout:** HTML/CSS template rendered to PDF via WeasyPrint
- **Local LLM agents:** Ollama — `llama3.1:8b` for drafting, `deepseek-r1:14b` for review (swapped from `llama3.1:70b`, which exceeded available system RAM)

## Project Structure

```bash
app/
├── main.py                     # FastAPI app entrypoint
├── config.py                    # Centralized env var loading (DATABASE_URL, ADMIN_KEY, BASE_URL, Ollama models/timeout, etc.)
├── resources.py                  # Single resource registry — model + schemas + url_path + label_field per resource
├── templating.py                  # Shared Jinja2Templates instance
├── routes/
│   ├── admin.py                    # Registers CRUD factory per resource
│   ├── admin_auth.py                 # Shared-secret admin route protection
│   ├── crud_factory.py                # Generic CRUD route factory, called per model
│   └── plants/
│       ├── router.py                   # Plant detail + directory routes
│       ├── schema.py                    # PlantOut / PlantCreate / PlantUpdate
│       └── __init__.py
├── templates/
│   ├── base.html
│   ├── plant_detail.html
│   ├── directory.html
│   ├── not_found.html
│   └── cards/
│       └── plants.html                 # HTML card template (QR + name/scientific name/care info), rendered via WeasyPrint
├── static/
│   └── css/style.css
├── cards/
│   ├── generate_qr.py                 # QR code generation per resource row
│   └── generate_card.py                # Renders cards/{url_path}.html per row via WeasyPrint, writes PDF
├── agents/
│   ├── queue/
│   │   ├── flowers.py                    # 206 flower names queued for enrichment
│   │   └── christenhusz.py                # Personal reference queue (vegetables/herbs mix)
│   ├── ollama_client.py                  # Dumb HTTP client — call_ollama(prompt, model), no parsing/validation
│   ├── parsing.py                        # Shared JSON extraction (parse_json) — used by enrichment, manager, retry agents
│   ├── enrichment_agent.py                # Drafts a PlantCreate-shaped record via Ollama; validate_draft(); shared FIELD_FORMAT_RULES
│   ├── manager_agent.py                    # Reviews a drafted record, returns verdict + issues
│   ├── retry_agent.py                       # Re-drafts only the fields a rejected record got wrong, given the reviewer's issues
│   └── slugify.py                           # generate_slug(name) — deterministic slug generation, used instead of trusting the LLM's own slug field
├── db/
│   ├── session.py                  # Engine, sessionmaker, get_db()
│   ├── base.py                      # Shared declarative Base
│   └── models/
│       ├── __init__.py                # Registry — re-exports every model
│       └── plants.py                   # Plant model
└── alembic/
    ├── env.py                      # Alembic migration environment
    └── versions/                     # generated migration scripts

scripts/
└── run_enrichment.py              # Orchestrates the full pipeline: skip-if-duplicate → draft → validate → review → retry-on-rejection → write; console + file (run_log.txt) logging
```

## Data Model (MVP)

**Plant / Variety**

- `id` — primary key (UUID)
- `slug` — used in the QR/detail page URL (e.g. `roma-tomato`); always generated deterministically via `slugify.generate_slug()`, never trusted from the LLM's own drafted output
- `common_name`, `scientific_name`
- `life_cycle` — annual / biennial / perennial
- `light_needs`
- `ph_min`, `ph_max`
- `soil_type`
- `watering_frequency`
- `spacing` — string (e.g. `"12-18 inches"`), not numeric
- `planting_season`
- `days_to_harvest` — string, since this can be a single number or a range (e.g. `"60-90"`)
- `common_pests`, `common_diseases`
- `notes`

This model favors the **catalog** approach (see Open Questions) — one row
per species/variety, shared across every printed card of that plant. If the
**instance** model is adopted later, a separate `garden_plants` table would
track a specific gardener's specific plant (tied to a user and a planting
date), referencing this catalog rather than replacing it.

## Features

### Core (MVP) — done

- [x] Plant catalog (CRUD, via generic factory)
- [x] QR code generation per plant, linked to detail page URL
- [x] Mobile-friendly plant detail page
- [x] Printable card generator — HTML/CSS template, rendered to PDF via WeasyPrint (QR + name + scientific name + light/water/soil info)
- [x] Admin write path (API-only, shared-secret protected — no human-facing form; content is agent-managed)
- [x] Catalog enrichment pipeline (draft → validate → review → retry → write), run against the full flowers queue and a personal reference queue

### Near-term

- [ ] Searchable/browsable plant directory (filters in progress)
- [ ] Filters (light needs, life cycle to start)
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

## Agents

### Catalog enrichment

Draft → validate → review → retry pattern, running locally via Ollama:

- **Enrichment agent** (`enrichment_agent.py`) — given an item name, drafts a `PlantCreate`-shaped record. Prompted to return `null` only when genuinely unsure, use quoted strings (not bare numbers) for fields like `spacing`/`days_to_harvest`, and always include `scientific_name` for recognizable items. These format rules live in a shared `FIELD_FORMAT_RULES` constant, reused by the retry agent's prompt too.
- **Shared JSON parsing** (`parsing.py`) — `parse_json()` strips markdown fences/preamble and handles `JSONDecodeError`, shared by the enrichment, manager, and retry agents so the extraction logic isn't duplicated.
- **Schema validation** — the drafted record is validated against `PlantCreate` in plain code (fast, deterministic) before it ever reaches the manager agent. The record's `slug` is overwritten with the deterministically-generated one (`slugify.generate_slug()`) before validation, rather than trusting whatever the LLM drafted for that field.
- **Manager agent** (`manager_agent.py`) — a separate review pass using a different local model than the drafter (`deepseek-r1:14b` vs. `llama3.1:8b`), to avoid a model rubber-stamping its own output. Judges factual plausibility only — not schema shape, which is already handled by validation. The review prompt explicitly instructs the model to ignore missing/null fields entirely and only flag genuine factual errors in filled-in fields, since early runs had a near-100% rejection rate driven mostly by "this field is missing" complaints rather than real inaccuracies.
- **Retry agent** (`retry_agent.py`) — on rejection, re-drafts the record given the original draft and the reviewer's specific issues, asking the model to correct only the flagged fields. The corrected record is re-validated and re-reviewed once; a second rejection is logged and skipped (no further retries).
- **Orchestration** (`scripts/run_enrichment.py`) — a single category (queue file) is imported at the top; skip-if-exists check against the DB happens before drafting so re-running the script is safe; results are tracked per item (duplicate / research_failed / validation_failed / rejected_after_retry / approved) and logged to both console and `run_log.txt`.
- Currently run against `flowers` (206 items) and a personal reference queue (`christenhusz.py`).

### Upcoming

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
- **Gap-filling agent** (proposed) — a focused follow-up pass specifically targeting `None` fields on already-approved records, rather than relying solely on the initial draft to fill everything. Not yet built.

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

### Resolved

- **Enrichment write path:** direct DB insert (via SQLAlchemy session in `run_enrichment.py`), not routed through the admin API.
- **Ollama models:** `llama3.1:8b` for drafting, `deepseek-r1:14b` for review — chosen over `llama3.1:70b` after that model's memory requirement (34+ GiB over available RAM) made it unusable locally.

## Setup

```bash
# clone and enter the repo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# apply migrations
alembic upgrade head

# run the dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

To generate a new migration after changing a model:

```bash
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

To generate QR codes and printable cards for the current catalog:

```bash
python -m app.cards.generate_qr
python -m app.cards.generate_card
```

To run catalog enrichment (edit `queue`/`url_path` at the top of the script to change category):

```bash
python3 -m scripts.run_enrichment
```

## Roadmap

1. ~~Finalize catalog data model and seed it with an initial set of plants~~
2. ~~Build plant detail page + directory~~
3. ~~Add QR generation tied to each plant's slug~~
4. ~~Build card layout/export for printing~~
5. ~~Build catalog enrichment + manager agents, populate flowers~~
6. Directory filters/search
7. ~~Rebuild card layout as HTML template~~
8. Decide on catalog vs. instance model before adding user accounts
9. Evaluate PWA support once the core flow is stable
10. Build a gap-filling agent for fields still left `null` after enrichment

## License

MIT License

Copyright (c) 2026 Randy Christenhusz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
