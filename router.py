"""
router.py — Decides which of the two agents should answer a question.

This is a small, separate LangChain call whose ONLY job is to pick a
category. It doesn't answer the question itself.
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=10,
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


def route(question: str) -> str:
    """
    Returns one of: "strategy", "general", "needs_live_data", or "unclear".

    "needs_live_data" is for F1-related questions asking about the
    CURRENT/live state of something (e.g. "what tires is Ferrari using
    right now") that neither agent can answer: strategy only covers
    past, named 2025 races, and general only searches static F1/FIA
    pages, not live/current info. This is different from "unclear",
    which is for genuinely off-topic questions.
    """
    messages = [
        SystemMessage(content=(
            "Classify this F1 question into one category. Respond with "
            "ONLY one word:\n"
            "strategy = asking about a SPECIFIC real 2025 race's results "
            "or outcome (e.g. 'who won the Bahrain GP') - only use this "
            "if a specific race is named or clearly implied\n"
            "general = anything else about F1 - rules, penalties, car "
            "mechanics, terminology, or general strategy concepts that "
            "don't require looking up a specific race\n"
            "needs_live_data = F1-related, but asks about something the "
            "system can't resolve to a specific known race: either the "
            "CURRENT/live state of something (e.g. 'what tires is "
            "Ferrari using right now'), OR a RELATIVE time reference "
            "this system has no way to anchor to a real date (e.g. "
            "'last week', 'this weekend', 'recently') since there's no "
            "concept of today's date built in\n"
            "unclear = not related to F1 at all"
        )),
        HumanMessage(content=question),
    ]
    response = llm.invoke(messages)
    answer = response.content.strip().lower()
    valid = ("strategy", "general", "needs_live_data")
    return answer if answer in valid else "unclear"
