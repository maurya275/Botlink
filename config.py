import re

API_ID = "30861624"
API_HASH = "4bac8ea697e16d2323ad170a04aa552a"
BOT_TOKEN = "8692072884:AAEzRyd7QiK3leHn-hc_qKEWf0nZGnLQq3Y"

MONGO_URI = "mongodb+srv://Shizukamusicsss:Shizukamusicsss@cluster0.zupd3uz.mongodb.net/?appName=Cluster0"

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