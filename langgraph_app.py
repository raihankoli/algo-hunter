from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
import json

load_dotenv()

# -------- STATE --------
class AgentState(TypedDict):
    query: str
    result: dict


# -------- CORE LOGIC --------
def load_data():
    if os.path.exists("enriched_coins.json"):
        file = "enriched_coins.json"
    else:
        file = "coins.json"

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_algo(state: AgentState):
    data = load_data()

    # simple top10 by market cap
    scored = []
    for c in data:
        mc = c.get("quote", {}).get("USD", {}).get("market_cap", 0) or 0
        scored.append((mc, c))

    ranked = sorted(scored, reverse=True)[:10]

    out = []
    for i, (_, r) in enumerate(ranked, start=1):
        out.append({
            "rank": i,
            "name": r.get("name"),
            "symbol": r.get("symbol"),
            "price": r.get("quote", {}).get("USD", {}).get("price"),
            "market_cap": r.get("quote", {}).get("USD", {}).get("market_cap"),
        })

    return {
        "query": state["query"],
        "result": {"top10": out},
    }


# -------- LANGGRAPH --------
builder = StateGraph(AgentState)
builder.add_node("algo", run_algo)
builder.set_entry_point("algo")
builder.add_edge("algo", END)

graph = builder.compile()
