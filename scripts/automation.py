import os
from dotenv import load_dotenv
import requests

load_dotenv()
# Use the Test URL while your n8n workflow is listening
# for a test event.
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

TIMEOUT = 15


def send_content_to_n8n(
    episode_title,
    genre,
    platform,
    generated_content,
    generation_id,
):
    """Send a saved content generation to the n8n webhook."""

    payload = {
        "generation_id": generation_id,
        "episode_title": episode_title,
        "genre": genre,
        "platform": platform,
        "generated_content": generated_content,
    }

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return True, "Content sent to n8n successfully."

    except requests.RequestException as exc:
        return False, f"Could not send content to n8n: {exc}"
