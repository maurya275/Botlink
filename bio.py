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

warn_db = {}
bio_free_db = {}
warn_limit_db = {}

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

def get_warn_limit(chat_id):
    return warn_limit_db.get(chat_id, 3)

async def premium_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Add Me To Your Group ✨",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= PREMIUM MESSAGES ================= #

LINK_MSG = (
    "━━━━━━━━━━━━━━━━━━━\n"
    "🚫 𝑳𝒊𝒏𝒌 𝑫𝒆𝒕𝒆𝒄𝒕𝒆𝒅 & 𝑹𝒆𝒎𝒐𝒗𝒆𝒅\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "🔗 Sharing external links is restricted.\n"
    "⚡ Please maintain group quality.\n"
)

ABUSE_MSG = (
    "━━━━━━━━━━━━━━━━━━━\n"
    "⚠ 𝑰𝒏𝒂𝒑𝒑𝒓𝒐𝒑𝒓𝒊𝒂𝒕𝒆 𝑳𝒂𝒏𝒈𝒖𝒂𝒈𝒆 𝑹𝒆𝒎𝒐𝒗𝒆𝒅\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "🛡 Respectful conversation is required.\n"
)

FORWARD_MSG = (
    "━━━━━━━━━━━━━━━━━━━\n"
    "📤 𝑭𝒐𝒓𝒘𝒂𝒓𝒅𝒆𝒅 𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝑹𝒆𝒎𝒐𝒗𝒆𝒅\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "⚡ Forwarded content is not allowed.\n"
)

EDIT_LINK_MSG = "✏ 𝑬𝒅𝒊𝒕𝒆𝒅 𝑳𝒊𝒏𝒌 𝑹𝒆𝒎𝒐𝒗𝒆𝒅."
EDIT_ABUSE_MSG = "✏ 𝑬𝒅𝒊𝒕𝒆𝒅 𝑰𝒏𝒂𝒑𝒑𝒓𝒐𝒑𝒓𝒊𝒂𝒕𝒆 𝑳𝒂𝒏𝒈𝒖𝒂𝒈𝒆 𝑹𝒆𝒎𝒐𝒗𝒆𝒅."

# ================= FREE COMMANDS FIXED ================= #

@app.on_message(filters.group & filters.command(["free","unfree","freelist"]))
async def free_system(_, message):

    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not is_admin(member):
        return

    cmd = message.command[0].lower()

    if cmd == "free" and message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        add_bio_free(message.chat.id, user_id)
        await message.reply_text("✅ User exempted from Bio Link detection.")
        return

    if cmd == "unfree" and message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        remove_bio_free(message.chat.id, user_id)
        await message.reply_text("❌ User removed from Bio exemption list.")
        return

    if cmd == "freelist":
        users = bio_free_db.get(message.chat.id, set())
        if not users:
            await message.reply_text("No users in Bio exemption list.")
            return
        text = "📋 **Bio Exempted Users:**\n\n"
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
    if is_admin(member):
        return

    # ===== BIO CHECK =====
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

            msg = await message.reply_text(
                f"🚫 Bio Link Detected\n⚠ Warning {warn}/{limit}",
                reply_markup=await premium_button()
            )

            if warn >= limit:
                await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await msg.edit_text(
                    "🔇 User Muted (Bio Violation)",
                    reply_markup=await premium_button()
                )
            return

    # ===== LINK =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(LINK_MSG, reply_markup=await premium_button())
        return

    # ===== FORWARD =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(FORWARD_MSG, reply_markup=await premium_button())
        return

    # ===== ABUSE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(ABUSE_MSG, reply_markup=await premium_button())
            return

    # ===== MEDIA SILENT =====
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
        await message.reply_text(EDIT_LINK_MSG, reply_markup=await premium_button())
        return

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(EDIT_ABUSE_MSG, reply_markup=await premium_button())
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Premium Final Version ✅")
    app.run()