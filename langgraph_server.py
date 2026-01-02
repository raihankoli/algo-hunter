from fastapi import FastAPI, Header, HTTPException
from agent_graph import agent  # agent_graph.py থেকে import

import os
from dotenv import load_dotenv

load_dotenv()  # .env file load
TEST_API_KEY = os.getenv("API_KEY")

app = FastAPI(title="Algo Hunter LangGraph API")

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != TEST_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run_agent(payload: dict, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return agent.invoke(payload)
