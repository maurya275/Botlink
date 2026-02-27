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
bio_free_db = {}

# ================= HELPERS ================= #

def get_warn(chat_id, user_id):
    return warn_db.get(chat_id, {}).get(user_id, 0)

def add_warn(chat_id, user_id):
    warn_db.setdefault(chat_id, {})
    warn_db[chat_id][user_id] = get_warn(chat_id, user_id) + 1
    return warn_db[chat_id][user_id]

def get_warn_limit(chat_id):
    return config_db.get(chat_id, 3)

def set_warn_limit(chat_id, limit):
    config_db[chat_id] = limit

def is_bio_free(chat_id, user_id):
    return user_id in bio_free_db.get(chat_id, set())

def add_bio_free(chat_id, user_id):
    bio_free_db.setdefault(chat_id, set()).add(user_id)

def remove_bio_free(chat_id, user_id):
    bio_free_db.setdefault(chat_id, set()).discard(user_id)

# ================= BUTTON ================= #

async def get_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me In Your Group",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= COMMANDS ================= #

@app.on_message(filters.command("free") & filters.group)
async def free_cmd(_, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        add_bio_free(message.chat.id, user_id)
        await message.reply_text("✅ User is now free from Bio Link detection.")

@app.on_message(filters.command("unfree") & filters.group)
async def unfree_cmd(_, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        remove_bio_free(message.chat.id, user_id)
        await message.reply_text("❌ User removed from Bio Free list.")

@app.on_message(filters.command("freelist") & filters.group)
async def freelist_cmd(_, message):
    users = bio_free_db.get(message.chat.id, set())
    if not users:
        await message.reply_text("No users in Bio Free list.")
        return
    text = "📋 Bio Free Users:\n\n"
    for u in users:
        text += f"• `{u}`\n"
    await message.reply_text(text)

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

    # ===== BIO LINK CHECK =====
    if not is_bio_free(chat_id, user_id):
        try:
            user = await app.get_chat(user_id)
            bio = user.bio or ""
        except:
            bio = ""

        if URL_PATTERN.search(bio):
            await message.delete()
            warn = add_warn(chat_id, user_id)
            limit = get_warn_limit(chat_id)

            warn_msg = await message.reply_text(
                f"🚫 **Bio Link Detected**\n"
                f"⚠ Warning {warn}/{limit}\n\n"
                f"Remove link from bio immediately.",
                reply_markup=await get_button()
            )

            if warn >= limit:
                await app.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions()
                )
                await warn_msg.edit_text(
                    "🔇 User Muted (Bio Link Violation)",
                    reply_markup=await get_button()
                )
            return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🔗 **Link Sharing Is Not Allowed Here.**\n"
            "Please avoid posting external links.",
            reply_markup=await get_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 **Forwarded Messages Are Restricted.**",
            reply_markup=await get_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ **Inappropriate Language Detected.**\n"
                "Maintain respectful conversation.",
                reply_markup=await get_button()
            )
            return

    # ===== MEDIA AUTO DELETE (SILENT) =====
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
    print("Bot Running Final Stable Version ✅")
    app.run()