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
        "✨ 𝗔𝗗𝗩𝗔𝗡𝗖𝗘𝗗 𝗚𝗥𝗢𝗨𝗣 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 ✨\n\n"

        "🛡 𝗕𝗶𝗼 𝗟𝗶𝗻𝗸 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n"
        "🔗 𝗔𝗻𝘁𝗶 𝗟𝗶𝗻𝗸 𝗦𝘆𝘀𝘁𝗲𝗺\n"
        "🚫 𝗔𝗻𝘁𝗶 𝗔𝗯𝘂𝘀𝗲 𝗙𝗶𝗹𝘁𝗲𝗿\n"
        "📤 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗖𝗼𝗻𝘁𝗿𝗼𝗹\n"
        "✏ 𝗘𝗱𝗶𝘁 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n"
        "🗑 𝗠𝗲𝗱𝗶𝗮 𝗔𝘂𝘁𝗼 𝗖𝗹𝗲𝗮𝗻\n\n"

        "⚡ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 • 𝗙𝗮𝘀𝘁 • 𝗦𝘁𝗮𝗯𝗹𝗲"
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

    # ✅ ADMIN FULLY SAFE (bio ignored)
    if is_admin(member):
        return

    # ===== BIO CHECK =====
    try:
        user = await app.get_chat(user_id)
        bio = user.bio or ""
    except:
        bio = ""

    if LINK_REGEX.search(bio):
        await message.delete()
        await message.reply_text(
            "🚫 𝗕𝗶𝗼 𝗟𝗶𝗻𝗸 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱\n"
            "⚠ Please remove link from your bio.\n"
            "🔒 Continued violation may result in mute.",
            reply_markup=await add_button()
        )
        return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 𝗟𝗶𝗻𝗸 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
            "🔐 Sharing links is not allowed here.",
            reply_markup=await add_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 𝗙𝗼𝗿𝘄𝗮𝗿𝗱𝗲𝗱 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
            "🔒 Forwarding is restricted in this group.",
            reply_markup=await add_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ 𝗜𝗻𝗮𝗽𝗽𝗿𝗼𝗽𝗿𝗶𝗮𝘁𝗲 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
                "💬 Please maintain respectful conversation.",
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

# ================= EDIT CHECK ================= #

@app.on_edited_message(filters.group)
async def edited(_, message):

    if not message.from_user:
        return

    member = await app.get_chat_member(message.chat.id, message.from_user.id)

    # ✅ ADMIN SAFE
    if is_admin(member):
        return

    text = message.text or message.caption or ""

    # Edited Link
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "✏ 𝗘𝗱𝗶𝘁𝗲𝗱 𝗟𝗶𝗻𝗸 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
            "🔐 Editing messages to add links is not allowed.",
            reply_markup=await add_button()
        )
        return

    # Edited Abuse
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "✏ 𝗘𝗱𝗶𝘁𝗲𝗱 𝗜𝗻𝗮𝗽𝗽𝗿𝗼𝗽𝗿𝗶𝗮𝘁𝗲 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
                "💬 Respect group guidelines.",
                reply_markup=await add_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Final Premium Stable Version ✅")
    app.run()