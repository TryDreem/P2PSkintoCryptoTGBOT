from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import DEALS_HISTORY_FILE
from models.states import DEAL_STATUSES
import json
from datetime import datetime

router = Router()

@router.callback_query(lambda c: c.data == "view_history")
async def view_history(callback: CallbackQuery):
    def escape_markdown_v1(text):
        text = str(text)
        text = text.replace('*', '\*')
        text = text.replace('_', '\_')
        return text

    try:
        if not DEALS_HISTORY_FILE.exists() or DEALS_HISTORY_FILE.stat().st_size == 0:
            return await callback.answer("History is empty", show_alert=True)

        with open(DEALS_HISTORY_FILE) as f:
            all_deals = json.load(f)

        user_id = callback.from_user.id

        user_deals = [
            deal for deal in all_deals[-10:]
            if deal["creator_id"] == user_id or deal.get("buyer_id") == user_id
        ]

        if not user_deals:
            return await callback.answer("🤷 No deals found", show_alert=True)

        response = ["📜 *Your deal history:*\n"]

        for i, deal in enumerate(user_deals, 1):
            try:
                date = datetime.fromisoformat(deal['created_at']).strftime("%d.%m.%Y %H:%M")
            except (KeyError, ValueError):
                date = "N/A"

            information = (
                f"*{escape_markdown_v1(i)}. {escape_markdown_v1(deal['skin_name'])}*\n"
                f"    📏 *Float:* {escape_markdown_v1(deal['skin_float'])}\n"
                f"    🪄 *Decorations:* {escape_markdown_v1(deal['skin_decorations'])}\n"
                f"    💵 *Price:* {escape_markdown_v1(deal['skin_price'])}$\n"
                f"    🕒 *Date:* {escape_markdown_v1(date)}\n"
                f"    👤 *Role:* {'Seller' if deal['creator_id'] == user_id else 'Buyer'}\n"
                f"    🚦 *Status:* {escape_markdown_v1(DEAL_STATUSES.get(deal.get('status'), 'unknown'))}\n"
                f"    📌 *ID:* `{escape_markdown_v1(deal.get("deal_id","Unknown"))}`\n"
            )

            if deal.get('creator_id') == user_id and 'transaction_hash' in deal:
                information += f"    💸 *Refund:* https://basescan.org/tx/{deal['transaction_hash']}\n"

            if deal["status"] not in ["completed", "dispute"]:
                information += "\nYou can start dispute with this deal.\n"

            response.append(information)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back", callback_data="start")],
            [InlineKeyboardButton(text="Start dispute", callback_data="start_dispute")]
        ])

        await callback.message.answer("\n".join(response), parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()

    except json.JSONDecodeError:
        await callback.answer("❌ Error: Invalid history data", show_alert=True)
    except Exception as e:
        print(f"History error: {e}")
        await callback.answer("🔧 Error loading history", show_alert=True)
