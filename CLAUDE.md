# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Gradio web UI (entry point)
python expert_panel_ui/app_ui.py
```

The app runs at `http://localhost:7860`.

## Environment Setup

Copy `example.env` to `.env` and populate:
- `OPENAI_API_KEY` — Required for OpenAI models and embeddings (text-embedding-ada-002)
- `ANTHROPIC_API_KEY` — Required for Claude models
- `GOOGLE_API_KEY` — Required for Gemini models
- `COGNITIVE_SVC_KEY`, `COGNITIVE_SVC_REGION`, `COG_SERVICE_ENDPOINT` — Azure Speech (optional)
- `GRADIO_DEFAULT_CONCURRENCY_LIMIT` — Gradio concurrency setting

For local Ollama models (llama3, deepseek-r1:1.5b), install and run Ollama separately before starting the app.

## Architecture

**Multi-agent LLM discussion simulator** — multiple AI experts (backed by different LLMs) discuss a topic in rounds, then a summarizer produces structured output.

### Component Map

| Layer | Module | Responsibility |
|---|---|---|
| UI | `expert_panel_ui/app_ui.py` | Gradio interface, state management, event wiring |
| Orchestration | `discussion/expert_discussion.py` | Discussion loop, expert lifecycle, round control |
| Agents | `experts/expert.py` | `Expert` (base), `DetailerExpert` (discussion), `SummarizerExpert` |
| Prompts | `experts/prompts.py` | System/discussion/summarizer prompt templates |
| LLM Config | `config/llm_config.py` | Initializes all LLM instances, maps type strings to objects |
| RAG | `utils/common_utils.py` | PDF/YAML ingestion into ChromaDB, document querying |

### Discussion Flow

1. User enrolls experts via the UI, each assigned a name, specialization, LLM type, and word limit.
2. `ExpertDiscussion.summarization(topic)` drives the session:
   - `start_discussion()` runs N rounds; each expert calls `think_and_respond()` against its LLM chain, streaming words back via `slow_echo()`.
   - All prior expert statements are injected into the next expert's prompt to enforce novel responses.
3. `SummarizerExpert.summarize()` produces a JSON-structured output (topic, summary, action items with SMART criteria) via `StructuredOutputParser`.

### LLM Support

`config/llm_config.py` initializes all models on startup and maps string keys (e.g., `"gpt-4o"`, `"gemini-2.0-flash"`, `"llama3"`, `"claude-sonnet-4-6"`) to LangChain LLM objects. To add a new model, add its initialization there and register the key in the map.

Current supported models: GPT-3.5-turbo, GPT-4o-mini, GPT-4o, GPT-4.1-mini, Gemini Pro, Gemini 2.0 Flash, Gemini 2.5 Flash, llama3 (Ollama), deepseek-r1:1.5b (Ollama), Claude Sonnet 4.6, Claude Haiku 4.5.

### RAG / Knowledge Base

Experts optionally use ChromaDB for document-grounded responses. Load documents via `utils/common_utils.load_and_embed_data()` (supports PDF and YAML). When a knowledge base is attached to an expert, the chain switches from `LLMChain` to `ConversationalRetrievalChain`.

### Expert Status States

`Expert` objects cycle through: `Idle → Thinking → Speaking → Listening → Idle`. The UI polls these states to update the status display in real time.

### Discussion Logging

Completed discussions are logged as CSV in `flagged_data_points/`. Gradio's built-in flagging appends to `flagged_data_points/log.csv`.
