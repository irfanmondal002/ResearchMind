
from functools import lru_cache

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from tools import scrape_url, web_search

load_dotenv()


# ---------------------------------------------------------
# Local LLM Configuration
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_llm():
    """Create and cache the local Ollama model."""
    return ChatOllama(
        model="qwen2.5:7b",
        temperature=0.1,
    )


# ---------------------------------------------------------
# 1. Search Agent
# ---------------------------------------------------------

def build_search_agent():
    return create_agent(
        model=get_llm(),
        tools=[web_search],
        system_prompt=(
            "You are a careful web research search agent. "
            "Always call the web_search tool before answering. "
            "Find relevant, reliable and recent information. "
            "Prefer official documentation, research papers, "
            "reputable publications and primary sources. "
            "Return the source titles, full URLs and useful snippets. "
            "Never invent sources or URLs."
        ),
    )


# ---------------------------------------------------------
# 2. Reader Agent
# ---------------------------------------------------------

def build_reader_agent():
    return create_agent(
        model=get_llm(),
        tools=[scrape_url],
        system_prompt=(
            "You are a web research reader agent. "
            "Inspect the search results provided by the user. "
            "Select the single most relevant HTTP or HTTPS URL "
            "that explicitly appears in those results. "
            "Call the scrape_url tool with that exact URL. "
            "Never invent or alter a URL. "
            "Use the extracted content to report the source title, "
            "URL, important facts, relevant dates and limitations. "
            "If scraping fails, clearly report that failure instead "
            "of pretending the page was read."
        ),
    )


# ---------------------------------------------------------
# 3. Writer Chain
# ---------------------------------------------------------

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert research writer.

Write clear, structured, factual and insightful reports.
Base factual claims on the research supplied to you.
Do not invent statistics, quotations, dates or citations.
Clearly distinguish supported findings from uncertainty.""",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic:
{topic}

Research gathered:
{research}

Use this structure:

# Introduction
Introduce the topic and explain why it matters.

# Key Findings
Present at least three well-explained findings.
Use meaningful headings where appropriate.
Include relevant facts, evidence and context.

# Limitations
Explain important gaps or limitations in the gathered evidence.

# Conclusion
Summarize the main conclusions.

# Sources
List the actual source URLs present in the research.
Do not fabricate URLs or claim to have verified sources
that were not provided.

Write in a professional, readable style.""",
        ),
    ]
)


@lru_cache(maxsize=1)
def get_writer_chain():
    """Create the research report writing chain."""
    return writer_prompt | get_llm() | StrOutputParser()


# ---------------------------------------------------------
# 4. Critic Chain
# ---------------------------------------------------------

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict, constructive research report critic. "
            "Be specific, evidence-based and honest.",
        ),
        (
            "human",
            """Review the research report below.

Report:
{report}

Evaluate accuracy, clarity, structure, depth, source quality,
unsupported claims and missing information.

Respond in exactly this format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)


@lru_cache(maxsize=1)
def get_critic_chain():
    """Create the research report critic chain."""
    return critic_prompt | get_llm() | StrOutputParser()


# ---------------------------------------------------------
# Helper: Extract Agent Output
# ---------------------------------------------------------

def _content_to_text(content) -> str:
    """Convert a message's content into readable text."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):
                text_part = item.get("text")

                if text_part:
                    parts.append(str(text_part))

        return "\n".join(parts).strip()

    return str(content).strip()


def extract_agent_text(result: dict) -> str:
    """Extract the final assistant response from a LangChain agent."""

    messages = result.get("messages", [])

    for message in reversed(messages):
        if getattr(message, "type", None) != "ai":
            continue

        if getattr(message, "tool_calls", None):
            continue

        text = _content_to_text(
            getattr(message, "content", "")
        )

        if text:
            return text

    raise RuntimeError(
        "The agent did not return a final text response."
    )
