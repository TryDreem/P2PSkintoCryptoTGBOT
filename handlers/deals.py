import asyncio
from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models.states import ProfileStates
from services.data_service import save_deal_to_history, load_profile_to_state
from services.crypto_service import send_usdc
from services.payment_service import check_usdc_payment
from utils.validators import (generate_code, is_valid_price, final_price_format, is_valid_evm_address,
                              is_valid_steam_nickname)
from config import bot, active_deals
from datetime import datetime, timedelta



router = Router()

@router.callback_query(lambda c: c.data == 'create_deal')
async def create_deal(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="I'm buying skin", callback_data="buyer_part"),
            InlineKeyboardButton(text="I'm selling skin", callback_data="seller_part"),
            InlineKeyboardButton(text="How to use bot", callback_data="how_to_use"),
            InlineKeyboardButton(text="Back", callback_data="start")
        ]
    ])
    await callback.message.answer(f'**Please, carefully read how to use bot!\nClicking on the one of '
                                  f'the buttons means your are agreed with our policy and all risks.**\n'
                                  f'Who you are?', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'buyer_part')
async def buyer_part(callback: types.CallbackQuery, state: FSMContext):
    await load_profile_to_state(callback.from_user.id, state)
    data = await state.get_data()
    steam_nickname = data.get("steam_nickname")
    trade_url = data.get("trade_url")
    if steam_nickname and trade_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Back", callback_data="create_deal"),
                InlineKeyboardButton(text="Change info", callback_data="profile"),
                InlineKeyboardButton(text="My info is correct", callback_data="enter_code")
            ]
        ])
        await callback.message.answer(f"❗️Please check your steam nickname and trade offer url carefully️"
                                      f" and if there are any mistakes please change them❗️\n"
                                      f"Your steam nickname: {steam_nickname}\n"
                                      f"Your trade offer url: {trade_url}\n"
                                      f"❗️Only if both of them correct, press the button MY INFO IS CORRECT",
                                      reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Add necessary info", callback_data="profile")
            ]
        ])
        await callback.message.answer("Firstly,you have to add your Steam nickname and trade offer url\n"
                                      "You can do it below",
                                      reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "enter_code")
async def enter_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🔑Please,enter the code from seller")
    await state.set_state(ProfileStates.code)


@router.message(ProfileStates.code)
async def waiting_for_code(message: types.Message, state: FSMContext):
    code = message.text.strip().upper()
    deal = active_deals.get(code)

    if not deal:
        return await message.answer("❌ Code not found or expired")

    if datetime.utcnow() - deal["created_at"] > timedelta(minutes=15):
        del active_deals[code]
        return await message.answer("⌛️ Code has expired")

    deal_info = (
        f"✅ Deal found!\n\n"
        f"🔹 Seller's Steam: {deal['user_steam']}\n"
        f"🔹 Skin name: {deal['skin_name']}\n"
        f"🔹 Float value: {deal.get('skin_float', 'N/A')}\n"
        f"🔹 Decorations: {deal.get('skin_decorations', 'None')}\n"
        f"🔹 Price: {deal['skin_price']}$\n\n"
        f"⚠️ Please verify all details before confirming!"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm Deal", callback_data=f"confirm_deal{code}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="create_deal")
        ]
    ])

    await message.answer(deal_info, reply_markup=keyboard)
    await state.finish()


@router.callback_query(lambda c: c.data == 'seller_part')
async def seller_part(callback: types.CallbackQuery, state: FSMContext):
    await load_profile_to_state(callback.from_user.id, state)
    data = await state.get_data()
    steam_nickname = data.get("steam_nickname")
    evm_address = data.get("crypto_wallet")
    if steam_nickname and evm_address:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Back", callback_data="create_deal"),
                InlineKeyboardButton(text="Change info", callback_data="profile"),
                InlineKeyboardButton(text="My info is correct", callback_data="filling_skin_info")
            ]
        ])
        await callback.message.answer(f"Please check your steam nickname and EVM address carefully"
                                      f" and if there are any mistakes please change them\n"
                                      f"Your steam nickname: {steam_nickname}\n"
                                      f"Your EVM address: `{evm_address}`\n"
                                      f"Only if both of them correct, press the button MY INFO IS CORRECT!",
                                      parse_mode="Markdown",reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Back", callback_data="create_deal"),
                InlineKeyboardButton(text="Add necessary info", callback_data="profile"),
            ]
        ])

        await callback.message.answer("Firstly,you have to add your Steam nickname and EVM address\n"
                                      "You can do it below",
                                      reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'filling_skin_info')
