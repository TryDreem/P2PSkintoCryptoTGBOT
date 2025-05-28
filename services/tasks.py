import asyncio
from datetime import datetime, timedelta
from config import active_deals


async def clean_up_codes():
    while True:
        now = datetime.utcnow()
        expired = [
            code for code, game in active_deals.items()
            if now - game['created_at'] > timedelta(minutes=15)
        ]
        for code in expired:
            del active_deals[code]
        await asyncio.sleep(60)