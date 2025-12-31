from fastapi import FastAPI
from pydantic import BaseModel
from langgraph_app import graph

app = FastAPI(title="Algo Hunter LangGraph API")

class RunRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run_agent(req: RunRequest):
    result = graph.invoke({
        "query": req.query
    })
    return result
