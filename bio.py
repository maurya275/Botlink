"""
Author: Bisnu Ray
User: https://t.me/BisnuRay
Channel: https://t.me/itsSmartDev
"""

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

app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ================= MESSAGE LINK DETECTOR ================= #

MESSAGE_LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/)",
    re.IGNORECASE
)

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message):
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"

    text = (
        "**✨ Welcome to BioLink Protector Bot! ✨**\n\n"
        "🛡️ I help protect your groups from users with links in their bio.\n\n"
        "**Use /help to see all available commands.**"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to Your Group", url=add_url)],
        [
            InlineKeyboardButton("🛠️ Support", url="https://t.me/itsSmartDev"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ])

    await message.reply_text(text, reply_markup=kb)


@app.on_message(filters.command("help"))
async def help_handler(client: Client, message):
    help_text = (
        "**🛠️ Bot Commands & Usage**\n\n"
        "`/config` – set warn-limit & punishment mode\n"
        "`/free` – whitelist a user\n"
        "`/unfree` – remove whitelist\n"
        "`/freelist` – list whitelisted users\n"
    )
    await message.reply_text(help_text)


# ================= BIO CHECK SYSTEM ================= #

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
    full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
    mention = f"[{full_name}](tg://user?id={user_id})"
    user_name = full_name  # bug fix

    if URL_PATTERN.search(bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return await message.reply_text("Please grant me delete permission.")

        mode, limit, penalty = await get_config(chat_id)

        if mode == "warn":
            count = await increment_warning(chat_id, user_id)

            warning_text = (
                "**🚨 Warning Issued** 🚨\n\n"
                f"👤 **User:** {mention} `[{user_id}]`\n"
                "❌ **Reason:** URL found in bio\n"
                f"⚠️ **Warning:** {count}/{limit}\n"
            )

            sent = await message.reply_text(warning_text)

            if count >= limit:
                try:
                    if penalty == "mute":
                        await client.restrict_chat_member(
                            chat_id, user_id,
                            ChatPermissions(can_send_messages=False)
                        )
                        await sent.edit_text(f"🔇 {user_name} muted (Link in Bio)")
                    else:
                        await client.ban_chat_member(chat_id, user_id)
                        await sent.edit_text(f"🔨 {user_name} banned (Link in Bio)")
                except errors.ChatAdminRequired:
                    await sent.edit_text("I don't have permission.")
        else:
            try:
                if penalty == "mute":
                    await client.restrict_chat_member(
                        chat_id, user_id,
                        ChatPermissions(can_send_messages=False)
                    )
                    await message.reply_text(f"🔇 {user_name} muted (Link in Bio)")
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await message.reply_text(f"🔨 {user_name} banned (Link in Bio)")
            except errors.ChatAdminRequired:
                await message.reply_text("I don't have permission.")
    else:
        await reset_warnings(chat_id, user_id)


# ================= GROUP LINK PROTECTION SYSTEM ================= #

@app.on_message(filters.group & (filters.text | filters.caption))
@app.on_edited_message(filters.group & (filters.text | filters.caption))
async def delete_group_links(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    text = message.text or message.caption or ""

    has_link = MESSAGE_LINK_PATTERN.search(text)
    is_forward = message.forward_from or message.forward_from_chat

    if has_link or is_forward:
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return

        bot = await client.get_me()
        add_url = f"https://t.me/{bot.username}?startgroup=true"

        warning_text = (
            "⚠️ **Member/Bot ke bheje gaye link ko delete kiya gaya.**\n\n"
            "🔐 Apne group ko secure karne ke liye hamen apne group me add kare."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me To Your Group", url=add_url)]
        ])

        await client.send_message(
            chat_id,
            warning_text,
            reply_markup=keyboard
        )


if __name__ == "__main__":
    app.run()