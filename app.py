import json
import re
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from pipeline import run_research_pipeline

load_dotenv()


# =========================================================
# 1. PAGE CONFIGURATION AND LOCAL HISTORY
# =========================================================

st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "research_history.json"


# =========================================================
# 2. GLOBAL STYLING
# =========================================================

st.markdown(
    r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    :root {
        --bg: #0b0c0f;
        --panel: #121318;
        --panel-hover: #1a1b21;
        --border: #292a32;
        --text: #ececf1;
        --muted: #92939f;
        --accent: #d8a87d;
        --green: #75c995;
        --red: #ff7777;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Force the whole app canvas to stay black, including Streamlit's main region. */
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    section.main,
    .main,
    .stApp {
        background: #0b0c0f !important;
        background-color: #0b0c0f !important;
        color: var(--text) !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: #0b0c0f !important;
    }

    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { visibility: hidden; }

    .block-container {
        max-width: 1050px;
        padding-top: 1.8rem;
        padding-bottom: 7rem;
    }

    [data-testid="stSidebar"] {
        background: #101116;
        border-right: 1px solid #25262d;
    }

    [data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li { color: #c9c9d2; }

    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: -0.035em;
    }

    h1 { font-size: 2rem !important; font-weight: 650 !important; }
    h2 { font-size: 1.45rem !important; font-weight: 600 !important; }
    h3 { font-size: 1.08rem !important; font-weight: 600 !important; }
    p, li { line-height: 1.75; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    hr { border-color: var(--border); }

    .stButton > button {
        background: #17181e;
        color: #e6e6ed;
        border: 1px solid var(--border);
        border-radius: 12px;
        min-height: 42px;
        transition: background 0.15s, border-color 0.15s;
    }

    .stButton > button:hover {
        background: var(--panel-hover);
        border-color: #55515a;
        color: white;
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(216, 168, 125, 0.22);
    }

    /* White research input on a fully dark canvas. */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] form > div,
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="textarea"] > div,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] [contenteditable="true"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #111217 !important;
        -webkit-text-fill-color: #111217 !important;
        border-color: #e4e4e7 !important;
        caret-color: #111217 !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] {
        border: 1px solid #e4e4e7 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.18) !important;
        overflow: hidden !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #d8a87d !important;
        box-shadow: 0 0 0 2px rgba(216, 168, 125, 0.20) !important;
    }

    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] [contenteditable="true"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1rem !important;
    }

    [data-testid="stChatInput"] textarea::placeholder,
    [data-testid="stChatInput"] [contenteditable="true"]::placeholder {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
        opacity: 1 !important;
    }

    /* A warm accent send button contrasts with the white input. */
    [data-testid="stChatInput"] button {
        background: #d8a87d !important;
        background-color: #d8a87d !important;
        color: #111217 !important;
        border: none !important;
        border-radius: 12px !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] button svg {
        color: #111217 !important;
        fill: #111217 !important;
        stroke: #111217 !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: #e7bc97 !important;
        background-color: #e7bc97 !important;
    }

    [data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding: 1rem 0;
    }

    [data-testid="stChatMessageContent"] {
        color: #e4e4eb;
        font-size: 0.97rem;
        line-height: 1.8;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #111217;
        border-color: var(--border);
        border-radius: 15px;
    }

    [data-testid="stTabs"] button { color: #a9a9b4; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--accent); }
    [data-testid="stTabHighlight"] { background: var(--accent); }

    [data-testid="stExpander"] {
        background: #111217;
        border-color: var(--border);
        border-radius: 12px;
    }

    [data-testid="stExpander"] summary { color: #dadbe2; }

    [data-testid="stDownloadButton"] button {
        background: #e8e5df;
        color: #171717;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    [data-testid="stDownloadButton"] button:hover {
        background: #ffffff;
        color: #111111;
    }

    [data-testid="stStatusWidget"] {
        background: #111217;
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stAlert"] { border-radius: 12px; }
    pre { border-radius: 10px !important; }

    @media (max-width: 700px) {
        .block-container { padding: 1rem 1rem 6rem; }
        h1 { font-size: 1.7rem !important; }
        [data-testid="stChatMessageContent"] { font-size: 0.93rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. PIPELINE STAGES
# =========================================================

STEPS = [
    {
        "key": "search",
        "number": "01",
        "title": "Search the web",
        "description": "Find relevant sources and evidence.",
    },
    {
        "key": "reader",
        "number": "02",
        "title": "Read sources",
        "description": "Extract useful content from a webpage.",
    },
    {
        "key": "writer",
        "number": "03",
        "title": "Write the report",
        "description": "Synthesize the gathered information.",
    },
    {
        "key": "critic",
        "number": "04",
        "title": "Review the report",
        "description": "Evaluate the report and suggest improvements.",
    },
]

WAITING_STATES = {step["key"]: "waiting" for step in STEPS}


# =========================================================
# 4. LOCAL RESEARCH HISTORY
# The app creates research_history.json automatically.
# It stores reports and follow-up chat on this computer.
# =========================================================

def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []

    try:
        content = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(content, list):
            return [item for item in content if isinstance(item, dict)]
    except (OSError, json.JSONDecodeError):
        st.warning("Could not read research_history.json. Starting with an empty history.")

    return []


def save_history(history: list[dict]) -> None:
    """Write research history atomically to avoid partial JSON files."""
    temporary_file = HISTORY_FILE.with_suffix(".json.tmp")
    temporary_file.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(HISTORY_FILE)


def find_research(research_id: str | None) -> dict | None:
    if not research_id:
        return None

    for item in st.session_state.research_history:
        if item.get("id") == research_id:
            return item

    return None


def set_active_research(research_id: str) -> None:
    st.session_state.active_research_id = research_id
    st.session_state.mode = "results"
    st.session_state.error = None


def start_new_research() -> None:
    st.session_state.mode = "research"
    st.session_state.active_research_id = None
    st.session_state.current_topic = ""
    st.session_state.running = False
    st.session_state.error = None
    st.session_state.step_states = WAITING_STATES.copy()


def begin_pipeline(topic: str) -> None:
    topic = topic.strip()
    if not topic:
        return

    st.session_state.current_topic = topic
    st.session_state.running = True
    st.session_state.mode = "running"
    st.session_state.error = None
    st.session_state.step_states = WAITING_STATES.copy()


def explain_error(error: Exception | str) -> str:
    message = str(error)
    normalized = message.lower()

    if any(term in normalized for term in ("resource_exhausted", "quota exceeded", "429")):
        return (
            "The model or API provider has reached a usage limit. Check its quota. "
            "If you intended to use Ollama, verify that agents.py uses ChatOllama."
        )

    if any(term in normalized for term in (
        "connection refused", "failed to connect", "connection error",
        "localhost:11434", "127.0.0.1:11434",
    )):
        return (
            "ResearchMind could not connect to Ollama. Make sure Ollama is running "
            "and check the installed model with `ollama list`."
        )

    if "tavily_api_key" in normalized:
        return "The Tavily key is missing. Check TAVILY_API_KEY in your .env file."

    if "model" in normalized and ("not found" in normalized or "pull" in normalized):
        return "The configured Ollama model may be missing. Run `ollama pull qwen2.5:7b` and verify agents.py."

    return message


def render_step(placeholder, step: dict, status: str) -> None:
    icons = {"waiting": "◯", "running": "⏳", "done": "✓", "error": "✕"}
    labels = {"waiting": "Waiting", "running": "Working", "done": "Completed", "error": "Failed"}
    placeholder.markdown(
        f"**{icons.get(status, '◯')} {step['number']} · {step['title']}**  \n"
        f"{step['description']}  \n`{labels.get(status, 'Waiting')}`"
    )


def render_report(result: dict, index: str) -> None:
    report = result.get("writer", "")
    tabs = st.tabs(["Research summary", "Sources", "Critic review", "Extracted content"])

    with tabs[0]:
        st.markdown(report or "No report was generated.")
        if report:
            slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", result.get("topic", "research_report")).strip("_")[:50]
            slug = slug or "research_report"
            st.download_button(
                "Download report (.md)",
                data=report,
                file_name=f"{slug}.md",
                mime="text/markdown",
                key=f"download_report_{index}",
            )

    with tabs[1]:
        st.markdown("### Search results")
        st.markdown(result.get("search") or "No search results are available.")

    with tabs[2]:
        st.markdown("### Critic feedback")
        st.markdown(result.get("critic") or "No critic feedback is available.")

    with tabs[3]:
        st.markdown("### Extracted webpage content")
        st.markdown(result.get("reader") or "No extracted content is available.")


def ask_about_research(research: dict, question: str) -> str:
    """Answer a follow-up using only the locally generated report context."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    from agents import get_llm

    result = research.get("result", {})
    report = result.get("writer", "")
    topic = research.get("topic", "Untitled research")

    if not report.strip():
        raise RuntimeError("This research item does not contain a report to ask questions about.")

    system_message = SystemMessage(
        content=(
            "You are the ResearchMind follow-up assistant. Answer the user's questions "
            "about the previously generated research report. Use the report below as "
            "your primary and only factual source. Do not run web searches or call tools. "
            "Do not invent facts. If the answer is not supported by the report, say that "
            "the report does not contain enough information and suggest starting new research. "
            "You may explain, summarize, compare, define terms, or clarify content already "
            "covered by the report.\n\n"
            f"Research topic: {topic}\n\n"
            f"Generated research report:\n{report[:24000]}"
        )
    )

    messages = [system_message]

    # Include previous discussion, but avoid adding the current question twice.
    qa_history = research.get("qa_messages", [])
    if (
        qa_history
        and qa_history[-1].get("role") == "user"
        and qa_history[-1].get("content") == question
    ):
        qa_history = qa_history[:-1]

    for item in qa_history[-8:]:
        if item.get("role") == "user":
            messages.append(HumanMessage(content=item.get("content", "")))
        elif item.get("role") == "assistant":
            messages.append(AIMessage(content=item.get("content", "")))

    messages.append(HumanMessage(content=question))
    response = get_llm().invoke(messages)
    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                text_parts.append(str(item["text"]))
        return "\n".join(text_parts).strip()

    return str(content).strip()


# =========================================================
# 5. SESSION STATE
# =========================================================

if "research_history" not in st.session_state:
    st.session_state.research_history = load_history()
if "mode" not in st.session_state:
    st.session_state.mode = "research"
if "active_research_id" not in st.session_state:
    st.session_state.active_research_id = None
if "running" not in st.session_state:
    st.session_state.running = False
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "step_states" not in st.session_state:
    st.session_state.step_states = WAITING_STATES.copy()
if "error" not in st.session_state:
    st.session_state.error = None


# =========================================================
# 6. SIDEBAR: NEW AND PREVIOUS RESEARCH
# =========================================================

with st.sidebar:
    st.markdown("## 🔬 ResearchMind")
    st.caption("Your AI research workspace")
    st.divider()

    if st.button("＋  Research a new topic", use_container_width=True, key="sidebar_new_research"):
        start_new_research()
        st.rerun()

    st.markdown("### Previous research")
    history_sorted = sorted(
        st.session_state.research_history,
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )

    if history_sorted:
        for item in history_sorted[:12]:
            title = item.get("topic", "Untitled research")
            label = title if len(title) <= 34 else title[:31] + "..."
            active = item.get("id") == st.session_state.active_research_id
            if st.button(
                ("● " if active else "· ") + label,
                key=f"open_research_{item.get('id', uuid.uuid4().hex)}",
                help=title,
                use_container_width=True,
            ):
                set_active_research(item["id"])
                st.rerun()
    else:
        st.caption("Your generated reports will appear here.")

    st.divider()
    st.markdown("### How it works")
    st.markdown(
        "**01 · Search**  \nFind useful web sources.\n\n"
        "**02 · Read**  \nExtract webpage content.\n\n"
        "**03 · Write**  \nGenerate the research summary.\n\n"
        "**04 · Review**  \nCritique the report.\n\n"
        "**05 · Ask**  \nDiscuss the report with your local model."
    )
    st.divider()
    st.caption("Model: Ollama · Qwen2.5 7B")
    st.caption("Reports are saved locally in research_history.json.")


# =========================================================
# 7. MAIN HEADER
# =========================================================

header_col, badge_col = st.columns([4, 2])
with header_col:
    st.markdown("## 🔬 ResearchMind")
    st.caption("Research first. Then ask your local AI about what it found.")
with badge_col:
    st.markdown("**LOCAL AI · QWEN2.5 7B**")
    st.caption("Search · Read · Write · Review · Ask")
st.divider()


# =========================================================
# 8. WELCOME / NEW RESEARCH SCREEN
# =========================================================

if st.session_state.mode == "research" and not st.session_state.running:
    st.markdown("### What would you like to research?")
    st.write(
        "Enter a topic to run the full research pipeline. After the report is generated, "
        "you can ask follow-up questions about it or return to any previous report."
    )

    example_topics = [
        "Recent advances in battery technology",
        "How AI agents work",
        "Renewable energy trends",
        "Applications of machine learning",
    ]
    example_cols = st.columns(2)
    for index, example in enumerate(example_topics):
        with example_cols[index % 2]:
            if st.button(example, key=f"example_{index}", use_container_width=True):
                begin_pipeline(example)
                st.rerun()


# =========================================================
# 9. ACTIVE RESEARCH RESULT SCREEN
# =========================================================

active_research = find_research(st.session_state.active_research_id)

if active_research and st.session_state.mode in {"results", "qa"}:
    st.markdown(f"# {active_research.get('topic', 'Research report')}")
    created_at = active_research.get("created_at", "")
    if created_at:
        st.caption(f"Generated locally · {created_at.replace('T', ' ')}")

    if st.session_state.mode == "results":
        render_report(active_research.get("result", {}), active_research.get("id", "report"))

        st.divider()
        st.markdown("### What would you like to do next?")
        choice_qa, choice_new = st.columns(2)

        with choice_qa:
            if st.button(
                "💬  Ask about this research",
                key="ask_this_research",
                use_container_width=True,
            ):
                st.session_state.mode = "qa"
                st.rerun()

        with choice_new:
            if st.button(
                "＋  Research another topic",
                key="research_another_topic",
                use_container_width=True,
            ):
                start_new_research()
                st.rerun()

    elif st.session_state.mode == "qa":
        with st.expander("View the generated research summary", expanded=False):
            st.markdown(active_research.get("result", {}).get("writer", "No report available."))

        st.caption("Your questions are answered by Ollama using this report as context. This mode does not rerun web search.")

        for index, qa_message in enumerate(active_research.get("qa_messages", [])):
            with st.chat_message(qa_message["role"]):
                st.markdown(qa_message.get("content", ""))

        action_qa, action_report, action_new = st.columns([2, 2, 2])
        with action_qa:
            if st.button("← Back to report", key="back_to_report", use_container_width=True):
                st.session_state.mode = "results"
                st.rerun()
        with action_report:
            if st.button("Choose previous research", key="choose_previous_research", use_container_width=True):
                st.session_state.mode = "research"
                st.session_state.active_research_id = None
                st.rerun()
        with action_new:
            if st.button("＋ New research", key="new_from_qa", use_container_width=True):
                start_new_research()
                st.rerun()


# =========================================================
# 10. RESEARCH PIPELINE EXECUTION
# =========================================================

if st.session_state.running:
    st.markdown("### Research in progress")
    st.caption(f"Investigating: {st.session_state.current_topic}")
    progress_container = st.container(border=True)
    progress_slots = {}

    with progress_container:
        for step in STEPS:
            slot = st.empty()
            progress_slots[step["key"]] = slot
            render_step(slot, step, st.session_state.step_states.get(step["key"], "waiting"))

    def on_step(step_key: str, status: str, detail: str) -> None:
        st.session_state.step_states[step_key] = status
        step_definition = next(item for item in STEPS if item["key"] == step_key)
        render_step(progress_slots[step_key], step_definition, status)

    try:
        with st.spinner("ResearchMind is searching, reading, writing, and reviewing..."):
            result = run_research_pipeline(
                st.session_state.current_topic,
                on_step=on_step,
            )

        result["topic"] = st.session_state.current_topic
        record = {
            "id": uuid.uuid4().hex,
            "topic": st.session_state.current_topic,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "result": result,
            "qa_messages": [],
        }
        st.session_state.research_history.append(record)
        save_history(st.session_state.research_history)
        st.session_state.active_research_id = record["id"]
        st.session_state.mode = "results"
        st.session_state.error = None

    except Exception as exc:
        st.session_state.error = str(exc)
        st.session_state.mode = "research"

    finally:
        st.session_state.running = False

    st.rerun()


# =========================================================
# 11. FOLLOW-UP QUESTION ANSWERING
# Follow-up questions use the local LLM and the selected report.
# They do not call run_research_pipeline or web search.
# =========================================================

if st.session_state.mode == "qa" and active_research:
    question = st.chat_input(
        "Ask a question about this research...",
        key="followup_chat_input",
        disabled=st.session_state.running,
    )

    if question and question.strip():
        clean_question = question.strip()
        active_research.setdefault("qa_messages", []).append(
            {"role": "user", "content": clean_question}
        )

        try:
            with st.spinner("Thinking about the generated research..."):
                answer = ask_about_research(active_research, clean_question)

            active_research["qa_messages"].append(
                {"role": "assistant", "content": answer}
            )
            save_history(st.session_state.research_history)

        except Exception as exc:
            active_research["qa_messages"].append(
                {
                    "role": "assistant",
                    "content": "I could not answer that question. " + explain_error(exc),
                }
            )
            save_history(st.session_state.research_history)

        st.rerun()


# =========================================================
# 12. RESEARCH INPUT
# Only the research mode starts the web research pipeline.
# =========================================================

if st.session_state.mode == "research" and not st.session_state.running:
    prompt = st.chat_input(
        "What would you like to research?",
        key="new_research_input",
    )

    if prompt and prompt.strip():
        begin_pipeline(prompt)
        st.rerun()


# =========================================================
# 13. GLOBAL ERROR DISPLAY
# =========================================================

if st.session_state.error:
    st.error("The research pipeline could not complete.")
    st.write(explain_error(st.session_state.error))
    with st.expander("Technical error details"):
        st.code(st.session_state.error, language="text")
