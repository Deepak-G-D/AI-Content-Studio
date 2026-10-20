# AI Content Studio

A local LLM-powered content generation application that transforms episode details into structured promotional content. Built with Python and Streamlit, the application integrates with LM Studio for local inference, SQLite for persistent storage, and n8n webhooks for workflow automation.

## Features

- **AI-Powered Content Generation:** Generate episode summaries, hooks, captions, titles, and calls to action from episode details.
- **Local LLM Integration:** Connect to a locally running language model through LM Studio's OpenAI-compatible API.
- **Structured JSON Output:** Request content in a consistent JSON format for easier processing and downstream automation.
- **Content Persistence:** Store generated content and metadata in SQLite, including timestamps and generation duration.
- **Dashboard & Analytics:** View total generations, average generation time, genre distribution, and recent activity.
- **Content Library:** Search by episode title, filter by genre and platform, inspect saved generations, download results, and delete records.
- **Workflow Automation:** Send generated content to an n8n webhook for further processing.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| User Interface | Streamlit |
| LLM Runtime | LM Studio |
| AI Integration | OpenAI-compatible REST API |
| Data Storage | SQLite |
| Workflow Automation | n8n |
| HTTP Requests | Requests |
| Data Format | JSON |

## Architecture

```text
User Input
    |
    v
Streamlit Application
    |
    v
Prompt Construction
    |
    v
LM Studio Local LLM
    |
    v
JSON Response Validation
    |
    v
SQLite Persistence
    |
    +----------------------+
    |                      |
    v                      v
Dashboard & Library     n8n Webhook
                           |
                           v
                    Workflow Processing
```

## Generated Content

For each episode, the application generates:

- **Episode Summary:** A concise overview of the episode.
- **Hooks:** Three attention-grabbing opening lines.
- **Captions:** Two promotional caption options.
- **Titles:** Two potential titles.
- **Calls to Action:** Two prompts encouraging audience engagement.

The generated content is returned in JSON format, making it easier to display, store, and transfer to other workflow tools.

## Getting Started

### Prerequisites

- Python version compatible with the project
- [uv](https://docs.astral.sh/uv/) package manager
- [LM Studio](https://lmstudio.ai/) with a compatible model downloaded
- [n8n](https://n8n.io/) for the optional workflow automation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Install dependencies

This project uses `uv` for Python dependency management.

```bash
uv sync
```

This installs the dependencies declared in `pyproject.toml` and uses the project's lockfile when available.

### 3. Start LM Studio

1. Open LM Studio and load your chosen model.
2. Start the local API server.
3. Verify that the endpoint configured in `llm.py` matches your server settings.

The default endpoint used by the application is:

```text
http://localhost:1234/v1/chat/completions
```

### 4. Configure n8n (optional)

1. Start your local n8n instance.
2. Create a workflow with a Webhook node.
3. Configure the webhook path to match the URL in `automation.py`.
4. Connect the webhook to an Edit Fields node to structure the incoming content.
5. Listen for a test event when using the test webhook URL.

### 5. Run the application

```bash
uv run streamlit run app.py
```

The application will start locally. Open the URL displayed in the terminal to use AI Content Studio.


Open the local URL printed in your terminal by Streamlit.

## Project Structure

```text
AI-Content-Studio/
├── app.py          # Streamlit interface, dashboard and content library
├── llm.py          # LM Studio API integration
├── prompts.py      # System instructions and user prompt construction
├── database.py     # SQLite database operations
├── automation.py   # n8n webhook integration
├── requirements.txt
├── .gitignore
└── README.md
```

The file names above reflect the intended project structure; adjust them if your repository uses different names.

## Data Storage

Generated content is stored locally in SQLite, together with associated metadata. The database layer supports initializing the database, saving generations, retrieving saved records, and deleting entries.

This provides a persistent content history without requiring a separate hosted database.

## Design Decisions

- **Local inference:** Uses LM Studio to run the language model locally rather than requiring a hosted LLM API.
- **Structured responses:** Requests JSON output to make generated fields easier to validate and process.
- **Separation of concerns:** Keeps prompt construction, model communication, database operations, and workflow integration in separate modules.
- **Persistent storage:** Uses SQLite to preserve generated content between application sessions.
- **Graceful automation failure:** Keeps locally stored results even when the n8n webhook is unavailable.

## Current Scope and Limitations

- Generation quality and response time depend on the selected local model and available hardware.
- Structured output still requires validation because model responses may be incomplete or malformed.
- The n8n integration depends on the webhook endpoint being available and correctly configured.
- The application currently focuses on content generation and workflow handoff; automated publishing to external platforms is outside its current scope.

## Future Improvements

- Add retry handling and clearer recovery for malformed or truncated model responses.
- Add export options for individual records and batches of generated content.
- Track generation success rates and failures in the dashboard.
- Extend n8n workflows for reporting and additional content-processing steps.
- Add automated tests for JSON validation, database operations, and API failure scenarios.

## Author

Developed as a practical project exploring local LLM integration, content workflows, application development, and operational analytics.
