# ================= UNIFIED GROUP SECURITY ================= #

@app.on_message(filters.group & ~filters.service, group=1)
async def unified_security(client: Client, message):

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

    # ================= BIO LINK DETECTOR ================= #

    try:
        user = await client.get_chat(user_id)
        bio = user.bio or ""
    except:
        bio = ""

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
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await warn_msg.edit_text("🔇 User muted (Link in Bio)")
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
            "🔗 Link Deleted Successfully!",
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
            "📤 Forward Message Deleted!",
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
                "⚠️ Abuse Message Deleted!",
                reply_markup=promo_kb
            )
            return

    # ================= MEDIA AUTO DELETE (Silent) ================= #

    if message.media:
        await asyncio.sleep(50)
        try:
            await message.delete()
        except:
            pass


# ================= EDITED MESSAGE SECURITY ================= #

@app.on_edited_message(filters.group, group=2)
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

    bot = await client.get_me()
    promo_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

    # LINK IN EDIT
    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except:
            pass

        await message.reply_text(
            "✏️ Edited Link Deleted!",
            reply_markup=promo_kb
        )
        return

    # ABUSE IN EDIT
    lowered = text.lower()
    for word in ABUSE_WORDS:
        if word in lowered:
            try:
                await message.delete()
            except:
                pass

            await message.reply_text(
                "⚠️ Edited Abuse Deleted!",
                reply_markup=promo_kb
            )
            return