from llm_backend import generate
from agents.prompts import SYSTEM_PROMPT, PLANNING_PROMPT, REVISION_PROMPT, EMAIL_PROMPT
from tools.slides import parse_pdf, slide_context
from tools.web_search import search_web
from tools.logger import log


def build_package(state: dict) -> str:
    if not state.get("file_path"):
        return "No slide file uploaded yet."

    try:
        pages = parse_pdf(state["file_path"])
    except Exception as exc:
        log(state, f"Slide parsing failed: {exc}")
        return f"Could not parse slides: {exc}"

    if not pages:
        return "No readable text was found in the uploaded PDF."

    state["pages"] = pages
    log(state, f"Parsed {len(pages)} slide/page(s).")
    slides = slide_context(pages)

    prompt = PLANNING_PROMPT.format(
        duration=state.get("duration", "60 minutes"),
        audience=state.get("audience", "university students"),
        language=state.get("language", "English"),
        slides=slides,
    )
    draft = generate([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    revised = generate([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": REVISION_PROMPT.format(draft=draft)},
    ])
    state["package"] = revised
    state["approved"] = False
    log(state, "Generated and revised lesson package.")
    return revised


def research(state: dict) -> str:
    topic = state.get("topic")
    if not topic and state.get("pages"):
        topic = state["pages"][0]["text"][:120]
    topic = topic or "NLP lecture teaching resources"
    results = search_web(f"{topic} lecture tutorial examples", max_results=3)
    state["research"] = results
    log(state, "Completed web research.")
    lines = ["Useful external resources:"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}\n   URL: {r['url']}\n   Why useful: {r['snippet']}")
    return "\n".join(lines)


def prepare_email(state: dict) -> str:
    package = state.get("package", "No package generated yet.")
    resources = state.get("research", [])
    resource_text = "\n".join([f"- {r['title']}: {r['url']}" for r in resources])
    combined = f"{package}\n\n# Useful Links\n{resource_text}"
    email_body = generate([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": EMAIL_PROMPT.format(package=combined)},
    ], max_tokens=1200)
    state["email_body"] = email_body
    log(state, "Prepared email preview.")
    return email_body
