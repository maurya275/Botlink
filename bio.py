from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "BotTelegramLinkProtector",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===== TELEGRAM LINK CHECK FUNCTION ===== #

def has_telegram_link(message: Message) -> bool:
    text = message.text or message.caption or ""

    # 1️⃣ Plain text check
    if "t.me" in text or "telegram.me" in text:
        return True

    # 2️⃣ Hidden markdown/entity link check
    if message.entities:
        for entity in message.entities:
            if entity.type in ["url", "text_link"]:
                return True

    # 3️⃣ Button URL check
    if message.reply_markup:
        for row in message.reply_markup.inline_keyboard:
            for button in row:
                if button.url and ("t.me" in button.url or "telegram.me" in button.url):
                    return True

    return False


# ===== MAIN DELETE SYSTEM ===== #

@app.on_message(filters.group)
@app.on_edited_message(filters.group)
async def delete_bot_links(client: Client, message: Message):

    # Sirf bot message check karega
    if message.from_user and message.from_user.is_bot:

        if has_telegram_link(message):

            try:
                await message.delete()
                print("Bot Telegram link message deleted")
            except Exception as e:
                print("Delete failed:", e)


app.run()