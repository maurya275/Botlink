import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, URL_PATTERN

app = Client(
    "advanced_security_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= SUPPORT BUTTONS ================= #

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

warn_db = {}
bio_free_db = {}

# ================= HELPERS ================= #

def is_admin(member):
    return member.status in ["administrator", "creator"]

def is_bio_free(chat_id, user_id):
    return user_id in bio_free_db.get(chat_id, set())

def add_bio_free(chat_id, user_id):
    bio_free_db.setdefault(chat_id, set()).add(user_id)

def remove_bio_free(chat_id, user_id):
    bio_free_db.setdefault(chat_id, set()).discard(user_id)

def get_warn(chat_id, user_id):
    return warn_db.get(chat_id, {}).get(user_id, 0)

def add_warn(chat_id, user_id):
    warn_db.setdefault(chat_id, {})
    warn_db[chat_id][user_id] = get_warn(chat_id, user_id) + 1
    return warn_db[chat_id][user_id]

async def main_buttons():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("👥 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_GROUP)
        ]
    ])

async def add_group_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start(_, message):

    text = (
        "╔════════════════════════════╗\n"
        " ✨ 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐆𝐑𝐎𝐔𝐏 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 ✨\n"
        "╚════════════════════════════╝\n\n"

        "🛡 𝗕𝗜𝗢 𝗟𝗜𝗡𝗞 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡\n"
        "🔗 𝗔𝗡𝗧𝗜 𝗟𝗜𝗡𝗞 𝗦𝗬𝗦𝗧𝗘𝗠\n"
        "🚫 𝗔𝗡𝗧𝗜 𝗔𝗕𝗨𝗦𝗘 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡\n"
        "📤 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 𝗖𝗢𝗡𝗧𝗥𝗢𝗟\n"
        "✏ 𝗘𝗗𝗜𝗧 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬\n"
        "🗑 𝗠𝗘𝗗𝗜𝗔 𝗖𝗟𝗘𝗔𝗡𝗨𝗣\n\n"

        "⚡ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 • 𝗙𝗮𝘀𝘁 • 𝗦𝘁𝗮𝗯𝗹𝗲"
    )

    await message.reply_text(text, reply_markup=await main_buttons())

# ================= MAIN SECURITY ================= #

@app.on_message(filters.group & ~filters.service)
async def security(_, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    member = await app.get_chat_member(chat_id, user_id)

    # ADMIN SAFE (ignore admin bio link)
    if is_admin(member):
        return

    # ===== BIO CHECK =====
    if not is_bio_free(chat_id, user_id):
        try:
            user = await app.get_chat(user_id)
            bio = user.bio or ""
        except:
            bio = ""

        if LINK_REGEX.search(bio):
            await message.delete()
            warn = add_warn(chat_id, user_id)

            warn_msg = await message.reply_text(
                "╔════════════════════╗\n"
                "🚫 𝐁𝐢𝐨 𝐋𝐢𝐧𝐤 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝\n"
                "╚════════════════════╝\n"
                f"⚠ 𝐖𝐚𝐫𝐧𝐢𝐧𝐠: {warn}/3\n"
                "🔎 Please remove link from bio.",
                reply_markup=await add_group_button()
            )

            if warn >= 3:
                await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await warn_msg.edit_text(
                    "🔇 𝐔𝐬𝐞𝐫 𝐌𝐮𝐭𝐞𝐝\n"
                    "Reason: Repeated Bio Violations",
                    reply_markup=await add_group_button()
                )
            return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "╔════════════════════╗\n"
            "🚫 𝐋𝐢𝐧𝐤 𝐑𝐞𝐦𝐨𝐯𝐞𝐝\n"
            "╚════════════════════╝\n"
            "🔐 Links are not allowed here.",
            reply_markup=await add_group_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 𝐅𝐨𝐫𝐰𝐚𝐫𝐝𝐞𝐝 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐑𝐞𝐦𝐨𝐯𝐞𝐝\n"
            "🔒 Forwarding is restricted.",
            reply_markup=await add_group_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "╔════════════════════╗\n"
                "⚠ 𝐈𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞\n"
                "╚════════════════════╝\n"
                "💬 Please maintain respectful chat.",
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
    if is_admin(member):
        return

    text = message.text or message.caption or ""

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "✏ 𝐄𝐝𝐢𝐭𝐞𝐝 𝐋𝐢𝐧𝐤 𝐑𝐞𝐦𝐨𝐯𝐞𝐝\n"
            "🔐 Editing to add links is not allowed.",
            reply_markup=await add_group_button()
        )
        return

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "✏ 𝐄𝐝𝐢𝐭𝐞𝐝 𝐈𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞 𝐑𝐞𝐦𝐨𝐯𝐞𝐝",
                reply_markup=await add_group_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Premium Version ✅")
    app.run()