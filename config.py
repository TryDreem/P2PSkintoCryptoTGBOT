import os
from pathlib import Path
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEALS_HISTORY_FILE = Path("data/deals_history.json")
USER_DATA_FILE = Path("data/user_data.json")
BOT_WALLET = "0x835a6A4500c1Cbb1c5F0B8Be3C1cF3DB6b8fcBE2" #here you can change to your bot's wallet
load_dotenv()
bot = Bot(token=TOKEN)
active_deals:  dict[str, dict] = {}