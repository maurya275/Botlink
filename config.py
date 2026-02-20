# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

import re

API_ID = "30861624" # Your Telegram API ID
API_HASH = "4bac8ea697e16d2323ad170a04aa552a" # Your Telegram API Hash
BOT_TOKEN = "8383893227:AAGoFsjWvYblmQJJnbQuA0eBJIBORYyR6fI" # Your Bot Token

# MongoDB connection URI
MONGO_URI = "mongodb+srv://Shizukamusicsss:Shizukamusicsss@cluster0.zupd3uz.mongodb.net/?appName=Cluster0"

DEFAULT_WARNING_LIMIT = 3
DEFAULT_PUNISHMENT = "mute" # Options: "mute", "ban"
DEFAULT_CONFIG = ("warn", DEFAULT_WARNING_LIMIT, DEFAULT_PUNISHMENT)

# Regex pattern to detect URLs in user bios
URL_PATTERN = re.compile(
    r'(https?://|www\.)[a-zA-Z0-9.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-]*)*' #done change here
)
