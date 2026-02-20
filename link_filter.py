from config import URL_PATTERN, DEFAULT_WARNING_LIMIT, DEFAULT_PUNISHMENT
from pyrogram.errors import ChatAdminRequired


async def check_and_delete_link(app, message, add_warn):

    text = message.text or message.caption

    if not text:
        return

    # Detect link
    if not URL_PATTERN.search(text):
        return

    try:
        await message.delete()
    except:
        return

    user = message.from_user

    # If anonymous admin or no user
    if not user:
        return

    warn_count = await add_warn(message.chat.id, user.id)

    if warn_count >= DEFAULT_WARNING_LIMIT:
        try:
            if DEFAULT_PUNISHMENT == "mute":
                await app.restrict_chat_member(
                    message.chat.id,
                    user.id,
                    permissions={}
                )
            elif DEFAULT_PUNISHMENT == "ban":
                await app.ban_chat_member(
                    message.chat.id,
                    user.id
                )
        except ChatAdminRequired:
            pass

    try:
        await message.chat.send_message(
            f"⚠️ {user.mention} link not allowed.\n"
            f"Warn: {warn_count}/{DEFAULT_WARNING_LIMIT}"
        )
    except:
        pass