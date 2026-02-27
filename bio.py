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

async def start_buttons():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Add Me To Your Group ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("📢 Support Channel", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("👥 Support Group", url=SUPPORT_GROUP)
        ]
    ])

async def add_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Add Me To Your Group ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start(_, message):

    text = (
        "╔══════════════════════╗\n"
        "  ✨ 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐆𝐑𝐎𝐔𝐏 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 ✨\n"
        "╚══════════════════════╝\n\n"
        "🛡 𝗕𝗜𝗢 𝗟𝗜𝗡𝗞 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡\n"
        "   └ Warn + Auto Mute System\n\n"
        "🔗 𝗔𝗡𝗧𝗜 𝗟𝗜𝗡𝗞 𝗦𝗬𝗦𝗧𝗘𝗠\n"
        "   └ Instant Link Removal\n\n"
        "🚫 𝗔𝗡𝗧𝗜 𝗔𝗕𝗨𝗦𝗘 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡\n"
        "   └ Smart Language Filter\n\n"
        "📤 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 𝗖𝗢𝗡𝗧𝗥𝗢𝗟\n"
        "   └ Auto Forward Delete\n\n"
        "✏ 𝗘𝗗𝗜𝗧 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬\n"
        "   └ Edited Link Detection\n\n"
        "🗑 𝗠𝗘𝗗𝗜𝗔 𝗖𝗟𝗘𝗔𝗡𝗨𝗣\n"
        "   └ Silent Auto Delete (50s)\n\n"
        "⚡ Fast • Stable • Professional Grade Protection\n\n"
        f"📢 Support Channel: {SUPPORT_CHANNEL}\n"
        f"👥 Support Group: {SUPPORT_GROUP}"
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

    # ===== INSTANT LINK DELETE (NO 50s WAIT) ===== #

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 𝐋𝐈𝐍𝐊 𝐒𝐇𝐀𝐑𝐈𝐍𝐆 𝐍𝐎𝐓 𝐀𝐋𝐋𝐎𝐖𝐄𝐃 𝐇𝐄𝐑𝐄\n\n"
            "🔐 Links are strictly prohibited in this group.\n"
            "⚡ Security System Active.",
            reply_markup=await add_button()
        )
        return

    # ===== MEDIA AUTO DELETE (ONLY MEDIA) ===== #

    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass
        return

    # ===== BIO LINK CHECK (3 WARN + 30 MIN MUTE) ===== #

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
                f"⚡ Warning: {count}/3\n"
                f"Remove link from bio immediately.\n\n"
                f"🔇 After 3 warnings you will be muted for 30 minutes.",
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

    # ===== ABUSE FILTER ===== #

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠️ 𝐀𝐁𝐔𝐒𝐈𝐕𝐄 𝐋𝐀𝐍𝐆𝐔𝐀𝐆𝐄 𝐍𝐎𝐓 𝐀𝐋𝐋𝐎𝐖𝐄𝐃\n\n"
                "💬 Maintain respectful conversation.",
                reply_markup=await add_button()
            )
            return

# ===== EDIT CHECK ===== #

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
            "✏ 𝐄𝐃𝐈𝐓𝐄𝐃 𝐋𝐈𝐍𝐊 𝐑𝐄𝐌𝐎𝐕𝐄𝐃\n\n"
            "🔐 Editing to add links is not allowed.",
            reply_markup=await add_button()
        )
        return

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "✏ 𝐄𝐃𝐈𝐓𝐄𝐃 𝐀𝐁𝐔𝐒𝐈𝐕𝐄 𝐌𝐄𝐒𝐒𝐀𝐆𝐄\n\n"
                "⚠ Respect group rules.",
                reply_markup=await add_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Stable Final Version ✅")
    app.run()