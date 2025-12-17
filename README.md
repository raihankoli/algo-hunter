<p align="center"><img src="https://raw.githubusercontent.com/raihankoli/algo-hunter/main/logo.png" width="200" /></p>

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Warden Studio](https://img.shields.io/badge/Warden-Agent-green)

# Algo Hunter — LangChain & Warden Studio Ready Crypto Analysis Agent

Algo Hunter is a Warden-ready AI agent that analyzes 9000+ crypto assets, detects exchange listings, ranks coins, and returns clean insights.

### Features
- Search any asset (name or symbol)
- 9000+ enriched coins dataset
- Exchange detection (Binance, Coinbase, OKX)
- Automated scoring & ranking
- Precomputed Top 10 snapshot
- Modular & Warden-optimized structure

## LangChain & LangGraph Integration

Algo Hunter is built using the **LangChain ecosystem** and structured with **LangGraph**
to support stateful, modular, and production-ready agent workflows.

- LangChain tools & executors  
- LangGraph-based agent flow  
- FastAPI-compatible agent interface  
- Designed for seamless Warden Studio integration

### Files
- `main.py` — Entrypoint  
- `multi_fetcher.py` — Data enrichment  
- `leaderboard.py` — Scoring engine  
- `coins.json` — Base list  
- `enriched_coins.json` — Enriched dataset  
- `top10.csv` — Pre-ranked assets  
- `agent.yaml` — Agent config  
- `requirements.txt` — Dependencies  

## Warden Studio Compatibility

Algo Hunter is designed to be **Warden Studio–ready**:

- Clean API entrypoint  
- Deterministic outputs  
- Modular agent structure  
- Compatible with LangChain / LangGraph deployment flow  

Once the Warden Agent Hub is public, this agent can be registered without refactoring.

### Author
Built by **Rayhan Koly**
```
pip install -r requirements.txt
python main.py
```
---
## ⭐ Support
If you find Algo Hunter useful, consider giving the repository a **star ⭐** — it helps a lot!
## 🤝 Contributing
Contributions are welcome!  
Feel free to open an **issue**, submit a **pull request**, or suggest improvements.
## 📄 License
This project is **proprietary**.  
Copying, modifying, or redistributing the code is **strictly prohibited** without permission.
---

Built with ⚡ by **Rayhan Koly**
