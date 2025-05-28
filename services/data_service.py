import json
import uuid
from aiogram.fsm.context import FSMContext
from config import USER_DATA_FILE, DEALS_HISTORY_FILE


def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data,dict):
                return data
            return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def get_user_data(user_id):
    data = load_user_data()
    return data.get(str(user_id), {})


async def load_profile_to_state(user_id,state: FSMContext):
    user_data = await get_user_data(user_id)
    await state.update_data(
        steam_nickname=user_data.get("steam_nickname"),
        crypto_wallet=user_data.get("crypto_wallet"),
        trade_url=user_data.get("trade_url")
    )


def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def save_deal_to_history(deal: dict):
    try:
        deal = deal.copy()
        deal['created_at'] = deal['created_at'].isoformat()

        if not DEALS_HISTORY_FILE.exists():
            DEALS_HISTORY_FILE.write_text("[]")

        try:
            with open(DEALS_HISTORY_FILE, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []


        if "deal_id" not in deal:
            deal["deal_id"] = str(uuid.uuid4())
        data.append(deal)

        with open(DEALS_HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"Error saving deal history: {e}")