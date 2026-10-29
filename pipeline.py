import os
from typing import Callable

from dotenv import load_dotenv

from agents import (
    build_reader_agent,
    build_search_agent,
    extract_agent_text,
    get_critic_chain,
    get_writer_chain,
)

load_dotenv()

StepCallback = Callable[[str, str, str], None]


def _notify(
    callback: StepCallback | None,
    step: str,
    status: str,
    detail: str = "",
) -> None:
    if callback:
        callback(step, status, detail)


def _run_step(
    step: str,
    action,
    callback: StepCallback | None = None,
) -> str:
    """Run a single stage and notify the UI about its status."""
    _notify(callback, step, "running", f"{step} stage started")

    try:
        result = action()
    except Exception as exc:
        _notify(callback, step, "error", str(exc))
        raise

    _notify(callback, step, "done", f"{step} stage completed")
    return result


def run_research_pipeline(
    topic: str,
    on_step: StepCallback | None = None,
) -> dict:
    """Run Search -> Reader -> Writer -> Critic."""

    topic = topic.strip()

    if not topic:
        raise ValueError("Please provide a research topic.")

    google_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )
    tavily_key = os.getenv("TAVILY_API_KEY")

    missing = []

    if not google_key:
        missing.append("GOOGLE_API_KEY")

    if not tavily_key:
        missing.append("TAVILY_API_KEY")

    if missing:
        raise RuntimeError(
            "Missing API key(s): "
            + ", ".join(missing)
            + ". Check your .env file."
        )

    state = {}

    # -----------------------------------------------------
    # Step 1: Search Agent
    # -----------------------------------------------------

    def do_search():
        result = build_search_agent().invoke(
            {
                "messages": [
                    (
                        "user",
                        (
                            "Search the web for recent, reliable, "
                            "detailed information about this topic: "
                            f"{topic}\n\n"
                            "Return useful source titles, complete "
                            "URLs and evidence-based summaries. "
                            "Do not invent sources."
                        ),
                    )
                ]
            }
        )

        return extract_agent_text(result)

    state["search"] = _run_step(
        "search",
        do_search,
        on_step,
    )

    if not state["search"]:
        raise RuntimeError("The Search Agent returned no results.")

    # -----------------------------------------------------
    # Step 2: Reader Agent
    # -----------------------------------------------------

    def do_read():
        prompt = (
            f"Research topic: {topic}\n\n"
            "Choose the single most relevant URL from these "
            "search results. Call scrape_url using that exact "
            "URL and summarize the extracted source. Do not "
            "invent URLs.\n\n"
            "Search results:\n"
            f"{state['search'][:10000]}"
        )

        result = build_reader_agent().invoke(
            {
                "messages": [
                    ("user", prompt)
                ]
            }
        )

        return extract_agent_text(result)

    state["reader"] = _run_step(
        "reader",
        do_read,
        on_step,
    )

    if not state["reader"]:
        raise RuntimeError("The Reader Agent returned no content.")

    # -----------------------------------------------------
    # Step 3: Writer Chain
    # -----------------------------------------------------

    def do_write():
        combined_research = (
            "SEARCH RESULTS:\n"
            f"{state['search']}\n\n"
            "SCRAPED SOURCE:\n"
            f"{state['reader']}"
        )

        return get_writer_chain().invoke(
            {
                "topic": topic,
                "research": combined_research,
            }
        )

    state["writer"] = _run_step(
        "writer",
        do_write,
        on_step,
    )

    if not state["writer"]:
        raise RuntimeError("The Writer Chain returned no report.")

    # -----------------------------------------------------
    # Step 4: Critic Chain
    # -----------------------------------------------------

    def do_critic():
        return get_critic_chain().invoke(
            {
                "report": state["writer"],
            }
        )

    state["critic"] = _run_step(
        "critic",
        do_critic,
        on_step,
    )

    return state


if __name__ == "__main__":
    research_topic = input("Enter a research topic: ")

    try:
        result = run_research_pipeline(research_topic)

        print("\n" + "=" * 60)
        print("FINAL RESEARCH REPORT")
        print("=" * 60)
        print(result["writer"])

        print("\n" + "=" * 60)
        print("CRITIC FEEDBACK")
        print("=" * 60)
        print(result["critic"])

    except Exception as exc:
        print(f"\nResearch pipeline failed: {exc}")