"""
Author: Bisnu Ray
Modified: Stable Unified Security Version
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

from config import API_ID, API_HASH, BOT_TOKEN, URL_PATTERN


# ================= EXTRA SETTINGS ================= #

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
        "**✨ BioLink Protector + Advanced Security Bot ✨**\n\n"
        "Bio link detection + Link filter + Abuse filter + Media control enabled.\n\n"
        "Use /help for commands."
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=add_url)]
    ])

    await message.reply_text(text, reply_markup=kb)


# ================= HELP ================= #

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    await message.reply_text(
        "**Commands:**\n\n"
        "/config\n"
        "/free\n"
        "/unfree\n"
        "/freelist\n\n"
        "Security:\n"
        "• Bio Link Warn + Mute\n"
        "• Link Delete\n"
        "• Abuse Delete\n"
        "• Edited Check\n"
        "• Forward Delete\n"
        "• Media Auto Delete (50 sec)"
    )


# ==========================================================
# ================= UNIFIED SECURITY =======================
# ==========================================================

@app.on_message(filters.group & ~filters.service)
async def unified_security(client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    # Skip admin & whitelist
    if await is_admin(client, chat_id, user_id):
        return
    if await is_whitelisted(chat_id, user_id):
        return

    bot = await client.get_me()
    promo_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

    # ================= BIO LINK DETECTOR ================= #

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
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions()
                )
                await warn_msg.edit_text("🔇 User muted (Link in Bio)")
            except:
                pass

        return


    # ================= MESSAGE LINK DELETE ================= #

    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        await message.reply_text("🔗 Link Deleted!", reply_markup=promo_kb)
        return


    # ================= FORWARD DELETE ================= #

    if message.forward_date:
        try:
            await message.delete()
        except:
            pass

        await message.reply_text("📤 Forward Deleted!", reply_markup=promo_kb)
        return


    # ================= ABUSE DELETE ================= #

    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass

            await message.reply_text("⚠️ Abuse Deleted!", reply_markup=promo_kb)
            return


    # ================= MEDIA AUTO DELETE ================= #

    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass


# ================= EDITED MESSAGE CHECK ================= #

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
    print("Bot Running Stable Version ✅")
    app.run()