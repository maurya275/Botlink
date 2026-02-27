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
warnings = {}   # warning storage

# ================= HELPERS ================= #

def is_admin(member):
    return member.status in ["administrator", "creator"]

async def start_buttons():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("👥 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_GROUP)
        ]
    ])

async def add_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start(_, message):

    text = (
        "━━━━━━━━━━━━━━━━━━\n"
        "✦ 𝐁𝐎𝐓 𝐋𝐈𝐍𝐊 𝐑𝐄𝐌𝐎𝐕𝐄𝐑 ✦\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🛡 Elite Group Security System\n\n"
        "🚫 Auto Link Protection\n"
        "🔎 Bio Link Scanner (3 Warning + Mute)\n"
        "🔞 Abuse Filter\n"
        "📤 Forward Control\n"
        "⚡ Real-Time Monitoring\n\n"
        "💎 Premium • Fast • Stable"
    )

    await message.reply_text(text, reply_markup=await start_buttons())

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

    # ===== BIO LINK CHECK WITH WARNING SYSTEM ===== #

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
                f"⚠ 𝐁𝐈𝐎 𝐋𝐈𝐍𝐊 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃\n\n"
                f"🚫 Please remove link from your bio.\n"
                f"⚠ Warning: {count}/3\n\n"
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

    # ===== NORMAL LINK CHECK ===== #

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 Link Removed\n🔐 Sharing links is not allowed.",
            reply_markup=await add_button()
        )
        return

    # ===== ABUSE CHECK ===== #

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ Inappropriate Language Removed\n💬 Maintain respectful conversation.",
                reply_markup=await add_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running With 3 Warning + 30 Min Mute System ✅")
    app.run()