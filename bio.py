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

# ================= EXTRA SECURITY SETTINGS ================= #

ABUSE_WORDS = [
    "madarchod","bhosdike","chutiya","mc","bc",
    "gandu","randi","harami","fuck","shit","bitch"
]

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)

MEDIA_DELETE_TIME = 50

# ================= APP ================= #

app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"

    text = (
        "**✨ Welcome to BioLink Protector Bot! ✨**\n\n"
        "🛡 Bio Protection + Advanced Group Security Enabled.\n\n"
        "Use /help to see all commands."
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to Your Group", url=add_url)],
        [InlineKeyboardButton("🗑️ Close", callback_data="close")]
    ])

    await message.reply_text(text, reply_markup=kb)

# ================= HELP ================= #

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    help_text = (
        "**🛠 Commands:**\n\n"
        "`/config` – set warn limit & punishment\n"
        "`/free` – whitelist user\n"
        "`/unfree` – remove whitelist\n"
        "`/freelist` – list whitelist\n\n"
        "Security Enabled:\n"
        "• Bio link detector\n"
        "• Link delete\n"
        "• Abuse delete\n"
        "• Edited check\n"
        "• Forward delete\n"
        "• Media auto delete (50 sec)"
    )
    await message.reply_text(help_text)

# ================= CONFIG / FREE / CALLBACK ================= #
# (Aapka original pura system yaha untouched rehne de)
# IMPORTANT: Aapka original config, free, unfree,
# freelist, callback_handler same rehne de.
# Unko delete nahi karna.
# Sirf niche unified security add kiya gaya hai.

# ================= UNIFIED SECURITY ================= #

@app.on_message(filters.group & ~filters.service)
async def unified_security(client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    if await is_admin(client, chat_id, user_id):
        return

    if await is_whitelisted(chat_id, user_id):
        return

    bot = await client.get_me()
    promo_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

    # ========= BIO LINK CHECK ========= #

    try:
        user = await client.get_chat(user_id)
        bio = user.bio or ""
    except:
        return

    if URL_PATTERN.search(bio):

        try:
            await message.delete()
        except:
            pass

        mode, limit, penalty = await get_config(chat_id)

        count = await increment_warning(chat_id, user_id)

        warn_msg = await message.reply_text(
            f"🚨 Warning {count}/{limit}\nUser has link in bio."
        )

        if count >= limit:
            try:
                # 🔥 ALWAYS MUTE (Ban disabled)
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions()
                )
                await warn_msg.edit_text("🔇 User muted (Link in Bio)")
            except:
                pass

        return

    # ========= LINK DELETE ========= #

    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        await message.reply_text(
            "🔗 Link Deleted!",
            reply_markup=promo_kb
        )
        return

    # ========= FORWARD DELETE ========= #

    if message.forward_date:
        try:
            await message.delete()
        except:
            pass

        await message.reply_text(
            "📤 Forward Deleted!",
            reply_markup=promo_kb
        )
        return

    # ========= ABUSE DELETE ========= #

    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass

            await message.reply_text(
                "⚠️ Abuse Deleted!",
                reply_markup=promo_kb
            )
            return

    # ========= MEDIA SILENT DELETE ========= #

    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass

# ================= EDITED MESSAGE SECURITY ================= #

@app.on_edited_message(filters.group)
async def edited_security(client, message):

    if not message.from_user:
        return

    text = message.text or message.caption or ""

    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass
        return

    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass
        return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Started Successfully ✅")
    app.run()