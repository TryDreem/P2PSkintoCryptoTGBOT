from aiogram.fsm.state import State, StatesGroup


DEAL_STATUSES = {
    'awaiting_payment': '⏳ Awaiting payment',
    'payment_confirmed': '✅ Payment confirmed',
    'skin_sent': '📦 Skin sent',
    'completed': '✔️ Completed',
    'expired': '⌛️ Expired',
    'dispute': '⚖️ Dispute'
}

#Here all necessary states
class ProfileStates(StatesGroup):
    steam_nickname = State()
    crypto_wallet = State()
    trade_url = State()
    code = State()
    skin_name = State()
    skin_price = State()
    skin_float = State()
    decorations = State()
    confirm_payment = State()
    confirm_skin_sent = State()
    confirm_skin_received = State()
    dispute_deal =  State()