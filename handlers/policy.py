from aiogram import Router
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(lambda c: c.data == 'policy')
async def policy(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back", callback_data="start"),
        ]
    ])
    await callback.message.answer("Policy info here", reply_markup=keyboard)
    await callback.answer()
