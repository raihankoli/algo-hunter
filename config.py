# config.py
import os
from dotenv import load_dotenv

# load from .env if present (for local testing)
load_dotenv()

# Market / agent settings
BINANCE_SYMBOL = os.getenv("BINANCE_SYMBOL", "BTCUSDT")     # default symbol
SIGNAL_THRESHOLD = float(os.getenv("SIGNAL_THRESHOLD", "0.05"))  # 5% change
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "60"))     # seconds

# Notifications (optional)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")    # put your bot token in .env if used
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")        # your chat id (number)

# Environment mode
ENV = os.getenv("ENV", "development")  # set to "production" when deployed
