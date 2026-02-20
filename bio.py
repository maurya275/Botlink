from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient
from config import *
from link_filter import check_and_delete_link
import asyncio

app = Client(
    "BioLinkRemover",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo.biolinkbot
warn_db = db.warns


# ================= COMMANDS =================

@app.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    await message.reply_text(
        "🔐 Bot Link Remover Active\n\n"
        "Links auto delete + Bio detect enabled.\n"
        "Use /help for help."
    )


@app.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    await message.reply_text(
        "📌 Commands List:\n\n"
        "/start - Start bot\n"
        "/help - Help menu\n"
        "/free - Bot status\n"
        "/biocheck - Reply user to check bio"
    )


@app.on_message(filters.command("free"))
async def free_cmd(_, message: Message):
    await message.reply_text(
        "🤖 Bot is running properly.\n"
        "Auto link delete enabled."
    )


@app.on_message(filters.command("biocheck"))
async def bio_check(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user.")

    user = message.reply_to_message.from_user
    bio = user.bio if user.bio else ""

    if URL_PATTERN.search(bio):
        await message.reply_text("⚠️ Link found in bio.")
    else:
        await message.reply_text("✅ No link in bio.")


# ================ WARN SYSTEM =================

async def add_warn(chat_id, user_id):
    data = await warn_db.find_one({"chat_id": chat_id, "user_id": user_id})

    if data:
        count = data["count"] + 1
        await warn_db.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": count}}
        )
    else:
        count = 1
        await warn_db.insert_one(
            {"chat_id": chat_id, "user_id": user_id, "count": count}
        )

    return count


# ================ LINK HANDLER =================

@app.on_message(filters.group)
async def link_handler(_, message: Message):
    if not message.text and not message.caption:
        return

    await check_and_delete_link(app, message, add_warn)


# ================ BIO AUTO CHECK =================

@app.on_message(filters.new_chat_members)
async def check_bio(_, message: Message):
    for user in message.new_chat_members:
        bio = user.bio if user.bio else ""
        if URL_PATTERN.search(bio):
            try:
                await app.restrict_chat_member(
                    message.chat.id,
                    user.id,
                    permissions={}
                )
                await message.reply_text(
                    f"⚠️ {user.mention} muted for bio link."
                )
            except:
                pass


print("Bot Started Successfully ✅")
app.run()