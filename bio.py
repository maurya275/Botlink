"""
Author: Bisnu Ray
User: https://t.me/BisnuRay
Channel: https://t.me/itsSmartDev
Upgraded With Link Filter System
"""

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

from link_filter import setup_link_filter  # NEW IMPORT


app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Activate link filter system
setup_link_filter(app)


@app.on_message(filters.command("start"))
async def start_handler(client: Client, message):
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"

    text = (
        "**✨ Welcome to BioLink Protector Bot! ✨**\n\n"
        "🛡️ I protect groups from:\n"
        "• Users with links in bio\n"
        "• Telegram links in messages\n\n"
        "Use /help to see commands."
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to Your Group", url=add_url)],
        [InlineKeyboardButton("🗑️ Close", callback_data="close")]
    ])

    await message.reply_text(text, reply_markup=kb)


@app.on_message(filters.group)
async def check_bio(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if await is_admin(client, chat_id, user_id):
        return

    if await is_whitelisted(chat_id, user_id):
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

        count = await increment_warning(chat_id, user_id)

        warning_text = (
            "**🚨 Warning Issued** 🚨\n\n"
            f"👤 {mention}\n"
            "❌ URL found in bio\n"
            f"⚠️ Warning: {count}/{limit}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel Warning", callback_data=f"cancel_warn_{user_id}"),
             InlineKeyboardButton("✅ Whitelist", callback_data=f"whitelist_{user_id}")]
        ])

        sent = await message.reply_text(warning_text, reply_markup=keyboard)

        if count >= limit:
            try:
                if penalty == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                    await sent.edit_text(f"**{full_name} has been muted (Link In Bio).**")
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await sent.edit_text(f"**{full_name} has been banned (Link In Bio).**")
            except errors.ChatAdminRequired:
                await sent.edit_text("I don't have permission to punish users.")


if __name__ == "__main__":
    app.run()