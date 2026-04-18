import time
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Clonify import app
from Clonify.misc import _boot_
from Clonify.utils.database import add_served_chat, add_served_user
from config import BANNED_USERS


# 🔹 SIMPLE SAFE START PANEL
def get_start_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎵 Play Music", callback_data="play"),
                InlineKeyboardButton("➕ Add Me", url="https://t.me/{}/?startgroup=true".format(app.username)),
            ],
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/your_channel"),
                InlineKeyboardButton("💬 Support", url="https://t.me/your_group"),
            ],
        ]
    )


@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
async def start_pm(client, message: Message):
    try:
        await add_served_user(message.from_user.id)

        text = f"""
👋 Hello {message.from_user.mention}

🎵 Welcome to {app.mention} Music Bot

⚡ Fast • Smooth • No Lag

👉 Send song name or use /play command
"""

        await message.reply_text(
            text,
            reply_markup=get_start_buttons(),
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(f"START ERROR: {e}")
        await message.reply_text("Bot start ho gaya hai but UI load nahi hua.")


@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
async def start_group(client, message: Message):
    try:
        uptime = int(time.time() - _boot_)

        text = f"""
🎵 {app.mention} is alive!

⏱ Uptime: {uptime} sec

👉 Use /play to start music
"""

        await message.reply_text(
            text,
            reply_markup=get_start_buttons(),
        )

        await add_served_chat(message.chat.id)

    except Exception as e:
        print(f"GROUP START ERROR: {e}")
