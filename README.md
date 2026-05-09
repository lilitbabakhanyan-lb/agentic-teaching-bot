# Agentic Telegram Teaching Assistant

A lightweight NLP homework project: a Telegram bot that accepts lecture slides, uses a local LLM, creates a teaching plan, researches supporting resources, previews an email, and sends it only after approval.

## Features

- Telegram commands: `/start`, `/help`, `/plan`, `/research`, `/status`, `/approve`, `/send`
- PDF slide text extraction with page references
- Local LLM backend through an OpenAI-compatible server such as llama.cpp or vLLM
- Compact web research with 3 resources
- SMTP email sending after explicit user approval
- Simple session state and logs
- Graceful handling of bad files, missing email, failed search, and unapproved sending

## Setup

```bash
git clone <your-repo-url>
cd agentic-teaching-bot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your Telegram bot token, LLM server URL, and SMTP credentials.

## Run a local LLM

### Option A: llama.cpp server
Example command:

```bash
./llama-server \
  -m models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  -c 4096
```

Use this in `.env`:

```bash
LLM_BASE_URL=http://localhost:8080/v1
LLM_MODEL=local-model
```

Documented model for this submission: `TinyLlama-1.1B-Chat`, GGUF `Q4_K_M`, context length `4096`. You may replace it with any local instruct model available on your machine.

### Option B: vLLM OpenAI-compatible server

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --host 127.0.0.1 \
  --port 8000
```

Then set:

```bash
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct
```

## Run the bot

```bash
python bot.py
```

## Example Telegram flow

1. Send `/start`
2. Upload a PDF file
3. Send:

```text
/plan 60 minutes | undergraduate NLP students | English | teacher@example.com
```

4. Send `/research`
5. Review the preview
6. Send `/approve`
7. Send `/send`

The bot refuses to send email without approval.

## Repository structure

```text
agentic-teaching-bot/
  README.md
  .env.example
  requirements.txt
  bot.py
  llm_backend.py
  agents/
    orchestrator.py
    prompts.py
  tools/
    slides.py
    web_search.py
    email.py
    logger.py
  examples/
    sample_slides.pdf
    sample_output.md
  design_report.md
```

## Limitations

- Minimal version supports PDF only. PPTX support can be added later.
- Web search depends on external connectivity and can fail.
- The LLM quality depends on the local model selected.
- Session state is stored in memory, so it resets when the bot restarts.
- Email sending requires SMTP credentials and an app password for Gmail-like providers.

## Academic integrity note

External libraries are used for Telegram, PDF parsing, web search, and HTTP calls. The architecture, prompts, and glue code should be understood before submission.
