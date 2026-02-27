import asyncio
import re
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
        "✏ Edit-Time Detection\n"
        "📤 Forward Control\n"
        "🔞 Abuse Filter\n"
        "🔎 Bio Link Scanner\n"
        "👑 Admin Safe Mode\n"
        "⚡ Real-Time Monitoring\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "💎 Premium • Fast • Stable\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "🚀 Add Me To Your Group\n"
        "For Smart Automatic Protection"
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

    try:
        user = await app.get_chat(user_id)
        bio = user.bio or ""
    except:
        bio = ""

    if LINK_REGEX.search(bio):
        await message.delete()
        await message.reply_text(
            "🚫 Bio Link Detected\n"
            "⚠ Please remove link from your bio.",
            reply_markup=await add_button()
        )
        return

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 Link Removed\n"
            "🔐 Sharing links is not allowed.",
            reply_markup=await add_button()
        )
        return

    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 Forwarded Message Removed\n"
            "🔒 Forwarding is restricted.",
            reply_markup=await add_button()
        )
        return

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ Inappropriate Language Removed\n"
                "💬 Maintain respectful conversation.",
                reply_markup=await add_button()
            )
            return

    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass

# ================= EDIT CHECK ================= #

@app.on_edited_message(filters.group)
async def edited(_, message):

    if not message.from_user:
        return

    member = await app.get_chat_member(message.chat.id, message.from_user.id)

    if is_admin(member):
        return

    text = message.text or message.caption or ""

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "✏ Edited Link Removed\n"
            "🔐 Editing to add links is not allowed.",
            reply_markup=await add_button()
        )
        return

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "✏ Edited Inappropriate Language Removed\n"
                "💬 Respect group guidelines.",
                reply_markup=await add_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Final Premium Stable Version ✅")
    app.run()