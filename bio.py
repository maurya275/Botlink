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

def get_warn(chat_id, user_id):
    return warn_db.get(chat_id, {}).get(user_id, 0)

def add_warn(chat_id, user_id):
    warn_db.setdefault(chat_id, {})
    warn_db[chat_id][user_id] = get_warn(chat_id, user_id) + 1
    return warn_db[chat_id][user_id]

def get_warn_limit(chat_id):
    return warn_limit_db.get(chat_id, 3)

def is_admin(member):
    return member.status in ["administrator", "creator"]

def is_bio_free(chat_id, user_id):
    return user_id in bio_free_db.get(chat_id, set())

def add_bio_free(chat_id, user_id):
    bio_free_db.setdefault(chat_id, set()).add(user_id)

def remove_bio_free(chat_id, user_id):
    bio_free_db.setdefault(chat_id, set()).discard(user_id)

async def get_button():
    bot = await app.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me In Your Group",
                              url=f"https://t.me/{bot.username}?startgroup=true")]
    ])

# ================= START ================= #

@app.on_message(filters.command("start"))
async def start(_, message):
    text = (
        "✨ **Advanced Bio Protection & Security Bot** ✨\n\n"
        "🛡 Smart Bio Link Detection (Warn + Auto Mute)\n"
        "🔗 Instant Link Removal\n"
        "🚫 Abuse Language Protection\n"
        "📤 Forward Message Restriction\n"
        "✏ Edited Message Security\n"
        "🗑 Auto Media Cleanup (Silent)\n\n"
        "⚡ Fast • Secure • Professional\n"
        "Use /help to see commands."
    )

    await message.reply_text(text, reply_markup=await get_button())

# ================= HELP ================= #

@app.on_message(filters.command("help"))
async def help_cmd(_, message):
    await message.reply_text(
        "**Admin Commands:**\n"
        "/free (reply)\n"
        "/unfree (reply)\n"
        "/freelist\n"
    )

# ================= FREE COMMANDS ================= #

@app.on_message(filters.command("free") & filters.group)
async def free_cmd(_, message):
    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not is_admin(member):
        return

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        add_bio_free(message.chat.id, user_id)
        await message.reply_text("✅ User is now exempted from Bio Link detection.")

@app.on_message(filters.command("unfree") & filters.group)
async def unfree_cmd(_, message):
    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not is_admin(member):
        return

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        remove_bio_free(message.chat.id, user_id)
        await message.reply_text("❌ User removed from Bio Free list.")

@app.on_message(filters.command("freelist") & filters.group)
async def freelist_cmd(_, message):
    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not is_admin(member):
        return

    users = bio_free_db.get(message.chat.id, set())
    if not users:
        await message.reply_text("No users in Bio Free list.")
        return

    text = "📋 **Bio Free Users:**\n\n"
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

            warn_msg = await message.reply_text(
                f"🚫 **Bio Link Detected**\n"
                f"⚠ Warning {warn}/{limit}",
                reply_markup=await get_button()
            )

            if warn >= limit:
                await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await warn_msg.edit_text(
                    "🔇 User Muted (Bio Link Violation)",
                    reply_markup=await get_button()
                )
            return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🔗 **Link Deleted Successfully.**",
            reply_markup=await get_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 **Forwarded Message Deleted.**",
            reply_markup=await get_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ **Inappropriate Language Deleted.**",
                reply_markup=await get_button()
            )
            return

    # ===== MEDIA SILENT DELETE =====
    if message.media:
        await asyncio.sleep(MEDIA_DELETE_TIME)
        try:
            await message.delete()
        except:
            pass

# ===== EDITED CHECK WITH MESSAGE =====

@app.on_edited_message(filters.group)
async def edited(_, message):

    if not message.from_user:
        return

    text = message.text or message.caption or ""

    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if is_admin(member):
        return

    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "✏ **Edited Link Deleted.**",
            reply_markup=await get_button()
        )
        return

    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "✏ **Edited Inappropriate Language Deleted.**",
                reply_markup=await get_button()
            )
            return

# ================= RUN ================= #

if __name__ == "__main__":
    print("Bot Running Final Premium Version ✅")
    app.run()