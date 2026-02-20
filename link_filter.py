from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageDeleteForbidden

from config import TELEGRAM_LINK_PATTERN, PROMOTION_TEXT, BOT_USERNAME


def setup_link_filter(app):

    @app.on_message(filters.group & filters.text)
    async def delete_links(client, message):

        if not message.text:
            return

        if TELEGRAM_LINK_PATTERN.search(message.text):

            try:
                await message.delete()
            except MessageDeleteForbidden:
                return

            add_link = f"https://t.me/{BOT_USERNAME}?startgroup=true"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add This Bot To Your Group", url=add_link)]
            ])

            await client.send_message(
                message.chat.id,
                PROMOTION_TEXT,
                reply_markup=keyboard
            )


    @app.on_edited_message(filters.group & filters.text)
    async def delete_edited_links(client, message):

        if not message.text:
            return

        if TELEGRAM_LINK_PATTERN.search(message.text):

            try:
                await message.delete()
            except MessageDeleteForbidden:
                return

            add_link = f"https://t.me/{BOT_USERNAME}?startgroup=true"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add This Bot To Your Group", url=add_link)]
            ])

            await client.send_message(
                message.chat.id,
                PROMOTION_TEXT,
                reply_markup=keyboard
            )