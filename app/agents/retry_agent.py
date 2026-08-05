# app/agents/retry_agent.py

from app.agents.ollama_client import call_ollama
from app.agents.parsing import parse_json


def _build_retry_prompt(item_name, draft, issues, resource):
    schema = resource["create_schema"]

    field_names = list(schema.model_fields.keys())
    fields_str = ", ".join(field_names)

    field_format_rules = """If unsure about a field, use null. For days_to_harvest, use a single number or a range like "60-90" as a quoted string — never unquoted. For other numeric fields, use a single number or null. Return spacing as a plain string, do not include extra quote characters. Only use null if you have no reasonable knowledge of that field — for well-known items like this, most fields should be filled in with your best answer. Always include scientific_name (the Latin binomial name, e.g. "Tagetes patula") for any item you recognize — do not leave it null unless the item is truly unidentifiable."""
    instructional_prompt = f"""Return only valid JSON, no other text. Fields to include: {fields_str}. {field_format_rules}"""
    context_prompt = f"""Previous draft: {draft}. Issues found: {issues}"""

    return f"{instructional_prompt} {context_prompt}"


def retry_draft(item_name, draft, issues, model, resource):
    prompt = _build_retry_prompt(item_name, draft, issues, resource)

    raw = call_ollama(prompt, model)
    if raw is None:
        return None

    corrected = parse_json(raw)
    return corrected