async def filling_skin_info(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back", callback_data="seller_part"),
        ]
    ])
    await callback.message.answer("Type name of skin or item you want to sell",reply_markup=keyboard)
    await state.set_state(ProfileStates.skin_name)


@router.message(ProfileStates.skin_name)
async def skin_name(message: Message, state: FSMContext):
    new_skin_name = message.text.strip()
    await state.update_data(skin_name=new_skin_name)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="My item doesn't have float", callback_data="filling_price"),
        ]
    ])
    await message.answer(f"✅ Skin name saved as **{new_skin_name}**\n"
                         f"Now please type float if your item has it,"
                         f"otherwise press the button below", parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(ProfileStates.skin_float)


@router.callback_query(lambda c: c.data == "filling_price")
async def skipping_float_or_decorations(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.skin_price)
    await callback.message.answer(
        "💰Please type the price in $ you want to sell this skin/item for:",parse_mode="Markdown")
    await callback.answer()


@router.message(ProfileStates.skin_float)
async def skin_float(message: Message, state: FSMContext):
    new_float = message.text.strip()
    await state.update_data(skin_float=new_float)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="My item doesn't have any decorations", callback_data="filling_price"),
        ]
    ])
    await message.answer(f"✅ Skin float saved as **{new_float}**\n"
                         f"Now please type all decorations on your skin\n"
                         f" if your item has it,otherwise press the button below", parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(ProfileStates.decorations)


@router.message(ProfileStates.decorations)
async def decorations(message: Message, state: FSMContext):
    new_decorations = message.text.strip()
    await state.update_data(decorations=new_decorations)
    await message.answer(f"✅ Skin decorations saved as **{new_decorations}**\n"
                         f"Now please type the price in $,you want to sell this skin/item (minimum 10$)", parse_mode="Markdown")
    await state.set_state(ProfileStates.skin_price)


@router.message(ProfileStates.skin_price)
async def price(message: Message, state: FSMContext):
    skin_price = message.text.strip()
    new_price = final_price_format(skin_price)
    if not is_valid_price(new_price):
        await message.answer("❌Minimum skin price is 10$,try again...🔄")
        return
    await state.update_data(skin_price=new_price)
    user_data = await state.get_data()
    user_steam = user_data.get("steam_nickname")
    user_evm_wallet = user_data.get("crypto_wallet")
    skin_name = user_data.get("skin_name")
    skin_float = user_data.get("skin_float")
    skin_decorations = user_data.get("decorations")
    skin_price = user_data.get("skin_price")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Change Info", callback_data="filling_skin_info")],
        [InlineKeyboardButton(text="✅ Confirm and Save", callback_data="sharing_code")]
    ])
    await message.answer(f"💰 Price saved as **{new_price}$** ✅\n"
        f"📋 Here's all information about your offer:\n"
        f"👤 Steam name: {user_steam}\n"
        f"🏦 Wallet: `{user_evm_wallet}`\n"
        f"🔫 Skin: {skin_name}\n"
        f"📏 Float: {skin_float}\n"
        f"🪄 Decorations: {skin_decorations}\n"
        f"💵 Price: {skin_price}$\n",
        parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'sharing_code')
async def sharing_code(callback: CallbackQuery,state: FSMContext):
    user_data = await state.get_data()
    user_steam = user_data.get("steam_nickname")
    user_evm_wallet = user_data.get("crypto_wallet")
    skin_name = user_data.get("skin_name")
    skin_float = user_data.get("skin_float")
    skin_decorations = user_data.get("decorations")
    skin_price = user_data.get("skin_price")
    if not is_valid_steam_nickname(user_steam) or not is_valid_evm_address(user_evm_wallet):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙Back to profile", callback_data="profile"),
            ]
        ])
        await callback.message.answer("Your steam nickname or EVM address is not valid,please try refill profile info",
                                      reply_markup=keyboard)
        return
    code = generate_code()
    active_deals[code] = {
        "creator_id": callback.from_user.id,
        "created_at": datetime.utcnow(),
        "user_steam": user_steam,
        "user_evm_wallet" : user_evm_wallet,
        "skin_name" : skin_name,
        "skin_float" : skin_float,
        "skin_decorations" : skin_decorations,
        "skin_price" : skin_price
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back to menu", callback_data="create_deal"),
        ]
    ])
    await callback.message.answer(
        f"Deal created!\nShare this code with your buyer to start deal (valid 15 minutes).\n`{code}`",
        parse_mode="Markdown", reply_markup=keyboard)


