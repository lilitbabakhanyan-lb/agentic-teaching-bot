## Agentic Telegram Teaching Assistant

This project is a lightweight NLP homework assignment built as a Telegram bot. The bot accepts lecture slides in PDF format, extracts the slide text, generates a lesson plan using a local LLM workflow, finds a few supporting web resources, previews the generated result, and sends it by email only after user approval.

The goal of the project was to build a simple agentic workflow with multiple tools working together, rather than focusing on a large or highly optimized model.

# Main Features

- Telegram bot interface
- PDF lecture slide upload
- Slide text extraction with page references
- Lesson plan generation
- Simple web research
- Email preview and approval flow
- Local LLM backend support through llama.cpp or vLLM
- Basic logging and session state handling

# Commands

```text
/start
/help
/plan
/research
/status
/approve
/send
```

# How the Project Works

1. The user starts the Telegram bot.
2. A PDF lecture file is uploaded.
3. The user sends a `/plan` command with lecture information such as duration, audience, language, and recipient email.
4. The bot extracts text from the slides and sends the content to the LLM backend.
5. A teaching package is generated, including objectives, a timed lesson structure, and an exercise.
6. The bot also retrieves several supporting web resources.
7. A preview is shown to the user.
8. The email is sent only after `/approve` is used.

# Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the bot:

```bash
python bot.py
```

The Telegram token and email credentials should be placed inside `.env`.

# Local LLM

The project is designed to work with a local OpenAI-compatible backend such as llama.cpp or vLLM. During development and testing, a fallback response mode was also implemented so the workflow could still be demonstrated on limited hardware.

# Repository Structure

```text
agentic-teaching-bot/
  bot.py
  llm_backend.py
  agents/
  tools/
  examples/
  README.md
  design_report.md
```

# Limitations

- Session state is temporary and resets after restart.
- Web search depends on internet connectivity.
- Local LLM performance depends on available hardware and model size.
