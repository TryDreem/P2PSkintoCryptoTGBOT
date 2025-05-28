from aiogram import Router
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(lambda c: c.data == 'how_to_use')
async def how_to_use(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Buyer's side",callback_data="info_for_buyer"),
            InlineKeyboardButton(text="Seller's side",callback_data="info_for_seller"),
            InlineKeyboardButton(text="Back", callback_data="start"),

        ]
    ])
    await callback.message.answer(
        f"**How the Bot Works**\n\n"
        f"**Payment Process** 💸\nAfter the buyer agrees to the deal, they will send the exact amount of USDC to the wallet address provided by the bot. The transaction is tracked, and the bot will wait for the confirmation of payment.\n\n"
        f"**Skin Sending by the Seller** 🎮 \nOnce the payment is confirmed, the seller will send the skin to the bot's trade offer. The bot will check if the skin matches the details provided by the seller (skin name, float, stickers). This is done to ensure that the correct item is being sent.\n\n"
        f"**Confirmation by the Buyer** ✅\nThe buyer must confirm the receipt of the skin. They will have a window of **10 minutes** to check and confirm that everything is correct.\n\n"
        f"**Completion of the Deal** ✔️\nOnce the buyer confirms the receipt of the skin, the bot will release the USDC to the seller, minus a 1% transaction fee. Both parties are notified about the successful completion of the transaction.\n\n"
        f"**Dispute Resolution** ⚖️\nIf there is a problem with the transaction (e.g., wrong skin or non-confirmation), a dispute can be opened. In such cases, we will review the transaction details and take the necessary actions to resolve the issue fairly.\n\n"
        f"**More info for buyer and seller below, please read it carefully!**",
        parse_mode="Markdown", reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == 'info_for_buyer')
async def info_for_buyer(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back", callback_data="how_to_use")
        ]
    ])
    await callback.message.answer(
        f"🔹 **Buyer's Instructions:**\n\n"
        f"1. Seller creates a deal and sends you the link or ID.\n"
        f"2. Click \"Create Deal\" → Select the deal.\n"
        f"3. Enter your **Steam trade offer link** and **Steam nickname**.\n"
        f"4. Carefully **verify the skin info**: name, float, and stickers.\n"
        f"5. Bot will show the USDC wallet address. **Send the exact amount** to the wallet.\n"
        f"6. Once payment is confirmed, the seller will send the skin to the bot.\n"
        f"7. You will have **10 minutes to confirm** the skin is correct.\n"
        f"8. If confirmed, the seller receives payment.\n\n"
        f"🛑 If the item is wrong or you suspect a scam, open a **dispute** before confirming.\n",
        parse_mode="Markdown", reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == 'info_for_seller')
async def info_for_seller(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Back", callback_data="how_to_use")
        ]
    ])
    await callback.message.answer(
        f"🔹 **Seller's Instructions:**\n\n"
        f"1. Click \"Create Deal\" and enter:\n"
        f"   - Skin name\n"
        f"   - Float value\n"
        f"   - Stickers (if any)\n"
        f"   - Price in USDC\n"
        f"   - **Your Steam nickname**\n"
        f"   - **Your Base network wallet address**\n\n"
        f"2. Wait for a buyer to join and send payment.\n"
        f"3. When payment is confirmed, send the skin in a trade offer to the buyer.\n"
        f"4. Buyer checks the skin for a match.\n"
        f"5. When the buyer confirms receipt, you receive USDC (with 1% fee).\n\n"
        f"🛑 Do **not** send the skin before bot confirms payment.\n",
        parse_mode="Markdown", reply_markup=keyboard
    )
