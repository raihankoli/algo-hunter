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
