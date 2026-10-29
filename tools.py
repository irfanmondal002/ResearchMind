import os
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()


@tool
def web_search(query: str) -> str:
    """Search the web for reliable information about a topic.
    Return source titles, URLs, and snippets.
    """
    query = query.strip()

    if not query:
        raise ValueError("The search query cannot be empty.")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing. Add it to your .env file."
        )

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=5,
        )

        results = response.get("results", [])
        if not results:
            return "No search results were found."

        output = []

        for result in results:
            output.append(
                f"Title: {result.get('title', 'Untitled')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Snippet: {result.get('content', '')[:500]}\n"
            )

        return "\n---\n".join(output)

    except Exception as exc:
        raise RuntimeError(
            f"Web search failed: {type(exc).__name__}: {exc}"
        ) from exc


@tool
def scrape_url(url: str) -> str:
    """Fetch a public HTTP or HTTPS webpage and extract readable text."""
    parsed_url = urlparse(url.strip())

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    hostname = (parsed_url.hostname or "").lower()

    if not hostname:
        raise ValueError("The URL must contain a hostname.")

    if hostname in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Local URLs cannot be scraped.")

    try:
        response = requests.get(
            url.strip(),
            timeout=(5, 15),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
                )
            },
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "footer", "header", "noscript"]
        ):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        if not text:
            return f"No readable text was extracted from {url}."

        return (
            f"Source URL: {url}\n\n"
            f"Extracted webpage content:\n{text[:8000]}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Could not scrape {url}: {type(exc).__name__}: {exc}"
        ) from exc