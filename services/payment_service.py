import os
import aiohttp
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("API_KEY")
BOT_WALLET = "0x835a6A4500c1Cbb1c5F0B8Be3C1cF3DB6b8fcBE2"
USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASESCAN_URL = "https://api.basescan.org/api"
async def check_usdc_payment(expected_amount, bot_wallet, deal_start_time):
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "module": "account",
                "action": "tokentx",
                "address": bot_wallet,
                "contractaddress": USDC_CONTRACT,
                "apikey": API_KEY,
                "sort": "desc"
            }

            async with session.get(BASESCAN_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()
    except Exception as e:
        print(f'API Error: {str(e)}')
        return False

    txs = data.get("result", [])

    expected_decimal = Decimal(str(expected_amount))
    tolerance = Decimal("0.005") * expected_decimal
    maximum_expected_amount = expected_decimal + min(tolerance, Decimal("0.005"))

    for tx in txs:
        try:
            value = Decimal(tx["value"]) / Decimal(10 ** 6)
            confirmations = int(tx.get("confirmations", 0))
            tx_time = datetime.fromtimestamp(int(tx["timeStamp"]))

            is_to_correct = tx['to'].lower() == BOT_WALLET.lower()
            is_amount_valid = expected_decimal <= value <= maximum_expected_amount
            is_confirmed = confirmations >= 15
            is_on_time = deal_start_time <= tx_time <= datetime.now()


            if is_to_correct and is_amount_valid and is_confirmed and is_on_time:
                print(f"✅ Confirmed payment: {value} USDC with {confirmations} confirmations")
                print(f"Hash: {tx["hash"]}")
                return True
        except Exception as e:
            print(f"Error processing transaction {tx.get('hash')}: {str(e)}")
            continue
    return False





