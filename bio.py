import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, URL_PATTERN, SUPPORT_GROUP, SUPPORT_CHANNEL

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

# USERNAME REMOVE ( @username allowed )
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

    await message.reply_text(text, reply_markup=await add_group_button())

# ================= FREE COMMANDS ================= #

@app.on_message(filters.command(["free","unfree","freelist"]) & filters.group)
async def bio_commands(_, message):

    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not is_admin(member):
        return

    cmd = message.command[0].lower()

    if cmd == "free" and message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        add_bio_free(message.chat.id, uid)
        await message.reply_text("✅ User exempted from Bio Link detection.")
        return

    if cmd == "unfree" and message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        remove_bio_free(message.chat.id, uid)
        await message.reply_text("❌ User removed from Bio exemption list.")
        return

    if cmd == "freelist":
        users = bio_free_db.get(message.chat.id, set())
        if not users:
            await message.reply_text("No users in Bio exemption list.")
            return

        text = "📋 Bio Exempted Users:\n\n"
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

    # ADMIN SAFE
    if is_admin(member):
        return

    # ===== BIO CHECK (ignore only @username) =====
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
                f"🚫 𝐁𝐢𝐨 𝐋𝐢𝐧𝐤 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝\n⚠ Warning {warn}/3",
                reply_markup=await add_group_button()
            )

            if warn >= 3:
                await app.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions()
                )
                await warn_msg.edit_text(
                    "🔇 𝐔𝐬𝐞𝐫 𝐌𝐮𝐭𝐞𝐝 (𝐁𝐢𝐨 𝐕𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧)",
                    reply_markup=await add_group_button()
                )
            return

    # ===== LINK DELETE =====
    if LINK_REGEX.search(text):
        await message.delete()
        await message.reply_text(
            "🚫 𝐋𝐢𝐧𝐤 𝐑𝐞𝐦𝐨𝐯𝐞𝐝",
            reply_markup=await add_group_button()
        )
        return

    # ===== FORWARD DELETE =====
    if message.forward_date:
        await message.delete()
        await message.reply_text(
            "📤 𝐅𝐨𝐫𝐰𝐚𝐫𝐝𝐞𝐝 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐑𝐞𝐦𝐨𝐯𝐞𝐝",
            reply_markup=await add_group_button()
        )
        return

    # ===== ABUSE DELETE =====
    for word in ABUSE_WORDS:
        if word in text.lower():
            await message.delete()
            await message.reply_text(
                "⚠ 𝐈𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞 𝐑𝐞𝐦𝐨𝐯𝐞𝐝",
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
            "✏ 𝐄𝐝𝐢𝐭𝐞𝐝 𝐋𝐢𝐧𝐤 𝐑𝐞𝐦𝐨𝐯𝐞𝐝",
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
    print("Bot Running Final Stable Version ✅")
    app.run()