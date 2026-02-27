import asyncio
import re
import time
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

# ===== WARNING STORAGE =====
bio_warnings = {}

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
        "🔎 Bio Link Monitoring\n"
        "🔞 Abuse Filter\n"
        "⚡ Real-Time Protection\n\n"
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

    # ✅ ADMIN SAFE
    if is_admin(member):
        return

    # ===== BIO CHECK WITH 3 WARNING SYSTEM =====
    try:
        user = await app.get_chat(user_id)
        bio = user.bio or ""
    except:
        bio = ""

    if LINK_REGEX.search(bio):

        count = bio_warnings.get(user_id, 0) + 1
        bio_warnings[user_id] = count

        if count < 3:
            await message.reply_text(
                f"⚠ 𝗕𝗜𝗢 𝗟𝗜𝗡𝗞 𝗪𝗔𝗥𝗡𝗜𝗡𝗚 ({count}/3)\n\n"
                "🚫 Your profile contains a restricted link.\n"
                "Please remove it to avoid mute.",
                reply_markup=await add_button()
            )
            return

        # 3rd time → mute
        try:
            await app.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 1800
            )
        except:
            pass

        await message.reply_text(
            "🔒 𝗨𝗦𝗘𝗥 𝗠𝗨𝗧𝗘𝗗\n\n"
            "You ignored 3 warnings.\n"
            "⏳ Muted for 30 minutes.",
            reply_markup=await add_button()
        )

        bio_warnings[user_id] = 0
        return

    # ===== NORMAL LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 Link Removed\n"
            "🔐 Sharing links is not allowed.",
            reply_markup=await add_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 Forwarded Message Removed\n"
            "🔒 Forwarding is restricted.",
            reply_markup=await add_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ Inappropriate Language Removed\n"
                "💬 Maintain respectful conversation.",
                reply_markup=await add_button()
            )
            return

    # ===== MEDIA AUTO DELETE =====
    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Final Version ✅")
    app.run()