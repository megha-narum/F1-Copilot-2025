"""
main.py — Run this file. Type a question, get an answer, repeat.

This is the only file you actually run. It ties everything else
together:
    your question -> router.py decides who should answer
                   -> agents.py gives the real, cited answer
"""

from router import route
from agents import strategy_agent, general_agent

AGENTS = {
    "strategy": strategy_agent,
    "general": general_agent,
}

print("F1 2025 Copilot — ask a question, or type 'quit' to stop.\n")

while True:
    question = input("You: ").strip()

    if question.lower() in ("quit", "exit"):
        break
    if not question:
        continue

    category = route(question)

    if category == "unclear":
        print("Bot: I can only help with F1-related questions.\n")
        continue

    if category == "needs_live_data":
        print(
            "Bot: Sorry! I can't answer questions about live or ongoing "
            "F1 info — but go ahead and ask me about a specific 2025 "
            "Grand Prix!\n"
        )
        continue

    agent_function = AGENTS[category]
    answer = agent_function(question)

    print(f"Bot [{category}]: {answer}\n")
