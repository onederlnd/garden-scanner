# app/agents/parsing.py
import json


def parse_json(draft):
    start = draft.find("{")
    end = draft.rfind("}")
    if start == -1 or end == -1:
        return None

    stripped = draft[start : end + 1]

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None

    return parsed
