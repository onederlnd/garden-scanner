# scripts/run_enrichment.py
import logging
from sqlalchemy import select
from app.agents.queue.flowers import flowers
from app.agents.retry_agent import retry_draft
from app.agents.enrichment_agent import run_research, validate_draft, review_draft
from app.agents.slugify import generate_slug
from app.db.session import SessionLocal
from app.resources import resources
from app.config import settings

log_config = logging.basicConfig(filename="run_log.txt", level=logging.INFO)

queue = flowers
url_path = "plants"


def is_duplicate(db, resource, slug):
    model = resource["model"]

    result = db.execute(select(model).where(model.slug == slug)).scalar()
    if result is None:
        return False

    return True


def run_enrichment():
    session = SessionLocal()

    resource = next(r for r in resources if r["url_path"] == url_path)

    draft_model = settings.draft_model
    review_model = settings.review_model

    results = []

    for item in queue:
        slug = generate_slug(item)

        duplicate = is_duplicate(session, resource, slug)
        if duplicate:
            logging.info("SKIP: duplicate - %s", item)
            results.append((item, "duplicate"))
            continue

        record = run_research(item, draft_model, resource)
        if record is None:
            logging.warning("SKIP: research failed - %s", item)
            results.append((item, "research_failed"))
            continue

        record["slug"] = slug

        validated = validate_draft(record, resource["create_schema"])
        if validated is None:
            logging.info("SKIP: validation failed - %s", item)
            results.append((item, "validation_failed"))
            continue

        verdict = review_draft(validated, review_model, resource)
        if verdict is None:
            logging.warning("SKIP: review failed - %s", item)
            results.append((item, "review_failed"))
            continue

        if verdict["approved"] is False:
            corrected = retry_draft(
                item, validated.model_dump(), verdict["issues"], draft_model, resource
            )
            if corrected is None:
                logging.warning("SKIP: retry failed - %s", item)
                results.append((item, "retry_failed"))
                continue

            corrected["slug"] = slug

            revalidated = validate_draft(corrected, resource["create_schema"])
            if revalidated is None:
                logging.warning("SKIP: retry validation failed - %s", item)
                results.append((item, "retry_validation_failed"))
                continue

            re_verdict = review_draft(revalidated, review_model, resource)
            if re_verdict is None or re_verdict["approved"] is False:
                logging.warning("SKIP: rejected after retry - %s", item)
                results.append((item, "rejected_after_retry"))
                continue

            validated = revalidated

        results.append((item, "approved"))
        data = resource["model"](**validated.model_dump())

        session.add(data)
        session.commit()
        session.refresh(data)

    session.close()
    for item, status in results:
        print(f"{item}: {status}")

    print(
        f"\nTotal: {len(results)} |"
        f"Approved: {sum(1 for _, s in results if s == 'approved')} | "
        f"Rejected: {sum(1 for _, s in results if s == 'rejected')}"
    )


if __name__ == "__main__":
    run_enrichment()
