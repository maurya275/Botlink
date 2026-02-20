import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "UltimateLinkProtector",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ========= STRONG LINK PATTERN (NOT @username) ========= #

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
        "🛡️ Link Protection Bot Active\n\n"
        "All links will be deleted automatically.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("➕ Add Me To Your Group", url=add_link)]]
        )
    )

# ================= MAIN LINK DELETE SYSTEM ================= #

@app.on_message(filters.group & filters.all)
@app.on_edited_message(filters.group & filters.all)
async def delete_links(client, message):

    if not message:
        return

    text = message.text or message.caption or ""

    # Detect real links (NOT username tag)
    has_link = LINK_PATTERN.search(text)

    # Detect forwarded messages (user or bot)
    is_forward = message.forward_from or message.forward_from_chat

    if has_link or is_forward:

        try:
            await message.delete()
        except Exception as e:
            print("Delete failed:", e)
            return

        bot = await client.get_me()
        add_link = f"https://t.me/{bot.username}?startgroup=true"

        await client.send_message(
            message.chat.id,
            "⚠️ Link detected and deleted!\n\n"
            "🔐 Secure your group from spam links.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("➕ Add Me To Your Group", url=add_link)]]
            )
        )

# ================= RUN ================= #

app.run()