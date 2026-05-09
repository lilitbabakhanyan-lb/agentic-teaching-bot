# Design Report: Agentic Telegram Teaching Assistant

## 1. Project overview

This project implements a small but complete LLM application for an NLP homework assignment. The system is a Telegram bot that accepts lecture slides, extracts slide text, uses a local LLM to create a teaching package, searches for supporting web resources, prepares an email preview, and sends the email only after explicit user approval.

The goal is not to build a very large system. The goal is to demonstrate tool integration, local LLM usage, basic agentic workflow design, and reliability.

## 2. Architecture

The project uses a simple finite-state workflow rather than a heavy agent framework. This keeps the behavior clear and easy to debug.

```text
Telegram Bot API -> Session State -> Orchestrator
                                  |-> Slide parser
                                  |-> Local LLM backend
                                  |-> Web search tool
                                  |-> Email sender
                                  |-> Logger/status tool
```

Each Telegram user receives a small in-memory session dictionary. The session stores uploaded file information, lecture duration, audience, output language, recipient email, generated package, research results, email preview, approval status, and logs.

The main workflow is:

1. User uploads a PDF.
2. `/plan` stores the duration, audience, language, and email.
3. The slide parser extracts text with page references.
4. The orchestrator sends the slide text to the local LLM.
5. The LLM produces a lesson package.
6. A second LLM call revises the package for clarity, timing, and grounding.
7. The bot creates an email preview.
8. User approves with `/approve`.
9. `/send` sends the email through SMTP.

## 3. Local LLM backend

The LLM backend is wrapped in a single function:

```python
generate(messages, temperature=0.2, max_tokens=900)
```

This function calls an OpenAI-compatible local server. The project can work with either llama.cpp or vLLM.

Recommended lightweight setup:

- Backend: llama.cpp server
- Model: TinyLlama-1.1B-Chat
- Quantization: GGUF Q4_K_M
- Context length: 4096
- Example command:

```bash
./llama-server -m models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --host 127.0.0.1 --port 8080 -c 4096
```

A stronger local model can be substituted if hardware allows. The code only depends on the OpenAI-compatible `/chat/completions` endpoint.

## 4. Tools

The project exposes the four practical tools required by the assignment.

### Slide parsing/retrieval

`tools/slides.py` uses PyMuPDF to extract PDF text page by page. Each page is stored with its page number, allowing the final package to include grounding notes such as `[slides: page 3]`.

### Web search

`tools/web_search.py` uses DuckDuckGo Search and returns 3 compact results with title, URL, and snippet. If web search fails, the tool returns a failure message instead of crashing the bot.

### Email sending

`tools/email.py` sends email through SMTP. Credentials are loaded from environment variables. The bot never sends an email until the user has reviewed the preview and used `/approve`.

### Logging/status

`tools/logger.py` appends simple timestamped messages to the user session. `/status` shows the uploaded file, current settings, approval state, and recent logs.

## 5. Prompts

Prompts are stored in `agents/prompts.py`. The planning prompt asks for the exact required structure:

- Title
- Slide summary with references
- Main concepts and prerequisites
- Learning objectives
- Timed teaching plan
- At least one exercise
- Grounding notes

A revision prompt asks the model to check whether the plan is realistic, clear, and grounded in the slides. An email prompt converts the package into a short professional email body.

## 6. Reliability and safety choices

The implementation includes several basic reliability decisions:

- Secrets are not committed; `.env.example` is provided instead.
- Email credentials are loaded only from environment variables.
- Email sending requires explicit `/approve`.
- Non-PDF files are rejected in the minimal version.
- Missing recipient email prevents sending.
- Failed web search returns an error resource instead of crashing.
- `/status` helps debug the current session.

## 7. Evaluation

### Test case 1: normal workflow

Input: a valid PDF lecture file about NLP, duration 60 minutes, audience undergraduate NLP students, language English, recipient email provided.

Expected result: the bot extracts slide text, creates a package with objectives, timed plan, exercise, links, email preview, then sends only after `/approve`.

### Test case 2: bad file

Input: upload a `.docx` or image file.

Expected result: the bot replies that only PDF is supported in the minimal version and does not crash.

### Test case 3: missing email

Input: upload slides and run `/plan 60 minutes | students | English`, then `/approve`, then `/send`.

Expected result: the bot refuses to send and says the recipient email is missing.

### Test case 4: unapproved send

Input: generate a plan and immediately run `/send` without `/approve`.

Expected result: the bot refuses to send and asks the user to approve the preview first.

## 8. Grounding check

The generated package is required to mark slide-based claims with slide/page references. External resources are shown separately under web research, so the user can distinguish slide-grounded content from web-supported material.

## 9. Latency note

Approximate runtime depends on hardware and model size. On a CPU with a small GGUF model, slide extraction is usually under a few seconds, while generation may take from 30 seconds to several minutes. On a GPU with vLLM and a small instruct model, generation is usually much faster.

## 10. Limitations

The minimal implementation intentionally avoids over-engineering. It does not include persistent database storage, PPTX parsing, PDF attachment generation, a dashboard, or advanced retrieval. The session state resets when the bot restarts. The output quality depends heavily on the chosen local model and the quality of slide text extraction.
