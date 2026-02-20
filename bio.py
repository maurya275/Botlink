import re
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "LinkDeleteBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Telegram link pattern
LINK_PATTERN = re.compile(
    r"(t\.me/\S+|https?://t\.me/\S+|telegram\.me/\S+)",
    re.IGNORECASE
)

@app.on_message(filters.group)
@app.on_edited_message(filters.group)
async def delete_links(client, message):

    try:
        text = message.text or message.caption or ""

        # Sirf bot ke message check kare
        if message.from_user and message.from_user.is_bot:

            if LINK_PATTERN.search(text):
                await message.delete()
                print("Deleted bot Telegram link")

    except Exception as e:
        print("Error:", e)


print("Bot Started Successfully...")
app.run()