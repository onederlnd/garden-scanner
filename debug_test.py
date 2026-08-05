# debug_test.py
from pydantic import ValidationError
from app.agents.enrichment_agent import run_research, validate_draft
from app.agents.manager_agent import _build_review_prompt, review_draft
from app.agents.ollama_client import call_ollama
from app.resources import resources
from app.config import settings

resource = next(r for r in resources if r["url_path"] == "plants")

record = run_research("Cilantro", settings.draft_model, resource)
print("RECORD:", record)

try:
    validated = resource["create_schema"](**record)
except ValidationError as e:
    print("VALIDATION ERROR:", e)
    validated = None


prompt = _build_review_prompt(validated, resource)
print("PROMPT:", prompt)

raw = call_ollama(prompt, settings.review_model)
print("RAW REVIEW RESPONSE:", raw)
