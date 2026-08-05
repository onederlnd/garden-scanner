# app/agents/ollama_client.py
import requests
from app.config import settings


def call_ollama(prompt, model):
    try:
        response = requests.post(
            f"{settings.ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.RequestException:
        return None

    data = response.json()
    return data.get("response")
