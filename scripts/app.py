import json
import time
import pandas as pd
import streamlit as st
from scripts.automation import send_content_to_n8n
from scripts.my_llm import generate_response
from scripts.prompts import SYSTEM_PROMPT, build_user_prompt
from scripts.database import (
    init_db,
    save_generation,
    get_all_generations,
    get_generation_by_id,
    delete_generation,
)


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✍️",
    layout="wide",
)

# Ensure the database and table exist.
init_db()


# -----------------------------
# Helper functions
# -----------------------------

def parse_generated_content(response):
    """Convert the model's JSON response into a Python dictionary."""

    # Handle models that wrap JSON in Markdown code fences.
    cleaned = response.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines)

    try:
        content = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned invalid JSON: {exc}\n\n"
            f"Raw response:\n{cleaned}"
        ) from exc

    if not isinstance(content, dict):
        raise ValueError("The model response must be a JSON object.")

    required_fields = [
        "episode_summary",
        "hooks",
        "captions",
        "titles",
        "calls_to_action",
    ]

    for field in required_fields:
        if field not in content:
            raise ValueError(f"Missing required field: {field}")

    return content


def display_content(content):
    """Display generated content in organized sections."""

    st.subheader("Episode Summary")
    st.write(content["episode_summary"])

    sections = [
        ("Promotional Hooks", "hooks"),
        ("Captions", "captions"),
        ("Titles", "titles"),
        ("Calls to Action", "calls_to_action"),
    ]

    for heading, key in sections:
        st.subheader(heading)

        for index, item in enumerate(content[key], start=1):
            st.markdown(f"**Option {index}**")
            st.write(item)


# -----------------------------
# Sidebar navigation
# -----------------------------

st.sidebar.title("✍️ AI Content Studio")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Generate Content", "Content Library"],
)

st.sidebar.divider()
st.sidebar.caption("Powered by a local LLM, Python and SQLite")


# -----------------------------
# Dashboard
# -----------------------------

