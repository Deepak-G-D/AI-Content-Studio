import requests
from dotenv import load_dotenv
import os

load_dotenv()

WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

payload = {
    "episode_title": "The Missing Letter",
    "episode_summary": (
        "A journalist discovers a mysterious letter "
        "that may explain an old disappearance."
    ),
    "hooks": [
        "One letter changes everything.",
        "Some secrets refuse to stay buried.",
        "The truth is closer than it seems."
    ]
}

try:
    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=15,
    )

    print("Status code:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()
    print("Webhook test successful!")

except requests.RequestException as exc:
    print("Webhook test failed:", exc)
