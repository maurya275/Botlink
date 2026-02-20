import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "UltraLinkProtector",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ========= STRONG LINK DETECTOR ========= #

LINK_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)",
    re.IGNORECASE
)

# ================= MAIN DELETE SYSTEM ================= #

@app.on_message(filters.group)
@app.on_edited_message(filters.group)
async def delete_links(client, message):

    text = message.text or message.caption or ""

    has_link = LINK_PATTERN.search(text)

    is_forward = (
        message.forward_from or
        message.forward_from_chat
    )

    # Detect sender_chat (anonymous admin / channel / bot)
    is_sender_chat = message.sender_chat is not None

    if has_link or is_forward:

        try:
            await message.delete()
        except Exception as e:
            print("Delete error:", e)
            return

        bot = await client.get_me()
        add_link = f"https://t.me/{bot.username}?startgroup=true"

        await client.send_message(
            message.chat.id,
            "⚠️ Link Deleted!\n\n🔐 Group Protected.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("➕ Add Me", url=add_link)]]
            )
        )

app.run()