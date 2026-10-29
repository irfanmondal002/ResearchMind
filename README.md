
# ResearchMind

An AI-powered research assistant built with Python, Streamlit, LangChain, and Ollama.

ResearchMind uses a multi-stage pipeline to search the web, read relevant sources, generate a structured research report, and review the report. Users can ask follow-up questions about previous research.

## Features

- Web search and source extraction
- Multi-agent research workflow
- AI-generated research reports
- Automated report critique and scoring
- Follow-up questions about generated research
- Local LLM inference using Ollama
- Markdown report downloads
- Dark, chat-style user interface

## Tech Stack

- Python
- Streamlit
- LangChain
- Ollama
- Qwen2.5 7B
- BeautifulSoup
- Tavily Search

## Requirements

- Python 3.12
- uv
- Ollama
- A Tavily API key for the current web search implementation

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/ResearchMind.git
cd ResearchMind
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Download the local model

```bash
ollama pull qwen2.5:7b
```

Make sure Ollama is running on your computer.

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
TAVILY_API_KEY=your_tavily_api_key_here
```

Never commit your actual API keys.

### 5. Run the application

```bash
uv run streamlit run app.py
```

Open the local URL displayed in the terminal.

## Project Structure

```text
ResearchMind/
├── app.py
├── agents.py
├── tools.py
├── pipeline.py
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

## How It Works

1. Search Agent finds relevant web sources.
2. Reader Agent extracts information from a selected source.
3. Writer Chain generates the research report.
4. Critic Chain evaluates the report and suggests improvements.

## Notes

Ollama runs the language model locally. Web search still requires internet connectivity. The current Tavily integration requires a Tavily API key.

Research history is stored locally and is excluded from Git.

## License

Add a license if you intend to distribute the project publicly.