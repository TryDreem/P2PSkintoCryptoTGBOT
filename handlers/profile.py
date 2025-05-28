from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models.states import ProfileStates
from services.data_service import load_user_data, save_user_data, load_profile_to_state, get_user_data
from utils.validators import is_valid_steam_nickname, is_valid_evm_address, is_valid_trade_url

router = Router()

async def profile_menu(message: types.Message):
    user_data = await get_user_data(message.chat.id) #same as user id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Steam Nickname", callback_data="steam_nickname"),
            InlineKeyboardButton(text="Cryptowallet", callback_data="cryptowallet"),
            InlineKeyboardButton(text="Trade-URL", callback_data="trade_url"),
            InlineKeyboardButton(text="Back", callback_data="start")
        ]
    ])

    profile_info = (
        "👤* Your profile:*\n"
        f"*Steam nickname*: {user_data.get('steam_nickname', 'Not set')}\n"
        f"*EVM Wallet*: `{user_data.get('crypto_wallet', 'Not set')}`\n"
        f"*Trade URL*: {user_data.get('trade_url', 'Not set')}"
    )

    await message.answer(f"*Here you can add/change your profile info*\n {profile_info}\n"
                                  "*Please notice that they will be used for future deals*",
                                  parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "profile")
async def profile(callback: types.CallbackQuery,state: FSMContext):
    await load_profile_to_state(callback.from_user.id, state)
    await profile_menu(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "steam_nickname")
async def checking_steam_nickname(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nickname = data.get("steam_nickname")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="profile")]
    ])

    if nickname:
        await callback.message.answer(
            f"Your Steam nickname is currently stored as: **{nickname}**\n\n"
            "If you want to change it, just send me a new one.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            "You haven't set a Steam nickname yet.\n"
            "Please send me your Steam nickname,so I can save it for future deals."
        )

    await state.set_state(ProfileStates.steam_nickname)
    await callback.answer()


@router.message(ProfileStates.steam_nickname)
async def process_steam_nickname(message: types.Message, state: FSMContext):
    new_nickname = message.text.strip()
    if not is_valid_steam_nickname(new_nickname):
        await message.answer(f"❌Invalid steam nickname, try again...")
        return

    user_id = str(message.from_user.id)
    user_data = load_user_data()


    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["steam_nickname"] = new_nickname
    save_user_data(user_data)

    await state.update_data(steam_nickname=new_nickname)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back to Profile", callback_data="profile")
        ]
    ])
    await message.answer(f"✅ Steam nickname saved as: **{new_nickname}**", parse_mode="Markdown", reply_markup=keyboard)
    await state.finish()


@router.callback_query(lambda c: c.data == "cryptowallet")
async def checking_crypto_wallet(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    evm_address = data.get("crypto_wallet")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="profile")]
    ])

    if evm_address:
        await callback.message.answer(
            f"Your EVM address is currently stored as: ``{evm_address}``\n\n"
            "If you want to change it, just send me a new one.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            "You haven't set your EVM address yet.\n"
            "Please send me your EVM address,so I can save it for future deals."
        )

    await state.set_state(ProfileStates.crypto_wallet)
    await callback.answer()


@router.message(ProfileStates.crypto_wallet)
async def process_crypto_wallet(message: types.Message, state: FSMContext):
    new_evm_address = message.text.strip()
    if not is_valid_evm_address(address=new_evm_address):
        await message.answer("❌Wrong EVM address,try again...")
        return

    user_data = load_user_data()
    user_id = str(message.from_user.id)

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["crypto_wallet"] = new_evm_address
    save_user_data(user_data)

    await state.update_data(crypto_wallet=new_evm_address)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back to Profile", callback_data="profile")
        ]
    ])
    await message.answer(f"✅ Your EVM address:\n ``{new_evm_address}``", parse_mode="Markdown", reply_markup=keyboard)
    await state.finish()


@router.callback_query(lambda c: c.data == "trade_url")
async def checking_trade_url(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    trade_url = data.get("trade_url")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="profile")]
    ])

    if trade_url:
        await callback.message.answer(
            f"Your trade offer url: ``{trade_url}``\n\n"
            "If you want to change it, just send me a new one.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            "You haven't set your trade offer url yet.\n"
            "Please send me your trade offer url,so I can save it for future deals."
        )

    await state.set_state(ProfileStates.trade_url)
    await callback.answer()


@router.message(ProfileStates.trade_url)
async def process_trade_offer(message: types.Message, state: FSMContext):
    new_trade_url = message.text.strip()
    if not is_valid_trade_url(link=new_trade_url):
        await message.answer("❌Wrong trade offer url,try again...")
        return
    user_data = load_user_data()
    user_id = str(message.from_user.id)

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["trade_url"] = new_trade_url
    save_user_data(user_data)

    await state.update_data(trade_url=new_trade_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back to Profile", callback_data="profile")
        ]
    ])
    await message.answer(f"✅ Your trade offer url:\n ``{new_trade_url}``", parse_mode="Markdown", reply_markup=keyboard)
    await state.finish()

