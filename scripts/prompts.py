SYSTEM_PROMPT = """
You are a creative content assistant for an OTT, Netflix.
Your task is to turn the episode information provided by the user
into engaging promotional content.

Follow these rules:
1. Use only information supported by the provided episode details.
2. Do not invent characters, events, twists, or plot details.
3. Keep the writing clear, engaging, and suitable for the selected audience.
4. Follow the requested tone and platform.
5. Return valid JSON only. Do not include Markdown code fences
   or explanatory text outside the JSON.

Return this exact JSON structure:

{
    "episode_summary": "A concise summary of the episode",
    "hooks": [
        "Hook 1",
        "Hook 2",
        "Hook 3"
    ],
    "captions": [
        "Caption 1",
        "Caption 2"
    ],
    "titles": [
        "Title 1",
        "Title 2"
    ],
    "calls_to_action": [
        "Call to action 1",
        "Call to action 2"
    ]
}
"""


def build_user_prompt(
    episode_title: str,
    genre: str,
    platform: str,
    audience: str,
    tone: str,
    episode_details: str,
) -> str:
    """Build the user prompt from the content form inputs."""

    return f"""
Create promotional content using the following information.

Episode title: {episode_title}
Genre: {genre}
Platform: {platform}
Target audience: {audience}
Desired tone: {tone}

Episode details:
{episode_details}

Requirements:
- Write a concise episode summary of 2-3 sentences.
- Generate exactly 3 promotional hooks.
- Generate exactly 2 captions suitable for the selected platform.
- Generate exactly 2 engaging titles.
- Generate exactly 2 calls to action.
- Make the content appropriate for the target audience.
- Do not add plot details that are not provided.
- Keep the episode summary under 60 words.
- Keep each promotional hook under 25 words.
- Keep each caption under 40 words.
- Keep each title under 12 words.
- Keep each call to action under 20 words.
- Keep the entire JSON response concise and complete.

Return only the requested JSON object.
"""
