import re

API_ID = "PASTE_NEW_API_ID"
API_HASH = "PASTE_NEW_API_HASH"
BOT_TOKEN = "PASTE_NEW_BOT_TOKEN"

MONGO_URI = "mongodb+srv://=Cluster0"

DEFAULT_WARNING_LIMIT = 3
DEFAULT_PUNISHMENT = "mute"
DEFAULT_CONFIG = ("warn", DEFAULT_WARNING_LIMIT, DEFAULT_PUNISHMENT)

# Bio URL pattern
URL_PATTERN = re.compile(
    r'(https?://|www\.)[a-zA-Z0-9.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-]*)*'
)

# Message Telegram link pattern
TELEGRAM_LINK_PATTERN = re.compile(
    r"(https?://)?(www\.)?(t\.me|telegram\.me)/[^\s]+",
    re.IGNORECASE
)

PROMOTION_TEXT = (
    "Member/Bot ke bheje gaye link ko delete kiya gaya.\n\n"
    "Apne group ko secure karne ke liye hamen apne group me add kare."
)

BOT_USERNAME = "BotLinkRemoverBot"