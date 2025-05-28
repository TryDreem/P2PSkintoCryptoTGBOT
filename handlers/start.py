from aiogram import Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from services.data_service import load_profile_to_state
router = Router()

@router.message(Command("start"))
async def start_button(message: Message,state:FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Profile", callback_data="profile"),
        InlineKeyboardButton(text="History", callback_data="view_history"),
        InlineKeyboardButton(text="How to use bot", callback_data="how_to_use"),
        InlineKeyboardButton(text="Policy", callback_data="policy"),
        InlineKeyboardButton(text="Create Deal", callback_data="create_deal")
    ]
    ])
    await load_profile_to_state(message.from_user.id,state)
    await message.answer('Choose an option:', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "start")
async def back_to_start_button(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Profile", callback_data="profile"),
            InlineKeyboardButton(text="History", callback_data="view_history"),
            InlineKeyboardButton(text="How to use bot", callback_data="how_to_use"),
            InlineKeyboardButton(text="Policy", callback_data="policy"),
            InlineKeyboardButton(text="Create Deal", callback_data="create_deal")
        ]
    ])
    await callback.message.answer("Choose an option:", reply_markup=keyboard)
    await callback.answer()
