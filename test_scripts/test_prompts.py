import json

from scripts.my_llm import generate_response
from scripts.prompts import SYSTEM_PROMPT, build_user_prompt


user_prompt = build_user_prompt(
    episode_title="The Missing Letter",
    genre="Mystery",
    platform="Instagram",
    audience="Young adults",
    tone="Suspenseful",
    episode_details=(
        "A young journalist discovers a letter hidden in an old book. "
        "The letter may be connected to a disappearance from years ago."
    ),
)

try:
    result = generate_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.7,
    )

    # Verify that the model returned valid JSON.
    content = json.loads(result)

    print("Content generated successfully!\n")
    print(json.dumps(content, indent=2, ensure_ascii=False))

except json.JSONDecodeError:
    print("The model did not return valid JSON.")
    print("Raw response:\n", result)

except RuntimeError as exc:
    print(f"Model error: {exc}")
