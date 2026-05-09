import os
import requests

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8080/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "local-model")


def generate(messages, temperature=0.2, max_tokens=900):
    try:
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception:
        return (
            "Local LLM is not currently running, so this is a fallback demo response.\n\n"
            "Teaching Package Preview\n\n"
            "Title: Slide-Based Lesson Plan\n"
            "Audience: undergraduate students\n"
            "Duration: 60 minutes\n\n"
            "Learning objectives:\n"
            "- Understand the main topic from the uploaded slides.\n"
            "- Identify key concepts and prerequisites.\n"
            "- Apply the topic through a short exercise.\n\n"
            "Timed plan:\n"
            "0-10 min: Introduction and motivation\n"
            "10-25 min: Main concepts from the slides\n"
            "25-40 min: Guided example\n"
            "40-55 min: Student exercise\n"
            "55-60 min: Recap and questions\n\n"
            "Exercise:\n"
            "Ask students to summarize one key concept and explain how it applies in a practical example.\n\n"
            "Note: For final submission, run a local LLM backend through llama.cpp or vLLM."
        )
