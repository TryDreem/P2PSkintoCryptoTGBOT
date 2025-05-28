from aiogram import Router, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models.states import ProfileStates
from config import DEALS_HISTORY_FILE
from services.data_service import save_deal_to_history
from config import bot, active_deals
import json
import uuid

router = Router()


@router.callback_query(lambda c: c.data == 'start_dispute')
async def enter_deal_id_for_dispute(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter the deal id to start dispute.")
    await state.set_state(ProfileStates.dispute_deal)


@router.message(ProfileStates.dispute_deal)
async def dispute_handler(message: types.Message):
    deal_id = message.text.strip()
    deal_found = False

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back to history", callback_data=f"view_history")]
    ])
    try:
        with open(DEALS_HISTORY_FILE, "r+") as f:
            deals = json.load(f)

            for deal in deals:

                if 'deal_id' not in deal:
                    deal['deal_id'] = str(uuid.uuid4()) #just in case

                if deal["deal_id"] == deal_id:
                    deal_found = True
                    if deal["status"] == "completed" or deal["status"] == "dispute":
                        await message.answer("Dispute over a completed transaction is not possible",reply_markup=keyboard)
                        return
                    deal["status"] = "dispute"
                    f.seek(0)
                    json.dump(deals, f, indent=2)
                    f.truncate()
                    await message.answer("Dispute has been created. Admin will contact your soon.", reply_markup=keyboard)
                    break
            if not deal_found:
                await message.answer("⚠️ Deal not found", reply_markup=keyboard)

    except Exception as e:
        print(f"Error {e}")
        await message.answer("🚫 An error occurred", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("dispute"))
async def deal_dispute_handler(callback: CallbackQuery):
    code = callback.data.replace("dispute", "")
    deal = active_deals.get(code)
    deal.update({
        "status": "dispute"
    })
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back to profile", callback_data=f"create_deal")]
    ])
    await bot.send_message(deal["buyer_id"], "You have started dispute, admin will contact you soon.",
                           reply_markup=keyboard)
    await bot.send_message(deal["creator_id"], "Buyer started dispute, admin will contact you soon.",
                           reply_markup=keyboard)
    save_deal_to_history(deal)
    del active_deals[code]
