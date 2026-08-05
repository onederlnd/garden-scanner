# app/agents/enrichment_agent.py

from pydantic import ValidationError
from app.agents.ollama_client import call_ollama
from app.agents.manager_agent import review_draft
from app.agents.parsing import parse_json


def _build_research_prompt(item_name, resource):
    schema = resource["create_schema"]

    field_names = list(schema.model_fields.keys())
    fields_str = ", ".join(field_names)
    instructional_prompt = f"""Return only valid JSON, no other text. Fields to include: {fields_str}. If unsure about a field, use null. For days_to_harvest, use a single number or a range like "60-90" as a quoted string — never unquoted. For other numeric fields, use a single number or null. Return spacing as a plain string, do not include extra quote characters. Only use null if you have no reasonable knowledge of that field — for well-known plants like this, most fields should be filled in with your best answer. Always include scientific_name (the Latin binomial name, e.g. "Tagetes patula") for any item you recognize — do not leave it null unless the item is truly unidentifiable."""

    item_prompt = f"""Research the following item: {item_name}"""

    return f"{instructional_prompt} {item_prompt}"


def validate_draft(draft, schema):
    try:
        data = schema(**draft)
        return data
    except ValidationError:
        return None


def run_research(item_name, model, resource):
    prompt = _build_research_prompt(item_name, resource)

    raw = call_ollama(prompt, model)
    if raw is None:
        return None

    draft = parse_json(raw)

    return draft


def orchestrator(queue, draft_model, review_model, resource):
    approved = []
    for item in queue:
        record = run_research(item, draft_model, resource)
        if record is None:
            continue

        validate = validate_draft(record, resource["create_schema"])
        if validate is None:
            continue

        review = review_draft(validate, review_model, resource)
        if review is None:
            continue

        if review["approved"]:
            approved.append(validate)
        else:
            continue

    return approved
