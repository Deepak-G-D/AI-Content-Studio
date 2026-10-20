import os
from dotenv import load_dotenv
import requests

load_dotenv()

#model name of the LLM
MODEL_NAME = os.getenv("MODEL")
BASE_URL = os.getenv("BASE_URL")

TIMEOUT = 300


def generate_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
) -> str:
    """Generate text using the local model in LM Studio."""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": temperature,
        "max_tokens": 1200,
        "stream": False,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Local model request failed: {exc}"
        ) from exc

    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            "LM Studio returned an unexpected response format."
        ) from exc