if page == "Dashboard":
    st.title("Content Dashboard")
    st.write("An overview of your AI-generated promotional content.")

    records = get_all_generations()

    total_generations = len(records)

    if total_generations:
        average_time = sum(
            record["generation_time"] or 0
            for record in records
        ) / total_generations

        unique_genres = len({
            record["genre"]
            for record in records
            if record["genre"]
        })

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Generations", total_generations)
        col2.metric("Average Generation Time", f"{average_time:.2f} sec")
        col3.metric("Unique Genres", unique_genres)

        st.subheader("Generations by Genre")

        genre_df = pd.DataFrame(records)
        genre_counts = (
            genre_df["genre"]
            .fillna("Unspecified")
            .value_counts()
            .rename_axis("Genre")
            .reset_index(name="Generations")
        )

        st.bar_chart(
            genre_counts,
            x="Genre",
            y="Generations",
        )

        st.subheader("Recent Generations")

        recent_df = pd.DataFrame(records[:5])

        st.dataframe(
            recent_df[
                [
                    "id",
                    "episode_title",
                    "genre",
                    "platform",
                    "created_at",
                    "generation_time",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "No content has been generated yet. "
            "Go to Generate Content to create your first result."
        )


# -----------------------------
# Generate Content
# -----------------------------

elif page == "Generate Content":
    st.title("Generate Promotional Content")

    st.write(
        "Enter your episode details and let your local AI model "
        "create promotional content."
    )

    with st.form("content_generation_form"):
        episode_title = st.text_input(
            "Episode Title",
            placeholder="e.g. The Missing Letter",
        )

        col1, col2 = st.columns(2)

        with col1:
            genre = st.selectbox(
                "Genre",
                [
                    "Mystery",
                    "Romance",
                    "Drama",
                    "Thriller",
                    "Comedy",
                    "Fantasy",
                    "Other",
                ],
            )

            platform = st.selectbox(
                "Platform",
                [
                    "Netflix",
                    "Instagram",
                    "YouTube",
                    "TikTok",
                    "Other",
                ],
            )

            audience = st.selectbox(
                "Target Audience",
                [
                    "Young adults",
                    "Adults",
                    "Teenagers",
                    "General audience",
                ],
            )

        with col2:
            tone = st.selectbox(
                "Desired Tone",
                [
                    "Suspenseful",
                    "Emotional",
                    "Humorous",
                    "Romantic",
                    "Dramatic",
                    "Informative",
                ],
            )

        episode_details = st.text_area(
            "Episode Details",
            placeholder=(
                "Describe the episode, its characters, "
                "and the main events..."
            ),
            height=180,
        )

        submitted = st.form_submit_button(
            "Generate Content",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not episode_title.strip() or not episode_details.strip():
            st.warning(
                "Please enter both an episode title and episode details."
            )

        else:
            user_prompt = build_user_prompt(
                episode_title=episode_title.strip(),
                genre=genre,
                platform=platform,
                audience=audience,
                tone=tone,
                episode_details=episode_details.strip(),
            )

            try:
                with st.spinner(
                    "Generating content with your local AI model..."
                ):
                    start_time = time.perf_counter()

                    response = generate_response(
                        system_prompt=SYSTEM_PROMPT,
                        user_prompt=user_prompt,
                        temperature=0.7,
                    )

                    generation_time = (
                        time.perf_counter() - start_time
                    )

                    content = parse_generated_content(response)

                # Save only after the response passes JSON validation.
                generation_id = save_generation(
                    episode_title=episode_title.strip(),
                    genre=genre,
                    platform=platform,
                    audience=audience,
                    tone=tone,
                    episode_details=episode_details.strip(),
                    generated_content=content,
                    generation_time=generation_time,
                )

                # Send the saved generation to n8n.
                sent, message = send_content_to_n8n(
                    episode_title=episode_title.strip(),
                    genre=genre,
                    platform=platform,
                    generated_content=content,
                    generation_id=generation_id,
                )

                if sent:
                    st.success(message)
                else:
                    st.warning(
                        f"Content was saved locally, but automation failed. {message}"
                    )

                st.session_state["latest_content"] = content
                st.session_state["latest_generation_id"] = generation_id

                st.success(
                    f"Content generated and saved! "
                    f"Generation ID: {generation_id}"
                )

                st.caption(
                    f"Generation time: {generation_time:.2f} seconds"
                )

            except (RuntimeError, json.JSONDecodeError, ValueError) as exc:
                st.error(f"Could not generate valid content: {exc}")

            except Exception as exc:
                st.error(
                    f"An unexpected error occurred: {exc}"
                )

    # Display the latest result during the current session.
    if "latest_content" in st.session_state:
        st.divider()
        st.header("Generated Result")

        display_content(st.session_state["latest_content"])

        st.download_button(
            "Download Content as JSON",
            data=json.dumps(
                st.session_state["latest_content"],
                ensure_ascii=False,
                indent=2,
            ),
            file_name="generated_content.json",
            mime="application/json",
        )


# -----------------------------
# Content Library
# -----------------------------


# -----------------------------
# Content Library
# -----------------------------

elif page == "Content Library":
    st.title("Content Library")
    st.write(
        "Search, filter, and manage your previously generated content."
    )

    records = get_all_generations()

    if not records:
        st.info(
            "Your library is empty. Generate some content first."
        )

    else:
        df = pd.DataFrame(records)

        # Search and filter controls.
        st.subheader("Find Content")

        col1, col2, col3 = st.columns(3)

        with col1:
            search_query = st.text_input(
                "Search episode title",
                placeholder="Enter a title...",
            )

        with col2:
            available_genres = sorted(
                df["genre"].dropna().unique().tolist()
            )

            selected_genre = st.selectbox(
                "Filter by genre",
                ["All genres"] + available_genres,
            )

        with col3:
            available_platforms = sorted(
                df["platform"].dropna().unique().tolist()
            )

            selected_platform = st.selectbox(
                "Filter by platform",
                ["All platforms"] + available_platforms,
            )

        filtered_records = records

        if search_query.strip():
            filtered_records = [
                record
                for record in filtered_records
                if search_query.strip().lower()
                in record["episode_title"].lower()
            ]

        if selected_genre != "All genres":
            filtered_records = [
                record
                for record in filtered_records
                if record["genre"] == selected_genre
            ]

        if selected_platform != "All platforms":
            filtered_records = [
                record
                for record in filtered_records
                if record["platform"] == selected_platform
            ]

        st.caption(
            f"Showing {len(filtered_records)} of {len(records)} "
            "saved generations."
        )

        # Summary table.
        if filtered_records:
            table_df = pd.DataFrame(filtered_records)

            st.dataframe(
                table_df[
                    [
                        "id",
                        "episode_title",
                        "genre",
                        "platform",
                        "created_at",
                        "generation_time",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

        st.divider()
        st.subheader("Saved Content")

        if not filtered_records:
            st.info("No generations match these filters.")

        for record in filtered_records:
            with st.expander(
                f"#{record['id']} — {record['episode_title']}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Genre:** {record['genre']}")
                    st.write(f"**Platform:** {record['platform']}")
                    st.write(f"**Audience:** {record['audience']}")

                with col2:
                    st.write(f"**Tone:** {record['tone']}")
                    st.write(f"**Created:** {record['created_at']}")
                    st.write(
                        f"**Generation time:** "
                        f"{record['generation_time'] or 0:.2f} sec"
                    )

                content = json.loads(record["generated_content"])
                display_content(content)

                st.download_button(
                    "Download this result",
                    data=json.dumps(
                        content,
                        ensure_ascii=False,
                        indent=2,
                    ),
                    file_name=f"generation_{record['id']}.json",
                    mime="application/json",
                    key=f"download_{record['id']}",
                )

                if st.button(
                    "Delete this generation",
                    key=f"delete_{record['id']}",
                ):
                    delete_generation(record["id"])

                    if st.session_state.get(
                        "latest_generation_id"
                    ) == record["id"]:
                        st.session_state.pop(
                            "latest_content", None
                        )
                        st.session_state.pop(
                            "latest_generation_id", None
                        )

                    st.rerun()
