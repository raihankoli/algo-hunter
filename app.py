# app.py — LangGraph Cloud wrapper for Algo Hunter

from fastapi import FastAPI
from main import app as algo_app

# LangGraph needs an ASGI app instance.
# We simply re-export the FastAPI app from main.py

app = algo_app
