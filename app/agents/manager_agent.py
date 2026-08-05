# app/agents/manager_agent.py

from app.agents.ollama_client import call_ollama
from app.agents.parsing import parse_json


def _build_review_prompt(draft, resource):
    schema = resource["create_schema"]

    field_names = list(schema.model_fields.keys())
    fields_str = ", ".join(field_names)

    instructional_prompt = f"""Review the following {fields_str} data for factual accuracy only.

    Rules:
    1. IGNORE any field that is null or missing. Do not mention it, do not list it as an issue, do not let it affect your decision. A separate process fills those in later.
    2. ONLY flag a field if it contains a value that is factually wrong.
    3. If every filled-in field is accurate, set "approved" to true, even if many fields are null.
    4. Your "issues" list must contain zero mentions of missing, null, or empty fields — only factual errors in fields that have a value.

    Return only JSON with keys 'approved' (true/false) and 'issues' (a list of strings, factual errors only)."""

    item_prompt = f"""Data to review: {draft.model_dump()}"""

    return f"{instructional_prompt} {item_prompt}"


def review_draft(draft, model, resource):
    prompt = _build_review_prompt(draft, resource)

    raw = call_ollama(prompt, model)
    if raw is None:
        return None

    verdict = parse_json(raw)
    return verdict
