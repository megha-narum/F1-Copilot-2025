# 🏁 F1 2025 Copilot

An AI assistant for casual F1 fans that answers questions about the 2025
season — grounded in real, cited sources, not just AI-generated guesses.

**Live demo:** _https://f1-copilot-2025.streamlit.app/_

---

## What it does

F1's fastest-growing fan segment is young and new to the sport — but F1
has a well-documented onboarding problem, with even F1 itself publishing
an official glossary to explain its own jargon. This project is an
accessibility layer on top of real F1 information, not a new source of
truth: every substantive answer is grounded in a real source and cited,
so you can verify it yourself.

Ask it things like:
- "Who won the Bahrain Grand Prix?"
- "What does a blue flag mean?"
- "Why do F1 cars throw sparks?"

## How it works

The system routes each question to one of two specialized agents,
based on what kind of information it needs — not by topic:

- **Strategy Agent** — for questions about a specific, named 2025 race.
  Resolves the race name to a real round number, pulls actual results
  from a live public F1 data API, and explains them — citing the data
  source.
- **General Agent** — for everything else: rules, terminology, car
  mechanics, and general strategy concepts. Performs a live web search
  restricted to `formula1.com` and `fia.com`, and answers only from what
  it finds — citing the real source URL.

A lightweight router (a single classification call) decides which agent
should handle each question, and correctly declines to answer questions
needing live/current data or unrelated to F1 entirely.

## Tech stack

- **[Claude](https://www.anthropic.com/claude)** (via [LangChain](https://www.langchain.com/)) — language model, accessed through LangChain's standard interface
- **[Tavily](https://tavily.com)** — domain-restricted web search
- **[Jolpica F1 API](https://api.jolpi.ca/ergast/)** — live, real F1 race data
- **[Streamlit](https://streamlit.io)** — web interface
- **Python**

## Project structure

```
main.py       # CLI entry point
app.py        # Streamlit web interface
router.py     # Classifies each question into an agent
agents.py     # The two agents (strategy + general), both cited
data.py       # Live F1 race data fetching
```

## Running it locally

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your own API keys:
   - `ANTHROPIC_API_KEY` from [console.anthropic.com](https://console.anthropic.com)
   - `TAVILY_API_KEY` from [tavily.com](https://tavily.com) (free tier available)
3. Run the CLI version:
   ```
   python3 main.py
   ```
   Or the web version:
   ```
   streamlit run app.py
   ```

## License

This is a personal portfolio project, built for demonstration purposes.
