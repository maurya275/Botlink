import asyncio
import re

ABUSE_WORDS = [
    "madarchod","bhosdike","chutiya","mc","bc",
    "gandu","randi","harami","fuck","shit","bitch"
]

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)

MEDIA_DELETE_TIME = 50


@app.on_message(filters.group & ~filters.service)
async def unified_security(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    # Admin / Whitelist skip
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

    user = await client.get_chat(user_id)
    bio = user.bio or ""

    if URL_PATTERN.search(bio):

        try:
            await message.delete()
        except:
            pass

        mode, limit, penalty = await get_config(chat_id)

        count = await increment_warning(chat_id, user_id)

        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={user_id})"

        warning_text = (
            f"🚨 **Warning {count}/{limit}**\n"
            f"User: {mention}\n"
            "Reason: Link in Bio"
        )

        sent = await message.reply_text(warning_text)

        if count >= limit:
            try:
                # 🔥 ALWAYS MUTE (Ban disabled permanently)
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await sent.edit_text(
                    f"🔇 {mention} has been muted (Link In Bio)."
                )
            except:
                pass

        return

    # ================= LINK DELETE ================= #

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

    # ================= FORWARD DELETE ================= #

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

    # ================= ABUSE DELETE ================= #

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

    # ================= MEDIA SILENT DELETE ================= #

    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass


# ================= EDITED MESSAGE CHECK ================= #

@app.on_edited_message(filters.group)
async def edited_security(client: Client, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    if await is_admin(client, chat_id, user_id):
        return
    if await is_whitelisted(chat_id, user_id):
        return

    # Edited link
    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass
        return

    # Edited abuse
    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass
            return