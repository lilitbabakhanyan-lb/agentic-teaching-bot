def search_web(query: str, max_results: int = 3) -> list[dict]:
    """Return compact web resources. Falls back gracefully if search fails."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", "Untitled"),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:250],
                })
        return results
    except Exception as exc:
        return [{"title": "Web search failed", "url": "", "snippet": str(exc)}]
