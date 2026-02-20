import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "LinkProtector",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= STRONG LINK PATTERN ================= #

LINK_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)",
    re.IGNORECASE
)

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start(client, message):
    bot = await client.get_me()
    add_link = f"https://t.me/{bot.username}?startgroup=true"

    await message.reply_text(
        "🛡️ **Link Protection Bot Active**\n\n"
        "Any link sent in group will be deleted automatically.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("➕ Add Me To Your Group", url=add_link)]]
        )
    )

# ================= LINK DELETE SYSTEM ================= #

@app.on_message(filters.group & ~filters.service)
@app.on_edited_message(filters.group & ~filters.service)
async def auto_delete_links(client, message):

    if not message:
        return

    text = message.text or message.caption or ""

    # Detect real links only (NOT @username)
    has_link = LINK_PATTERN.search(text)

    # Detect forwarded message
    is_forward = message.forward_from or message.forward_from_chat

    if has_link or is_forward:

        try:
            await message.delete()
        except:
            return

        bot = await client.get_me()
        add_link = f"https://t.me/{bot.username}?startgroup=true"

        await client.send_message(
            message.chat.id,
            "⚠️ **Link Deleted Successfully!**\n\n"
            "🔐 Keep your group safe from links.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("➕ Add Me To Your Group", url=add_link)]]
            )
        )

# ================= RUN ================= #

app.run()