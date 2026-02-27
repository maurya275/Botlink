"""
Author: Bisnu Ray
User: https://t.me/BisnuRay
Channel: https://t.me/itsSmartDev
"""

import asyncio
import re

from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

from helper.utils import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist
)

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    URL_PATTERN
)

# ================= SETTINGS ================= #

ABUSE_WORDS = [
    "madarchod", "bhosdike", "chutiya",
    "mc", "bc", "gandu", "randi",
    "harami", "fuck", "shit", "bitch"
]

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)

MEDIA_DELETE_TIME = 50  # 50 seconds

# ============================================ #

app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ================= START ==================== #

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message):
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"

    text = (
        "**✨ Welcome to BioLink Protector Bot ✨**\n\n"
        "🛡 Bio link protection + Advanced Group Security\n\n"
        "Use /help to see commands."
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to Your Group", url=add_url)]
    ])

    await message.reply_text(text, reply_markup=kb)

# ============================================ #
# ============ MESSAGE SECURITY ============== #

@app.on_message(filters.group & ~filters.service)
async def message_security(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    if await is_whitelisted(chat_id, user_id):
        return

    # LINK DELETE
    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        bot = await client.get_me()
        await message.reply_text(
            "✨🔗 **Link Deleted Successfully!**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Me In Your Group",
                                      url=f"https://t.me/{bot.username}?startgroup=true")]
            ])
        )
        return

    # FORWARD DELETE
    if message.forward_date:
        try:
            await message.delete()
        except:
            pass

        await message.reply_text("📤🚫 **Forward Message Deleted!**")
        return

    # ABUSE FILTER
    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass

            await message.reply_text("⚠️🚫 **Abuse Message Not Allowed Here!**")
            return

    # MEDIA AUTO DELETE
    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass

# ============================================ #
# ============ EDITED MESSAGE CHECK ========== #

@app.on_edited_message(filters.group)
async def edited_security(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    text = message.text or message.caption or ""

    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        await message.reply_text("✏️🚫 **Edited Message Deleted!**")

# ============================================ #
# ============ BIO LINK WARNING SYSTEM ======= #

@app.on_message(filters.group)
async def check_bio(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
        return

    user = await client.get_chat(user_id)
    bio = user.bio or ""

    if URL_PATTERN.search(bio):

        try:
            await message.delete()
        except:
            return

        mode, limit, penalty = await get_config(chat_id)

        count = await increment_warning(chat_id, user_id)

        warn_msg = await message.reply_text(
            f"🚨 Warning {count}/{limit}\nUser has link in bio."
        )

        if count >= limit:
            try:
                # 🔥 ALWAYS MUTE (never ban)
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await warn_msg.edit_text("🔇 User muted (Link in Bio)")
            except:
                pass
    else:
        await reset_warnings(chat_id, user_id)

# ============================================ #

if __name__ == "__main__":
    app.run()