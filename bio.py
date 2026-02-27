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

# ================== SETTINGS ================== #

# 👉 YAHAN GALI WORDS ADD KARO
ABUSE_WORDS = [
    "madarchod",
    "bhosdike",
    "chutiya",
    "mc",
    "bc",
    "gandu",
    "randi",
    "harami",
    "fuck",
    "shit",
    "bitch"
]

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)

# ============================================== #

app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# =============== COMMON BUTTON =============== #

async def get_add_button(client):
    bot = await client.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me In Your Group", url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ============================================= #
# ============ MAIN GROUP HANDLER ============ #

@app.on_message(filters.group & ~filters.service)
async def group_security(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    # ===============================
    # 🔹 1. MESSAGE LINK DELETE
    # ===============================

    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        kb = await get_add_button(client)
        await client.send_message(
            chat_id,
            "✨🔗 **Link Deleted Successfully!**\n\n🚫 Links are not allowed here.",
            reply_markup=kb
        )
        return

    # ===============================
    # 🔹 2. FORWARD DELETE
    # ===============================

    if message.forward_date:
        try:
            await message.delete()
        except:
            pass

        kb = await get_add_button(client)
        await client.send_message(
            chat_id,
            "📤🚫 **Forward Message Deleted!**\n\nForwarded content is restricted here.",
            reply_markup=kb
        )
        return

    # ===============================
    # 🔹 3. ABUSE FILTER
    # ===============================

    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass

            kb = await get_add_button(client)
            await client.send_message(
                chat_id,
                "⚠️🚫 **Abuse Message Not Allowed Here!**\n\nMaintain respect in the group.",
                reply_markup=kb
            )
            return

    # ===============================
    # 🔹 4. AUTO MEDIA DELETE
    # ===============================

    if message.media:
        await asyncio.sleep(20)
        try:
            await message.delete()
        except:
            pass


# ============================================= #
# ========== EDITED MESSAGE CHECK ============ #

@app.on_edited_message(filters.group)
async def edited_security(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        kb = await get_add_button(client)
        await client.send_message(
            chat_id,
            "✏️🚫 **Edited Message Deleted!**\n\nEdited links are not allowed here.",
            reply_markup=kb
        )


# ============================================= #
# ========== ORIGINAL BIO WARNING ============ #
# 🔥 YE SYSTEM SAME HAI — TOUCH NAHI KIYA

@app.on_message(filters.group)
async def check_bio(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Skip admin & whitelist (original logic)
    if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
        return

    user = await client.get_chat(user_id)
    bio = user.bio or ""

    full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
    mention = f"[{full_name}](tg://user?id={user_id})"

    if URL_PATTERN.search(bio):

        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return await message.reply_text("Please give me delete permission.")

        mode, limit, penalty = await get_config(chat_id)

        if mode == "warn":

            count = await increment_warning(chat_id, user_id)

            warning_text = (
                f"🚨 **Warning Issued** 🚨\n\n"
                f"👤 {mention}\n"
                f"⚠️ Warning {count}/{limit}\n\n"
                "Remove link from your bio."
            )

            sent = await message.reply_text(warning_text)

            if count >= limit:
                try:
                    if penalty == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                        await sent.edit_text(f"{mention} has been 🔇 muted for [Link In Bio].")
                    else:
                        await client.ban_chat_member(chat_id, user_id)
                        await sent.edit_text(f"{mention} has been 🔨 banned for [Link In Bio].")
                except:
                    pass

        else:
            try:
                if mode == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                else:
                    await client.ban_chat_member(chat_id, user_id)
            except:
                pass

    else:
        await reset_warnings(chat_id, user_id)


# ============================================= #

if __name__ == "__main__":
    app.run()