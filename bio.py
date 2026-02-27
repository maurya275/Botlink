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

# ================= SETTINGS ================= #

ABUSE_WORDS = [
    "madarchod","bhosdike","chutiya","mc","bc",
    "gandu","randi","harami","fuck","shit","bitch"
]

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)

MEDIA_DELETE_TIME = 50

# ================= DATABASE (Memory Based) ================= #

warn_db = {}
config_db = {}
whitelist_db = {}

# ================= HELPERS ================= #

def get_warn(chat_id, user_id):
    return warn_db.get(chat_id, {}).get(user_id, 0)

def add_warn(chat_id, user_id):
    warn_db.setdefault(chat_id, {})
    warn_db[chat_id][user_id] = get_warn(chat_id, user_id) + 1
    return warn_db[chat_id][user_id]

def reset_warn(chat_id, user_id):
    if chat_id in warn_db and user_id in warn_db[chat_id]:
        warn_db[chat_id][user_id] = 0

def get_config(chat_id):
    return config_db.get(chat_id, {"warn_limit":3})

def set_warn_limit(chat_id, limit):
    config_db.setdefault(chat_id, {})
    config_db[chat_id]["warn_limit"] = limit

def is_whitelisted(chat_id, user_id):
    return user_id in whitelist_db.get(chat_id, set())

def add_whitelist(chat_id, user_id):
    whitelist_db.setdefault(chat_id, set()).add(user_id)

def remove_whitelist(chat_id, user_id):
    whitelist_db.setdefault(chat_id, set()).discard(user_id)

# ================= COMMANDS ================= #

@app.on_message(filters.command("start"))
async def start(_, message):
    bot = await app.get_me()
    add_link = f"https://t.me/{bot.username}?startgroup=true"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=add_link)]
    ])

    await message.reply_text(
        "🔥 Advanced Bio + Security Bot Active 🔥\n\nUse /help",
        reply_markup=kb
    )

@app.on_message(filters.command("help"))
async def help_cmd(_, message):
    await message.reply_text(
        "/setwarn 5\n"
        "/whitelist (reply)\n"
        "/unwhitelist (reply)\n\n"
        "Security Active:\n"
        "• Bio Link Warn\n"
        "• Link Delete\n"
        "• Abuse Delete\n"
        "• Forward Delete\n"
        "• Edited Check\n"
        "• Media Auto Delete"
    )

@app.on_message(filters.command("setwarn") & filters.group)
async def setwarn(_, message):
    if not message.reply_to_message and len(message.command) == 2:
        limit = int(message.command[1])
        set_warn_limit(message.chat.id, limit)
        await message.reply_text(f"Warn limit set to {limit}")

@app.on_message(filters.command("whitelist") & filters.group)
async def whitelist(_, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        add_whitelist(message.chat.id, user_id)
        await message.reply_text("User whitelisted.")

@app.on_message(filters.command("unwhitelist") & filters.group)
async def unwhitelist(_, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        remove_whitelist(message.chat.id, user_id)
        await message.reply_text("User removed from whitelist.")

# ================= MAIN SECURITY ================= #

@app.on_message(filters.group & ~filters.service)
async def security(_, message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    member = await app.get_chat_member(chat_id, user_id)
    if member.status in ["administrator", "creator"]:
        return

    if is_whitelisted(chat_id, user_id):
        return

    # ===== BIO CHECK =====
    try:
        user = await app.get_chat(user_id)
        bio = user.bio or ""
    except:
        bio = ""

    if URL_PATTERN.search(bio):
        await message.delete()
        warn = add_warn(chat_id, user_id)
        limit = get_config(chat_id)["warn_limit"]

        warn_msg = await message.reply_text(
            f"⚠ Warning {warn}/{limit}\nLink in bio not allowed."
        )

        if warn >= limit:
            await app.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions()
            )
            await warn_msg.edit_text("🔇 User Muted (Bio Link)")

        return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            return

    # ===== MEDIA AUTO DELETE =====
    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass

# ===== EDITED CHECK =====

@app.on_edited_message(filters.group)
async def edited(_, message):
    text = message.text or message.caption or ""
    if LINK_REGEX.search(text):
        await message.delete()
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Successfully ✅")
    app.run()