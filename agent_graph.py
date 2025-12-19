# agent_graph.py
from langgraph.graph import StateGraph
from typing import Dict, Any
from main import load_json_file

def algo_node(state: Dict[str, Any]) -> Dict[str, Any]:
    show = int(state.get("show", 5))
    # auto-select file same as main.py logic
    if load_json_file:
        try:
            data = load_json_file("enriched_coins.json")
        except Exception:
            data = load_json_file("coins.json")
    else:
        data = load_json_file("coins.json")

    lines = []
    for item in data[:show]:
        sym = (item.get("symbol") or "").upper()
        name = item.get("name") or ""
        price = None
        try:
            price = item.get("quote", {}).get("USD", {}).get("price")
        except Exception:
            price = None
        lines.append(f"{sym} — {name} (price: {price})")
    return {"result": "\n".join(lines)}

graph = StateGraph(dict)
graph.add_node("algo", algo_node)
graph.set_entry_point("algo")
graph.set_finish_point("algo")

agent = graph.compile()

from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

import os
TEST_API_KEY = os.getenv("API_KEY")

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != TEST_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/run")
def run_agent(payload: dict, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return agent.invoke(payload)
