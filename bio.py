import asyncio
import re
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "advanced_security_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= SUPPORT ================= #

SUPPORT_CHANNEL = "https://t.me/YourChannelUsername"
SUPPORT_GROUP = "https://t.me/YourGroupUsername"

# ================= SETTINGS ================= #

ABUSE_WORDS = [
    "madarchod","bhosdike","chutiya","mc","bc",
    "gandu","randi","harami","fuck","shit","bitch"
]

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/)",
    re.IGNORECASE
)

MEDIA_DELETE_TIME = 50
warnings = {}

# ================= HELPERS ================= #

def is_admin(member):
    return member.status in ["administrator", "creator"]

async def add_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= MAIN SECURITY ================= #

@app.on_message(filters.group & ~filters.service)
async def security(_, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    member = await app.get_chat_member(chat_id, user_id)
    if is_admin(member):
        return

    # ================= MEDIA AUTO DELETE ================= #

    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass
        return

    # ================= BIO LINK CHECK (3 WARNING + MUTE) ================= #

    try:
        user = await app.get_chat(user_id)
        bio = user.bio or ""
    except:
        bio = ""

    if LINK_REGEX.search(bio):

        key = f"{chat_id}_{user_id}"
        warnings[key] = warnings.get(key, 0) + 1
        count = warnings[key]

        await message.delete()

        if count < 3:
            await message.reply_text(
                f"⚠️ 𝐁𝐈𝐎 𝐋𝐈𝐍𝐊 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃\n\n"
                f"🚫 Please remove link from your bio immediately.\n"
                f"⚡ 𝐖𝐚𝐫𝐧𝐢𝐧𝐠: {count}/3\n\n"
                f"🔒 After 3 warnings you will be muted for 30 minutes.",
                reply_markup=await add_button()
            )
        else:
            until_time = datetime.now() + timedelta(minutes=30)

            await app.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(),
                until_date=until_time
            )

            warnings[key] = 0

            await message.reply_text(
                "🔇 𝐔𝐒𝐄𝐑 𝐌𝐔𝐓𝐄𝐃\n\n"
                "⛔ 3/3 Warnings Completed\n"
                "🕒 Muted For 30 Minutes\n\n"
                "Remove link from bio before messaging again.",
                reply_markup=await add_button()
            )
        return

    # ================= LINK MESSAGE DELETE ================= #

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 𝐋𝐈𝐍𝐊 𝐑𝐄𝐌𝐎𝐕𝐄𝐃\n\n"
            "🔐 Sharing links is not allowed in this group.\n"
            "⚡ Keep the community clean & safe.",
            reply_markup=await add_button()
        )
        return

    # ================= ABUSE CHECK ================= #

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠️ 𝐈𝐍𝐀𝐏𝐏𝐑𝐎𝐏𝐑𝐈𝐀𝐓𝐄 𝐋𝐀𝐍𝐆𝐔𝐀𝐆𝐄\n\n"
                "🚫 Abusive words are strictly prohibited.\n"
                "💬 Please maintain respectful conversation.",
                reply_markup=await add_button()
            )
            return

# ================= EDIT CHECK ================= #

@app.on_edited_message(filters.group)
async def edited(_, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    member = await app.get_chat_member(chat_id, user_id)
    if is_admin(member):
        return

    # ===== EDITED LINK ===== #

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "✏️ 𝐄𝐃𝐈𝐓𝐄𝐃 𝐋𝐈𝐍𝐊 𝐑𝐄𝐌𝐎𝐕𝐄𝐃\n\n"
            "🚫 Editing message to add links is not allowed.\n"
            "🔐 Group protection active.",
            reply_markup=await add_button()
        )
        return

    # ===== EDITED ABUSE ===== #

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "✏️ 𝐄𝐃𝐈𝐓𝐄𝐃 𝐀𝐁𝐔𝐒𝐈𝐕𝐄 𝐌𝐄𝐒𝐒𝐀𝐆𝐄\n\n"
                "⚠️ Abusive language detected after editing.\n"
                "💬 Respect group guidelines.",
                reply_markup=await add_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Final Fully Stable Version ✅")
    app.run()