async def monitor_payment_task(bot: Bot, deal: dict, code: str):
    try:
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=15)

        while datetime.now() < end_time:

            payment_received = await check_usdc_payment(
                expected_amount=deal["skin_price"],
                bot_wallet="0x835a6A4500c1Cbb1c5F0B8Be3C1cF3DB6b8fcBE2",
                deal_start_time=start_time
            )


            if payment_received:
                keyboard_for_confirmation = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Skin Sent", callback_data=f"skin_sent{code}")]
                ])
                keyboard_for_dispute = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Start dispute", callback_data=f"dispute{code}")]
                ])

                deal["status"] = "payment_confirmed"
                await bot.send_message(
                    deal["creator_id"],
                    f"💰 Payment received! Now send skin following this trade offer url:\n"
                    f"{deal["buyer_trade_url"]}",
                    reply_markup=keyboard_for_confirmation)
                await bot.send_message(
                    deal["buyer_id"],
                    "💰 Payment received! Now please wait for skin...", reply_markup=keyboard_for_dispute)
                return


            await asyncio.sleep(10)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back", callback_data=f"create_deal")]
        ])

        deal.update({
            "status": "expired"
        })
        save_deal_to_history(deal)
        del active_deals[code]
        await bot.send_message(deal["buyer_id"], "❌ Payment timeout (15 minutes)", reply_markup=keyboard)
        await bot.send_message(deal["creator_id"], "❌ Payment timeout (15 minutes)",reply_markup=keyboard)


    except Exception as e:
        print(f"Error in payment monitoring: {e}")
        await bot.send_message(deal["creator_id"], "⚠️ Payment monitoring failed")


@router.callback_query(lambda c: c.data.startswith("confirm_deal"))
async def confirm_deal_handler(callback: CallbackQuery, state: FSMContext):
    code = callback.data.replace("confirm_deal", "")
    deal = active_deals.get(code)

    if not deal:
        return await callback.message.answer("⚠️ Deal not found or expired.")

    buyer_data = await state.get_data()
    deal.update({
        "buyer_id" : callback.from_user.id,
        "buyer_trade_url" : buyer_data.get("trade_url"),
        "status": "awaiting_payment"
    })
    bot_evm_address = "0x835a6A4500c1Cbb1c5F0B8Be3C1cF3DB6b8fcBE2"

    asyncio.create_task(monitor_payment_task(bot, deal, code))

    await bot.send_message(deal["creator_id"], "💡 Buyer confirmed the deal.\n🕒 Waiting for buyer's payment...")
    await callback.message.answer(
        f"💸 Please send `{deal['skin_price']}` USDC to:\n"
        f"`{bot_evm_address}`\n"
        "Network: Base\n"
        "Token: USDC\n"
        "When payment will be confirmed bot will move on to the next stage...",
        parse_mode="Markdown"
    )


    await state.clear()


@router.callback_query(lambda c: c.data.startswith("skin_sent"))
async def skin_sent_handler(callback: CallbackQuery):
    code = callback.data.replace("skin_sent", "")
    deal = active_deals.get(code)

    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Skin received", callback_data=f"confirm{code}")],
        [InlineKeyboardButton(text="📝 Start dispute", callback_data=f"dispute{code}")]
    ])

    await bot.send_message(deal["buyer_id"], "🎁 Skin sent! Please confirm", reply_markup=confirm_keyboard)
    await bot.send_message(deal["creator_id"], "🕒Waiting for confirmation from buyer...")


@router.callback_query(lambda c: c.data.startswith("confirm"))
async def final_confirmation(callback: CallbackQuery):
    try:
        code = callback.data.replace("confirm","")
        deal = active_deals.get(code)

        final_price = float(deal["skin_price"])
        payout = round(final_price * 0.99, 2)

        tx_hash = send_usdc(f"{deal['user_evm_wallet']}", payout)

        deal.update({"transaction_hash" : tx_hash,
                     "status": "completed"})

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back to menu", callback_data=f"create_deal")]
        ])
        await bot.send_message(
            deal["creator_id"],
            f"✅ Deal complete!\nNetwork: Base\nToken: USDC\n{payout} USDC sent to:\n`{deal['user_evm_wallet']}`\n"
            f"Here you can see transaction in BaseScan:\n"
            f"https://basescan.org/tx/{tx_hash}",
            parse_mode="Markdown",reply_markup=keyboard
        )

        await bot.send_message(
            deal["buyer_id"],"🎉 Thank you for using our service!",reply_markup=keyboard
        )


        save_deal_to_history(deal)

        del active_deals[code]

    except Exception as e:
        await callback.message.answer("❌ Error processing confirmation")
