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

# Only real links (username allowed)
LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/)",
    re.IGNORECASE
)

MEDIA_DELETE_TIME = 50

warn_db = {}
bio_free_db = {}

# ================= HELPERS ================= #

def is_admin(member):
    return member.status in ["administrator", "creator"]

async def add_group_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

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

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start(_, message):

    text = (
        "╔══════════════════════════════╗\n"
        "║      ✨ 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 ✨      ║\n"
        "╠══════════════════════════════╣\n"
        "║ 🛡  Bio Link Protection       ║\n"
        "║ 🔗  Anti Link System          ║\n"
        "║ 🚫  Abuse Filter              ║\n"
        "║ 📤  Forward Control           ║\n"
        "║ ✏  Edit Protection            ║\n"
        "║ 🗑  Media Auto Cleanup         ║\n"
        "╠══════════════════════════════╣\n"
        "║ ⚡ Fast • Stable • Premium     ║\n"
        "╚══════════════════════════════╝"
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

    # 🔥 ADMIN FULLY SAFE (bio ignored completely)
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
            "╔════════════════════════╗\n"
            "║ 🚫  𝐁𝐢𝐨 𝐋𝐢𝐧𝐤 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝        ║\n"
            "╠════════════════════════╣\n"
            "║ 🔎 Remove link from bio ║\n"
            "║ ⚠ Repeated = Auto Mute  ║\n"
            "╚════════════════════════╝",
            reply_markup=await add_group_button()
        )
        return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()

        await message.reply_text(
            "╔════════════════════════╗\n"
            "║ 🚫  𝐋𝐢𝐧𝐤 𝐑𝐞𝐦𝐨𝐯𝐞𝐝              ║\n"
            "╠════════════════════════╣\n"
            "║ 🔐 Links not allowed    ║\n"
            "╚════════════════════════╝",
            reply_markup=await add_group_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()

        await message.reply_text(
            "╔════════════════════════╗\n"
            "║ 📤  𝐅𝐨𝐫𝐰𝐚𝐫𝐝 𝐑𝐞𝐦𝐨𝐯𝐞𝐝          ║\n"
            "╠════════════════════════╣\n"
            "║ 🔒 Forwarding blocked   ║\n"
            "╚════════════════════════╝",
            reply_markup=await add_group_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()

            await message.reply_text(
                "╔════════════════════════╗\n"
                "║ ⚠  𝐈𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐋𝐚𝐧𝐠.        ║\n"
                "╠════════════════════════╣\n"
                "║ 💬 Maintain Respect     ║\n"
                "╚════════════════════════╝",
                reply_markup=await add_group_button()
            )
            return

    # ===== MEDIA SILENT =====
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

    # ADMIN SAFE
    if is_admin(member):
        return

    text = message.text or message.caption or ""

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "╔════════════════════════╗\n"
            "║ ✏  𝐄𝐝𝐢𝐭𝐞𝐝 𝐋𝐢𝐧𝐤 𝐑𝐞𝐦𝐨𝐯𝐞𝐝      ║\n"
            "╚════════════════════════╝",
            reply_markup=await add_group_button()
        )

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Premium Final Version ✅")
    app.run()