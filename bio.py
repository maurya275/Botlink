import re
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)
from pyrogram.enums import ChatMemberStatus
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    BOT_USERNAME,
    SUPPORT_GROUP,
    SUPPORT_CHANNEL
)

app = Client(
    "PremiumModeratorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= STORAGE =================

free_users = {}

# ================= REGEX =================

REAL_LINK_REGEX = r"(https?://|t\.me/|telegram\.me/|www\.)"
USERNAME_ONLY_REGEX = r"^@\w+$"

ABUSE_WORDS = ["gali1", "gali2", "gali3"]  # apne words add karo

# ================= HELPERS =================

async def is_admin(message):
    member = await app.get_chat_member(
        message.chat.id,
        message.from_user.id
    )
    return member.status in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    )

def contains_real_link(text):
    if not text:
        return False
    return re.search(REAL_LINK_REGEX, text)

def is_only_username(text):
    if not text:
        return False
    return re.fullmatch(USERNAME_ONLY_REGEX, text.strip())

def contains_abuse(text):
    if not text:
        return False
    text = text.lower()
    return any(word in text for word in ABUSE_WORDS)

async def delete_with_message(message, reason):
    await message.delete()
    await message.reply_text(
        f"╔═════ ❖ 𝑴𝑶𝑫𝑬𝑹𝑨𝑻𝑰𝑶𝑵 𝑨𝑳𝑬𝑹𝑻 ❖ ═════╗\n"
        f"⚠️ {reason}\n\n"
        f"🚫 Restricted Content Removed\n"
        f"🔒 Please Follow Group Rules\n\n"
        f"➕ 𝘼𝙙𝙙 𝙈𝙚 𝙏𝙤 𝙔𝙤𝙪𝙧 𝙂𝙧𝙤𝙪𝙥",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "➕ Add Me To Your Group",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ]]
        )
    )

# ================= START DESCRIPTION =================

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "╔═══ ❖ 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑮𝑹𝑶𝑼𝑷 𝑴𝑶𝑫𝑬𝑹𝑨𝑻𝑶𝑹 ❖ ═══╗\n\n"
        "🔰 Advanced Protection System\n\n"
        "✅ Bio Link Detection\n"
        "✅ Link Auto Delete\n"
        "✅ Edit Link Protection\n"
        "✅ Abuse Detection\n"
        "✅ Edited Abuse Protection\n"
        "✅ Media Auto Delete\n\n"
        "🔗 Support Group:\n"
        f"{SUPPORT_GROUP}\n\n"
        "📢 Update Channel:\n"
        f"{SUPPORT_CHANNEL}"
    )

# ================= FREE COMMANDS =================

@app.on_message(filters.command("free") & filters.group)
async def free_user(_, message):
    if not await is_admin(message):
        return
    if not message.reply_to_message:
        return
    free_users[message.reply_to_message.from_user.id] = True
    await message.reply_text("✅ User Free From Bio Detection")

@app.on_message(filters.command("unfree") & filters.group)
async def unfree_user(_, message):
    if not await is_admin(message):
        return
    if not message.reply_to_message:
        return
    free_users.pop(message.reply_to_message.from_user.id, None)
    await message.reply_text("❌ User Removed From Free List")

@app.on_message(filters.command("freelist") & filters.group)
async def freelist(_, message):
    if not await is_admin(message):
        return
    if not free_users:
        await message.reply_text("Free list empty.")
        return
    text = "📜 Free Users:\n"
    for user in free_users:
        text += f"- `{user}`\n"
    await message.reply_text(text)

# ================= BIO LINK DETECTION =================

@app.on_message(filters.group & filters.text)
async def bio_check(_, message):

    if await is_admin(message):
        return

    user_id = message.from_user.id

    if user_id in free_users:
        return

    try:
        user = await app.get_users(user_id)
        bio = user.bio

        if not bio:
            return

        if is_only_username(bio.strip()):
            return

        if contains_real_link(bio):
            await app.restrict_chat_member(
                message.chat.id,
                user_id,
                ChatPermissions()
            )
            await message.reply_text("🚫 User Muted (Bio Link Detected)")

    except:
        pass

# ================= MAIN FILTER =================

@app.on_message(filters.group)
async def main_filter(_, message):

    if await is_admin(message):
        return

    if message.media:
        await message.delete()
        return

    text = message.text

    if not text:
        return

    if is_only_username(text):
        return

    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                return

    if contains_real_link(text):
        await delete_with_message(message, "🔗 Link Removed")

    elif contains_abuse(text):
        await delete_with_message(message, "🚫 Inappropriate Language Deleted")

# ================= EDIT FILTER =================

@app.on_message(filters.group & filters.edited)
async def edit_filter(_, message):

    if await is_admin(message):
        return

    text = message.text

    if not text:
        return

    if is_only_username(text):
        return

    if contains_real_link(text):
        await delete_with_message(message, "✏️ Edited Link Removed")

    elif contains_abuse(text):
        await delete_with_message(message, "✏️ Edited Inappropriate Language Removed")

# ================= RUN =================

app.run()