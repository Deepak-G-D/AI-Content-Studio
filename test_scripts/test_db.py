import json

from scripts.database import (
    init_db,
    save_generation,
    get_all_generations,
    get_generation_by_id,
    delete_generation,
)


# 1. Create the database and table.
init_db()
print("Database initialized.")

# 2. Create some sample generated content.
sample_content = {
    "episode_summary": "A journalist discovers a mysterious letter.",
    "hooks": [
        "One letter changes everything.",
        "The past is not finished.",
        "A secret waits to be uncovered.",
    ],
    "captions": [
        "Every letter hides a story.",
        "Some secrets refuse to stay buried.",
    ],
    "titles": ["The Missing Letter", "Secrets in Ink"],
    "calls_to_action": ["Discover the mystery.", "Watch the story unfold."],
}

# 3. Save the sample.
generation_id = save_generation(
    episode_title="The Missing Letter",
    genre="Mystery",
    platform="Netflix",
    audience="Young adults",
    tone="Suspenseful",
    episode_details="A journalist discovers a letter in an old book.",
    generated_content=sample_content,
    generation_time=4.25,
)

print(f"Saved generation with ID: {generation_id}")

# 4. Retrieve and inspect the saved record.
record = get_generation_by_id(generation_id)

if record:
    print("\nRetrieved episode:", record["episode_title"])
    print("Generation time:", record["generation_time"], "seconds")
    print("Created at:", record["created_at"])

    content = json.loads(record["generated_content"])
    print("Number of hooks:", len(content["hooks"]))

# 5. Check the content library.
records = get_all_generations()
print("\nTotal saved generations:", len(records))

# 6. Remove the test record so it doesn't pollute your library.
if delete_generation(generation_id):
    print("Test record deleted.")
