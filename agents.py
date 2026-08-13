"""
agents.py — Two "experts," both grounded in real, citable sources.

STRATEGY AGENT: looks up real 2025 race results from a live F1 data API,
then asks Claude to explain them — with a citation showing where the
data came from.

GENERAL QUESTIONS AGENT: searches official F1/FIA websites for real
content (rules, terminology, car regulations, general concepts), then
asks Claude to answer using ONLY what was found — with a citation
linking to the real page.

The point of both: this app doesn't claim to know things itself. It
makes REAL, OFFICIAL F1 information easier to find and understand —
an accessibility layer, not a new source of truth.
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient
from data import get_race_results, get_season_schedule

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=400,
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

DATA_SOURCE_NAME = "Jolpica F1 API (official F1/FIA timing data)"


def ask_claude(system_prompt: str, user_message: str) -> str:
    """Shared helper: send instructions + a message, get text back."""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    response = llm.invoke(messages)
    return response.content


# --- STRATEGY AGENT (real race results, cited) ---

def find_race_round(question: str) -> int:
    schedule = get_season_schedule()
    schedule_text = "\n".join(f"{r['round']}: {r['name']}" for r in schedule)

    answer = ask_claude(
        system_prompt=(
            "Given a list of 2025 F1 races and a question, respond with "
            "ONLY the round number that matches, or 'none' if no specific "
            "race is named. No other text."
        ),
        user_message=f"Races:\n{schedule_text}\n\nQuestion: {question}",
    )
    return int(answer) if answer.strip().isdigit() else None


def strategy_agent(question: str) -> str:
    round_number = find_race_round(question)

    if round_number is None:
        return "I can only answer questions about a specific named 2025 Grand Prix; vague references are out of my scope!"

    results = get_race_results(round_number)
    if not results:
        return "I don't have data for that race yet."

    results_text = "\n".join(f"{r['position']}. {r['driver']}" for r in results)

    explanation = ask_claude(
        system_prompt=(
            "You explain F1 race results to casual fans in plain English, "
            "3-4 sentences. Only use the real results you're given — "
            "never invent a finishing position."
        ),
        user_message=f"Real race results:\n{results_text}\n\nQuestion: {question}",
    )

    return f"{explanation}\n\nSource: {DATA_SOURCE_NAME}"


# --- GENERAL QUESTIONS AGENT (real web search, cited) ---

def general_agent(question: str) -> str:
    """
    Searches official F1/FIA websites for real content, then asks
    Claude to answer using ONLY what was found. Always cites the real
    source URL, so the user can verify it themselves — this agent
    never answers from Claude's own memory alone.

    For comparison-style questions, Claude is explicitly instructed to
    cross-check across all sources rather than trust a single result,
    since a single article can be narrowly scoped (e.g. "most wins by
    an Australian driver" is not the same claim as "most wins overall")
    and generalizing from it produces a confidently wrong answer.
    """
    search_results = tavily.search(
        query=question,
        include_domains=["formula1.com", "fia.com"],
        max_results=5,
    )

    hits = search_results.get("results", [])
    if not hits:
        return "I couldn't find anything on F1's official sites for that — try rephrasing."

    sources_text = "\n\n".join(
        f"Source {i+1}: {hit['url']}\nContent: {hit['content'][:500]}"
        for i, hit in enumerate(hits)
    )

    answer = ask_claude(
        system_prompt=(
            "You explain F1 concepts to casual fans in plain English, "
            "3-4 sentences. Base your answer ONLY on the real source "
            "content you're given below — do not add anything from your "
            "own general knowledge that isn't supported by these sources.\n\n"
            "IMPORTANT for comparisons (e.g. 'who had more wins, X or Y'): "
            "cross-check ALL the sources given, not just the first one. "
            "Watch for sources that are narrowly scoped (e.g. a record "
            "'by an Australian driver' is NOT the same as an overall "
            "record) — do not generalize a narrow claim into a broader "
            "one. If the sources don't clearly support a direct "
            "comparison, or they conflict, say so honestly instead of "
            "picking one and stating it as fact."
        ),
        user_message=f"Official F1/FIA source content:\n{sources_text}\n\nQuestion: {question}",
    )

    top_source = hits[0]["url"]
    return f"{answer}\n\nSource: {top_source}"
