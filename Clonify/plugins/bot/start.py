# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla
# -----------------------------------------------

import random
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import boot
from SHUKLAMUSIC.plugins.sudo.sudoers import sudoers_list
from SHUKLAMUSIC.utils import bot_sys_stats
from SHUKLAMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
    is_on_off,
)
from SHUKLAMUSIC.utils.decorators.language import LanguageStart
from SHUKLAMUSIC.utils.formatters import get_readable_time
from SHUKLAMUSIC.utils.inline import help_pannel, private_panel, start_panel
from strings import get_string
from config import BANNED_USERS, SHASHANK_IMG


EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]


# 🔹 SAFE SENDER (image fail → text fallback)
async def send_safe(msg: Message, photo, caption, markup, effect_id=None):
    try:
        return await msg.reply_photo(
            photo,
            caption=caption,
            reply_markup=markup,
            message_effect_id=effect_id,
        )
    except Exception as e:
        print(f"[PHOTO ERROR] {e}")
        return await msg.reply_text(
            caption,
            reply_markup=markup,
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        await add_served_user(message.from_user.id)

        bot_mention = client.me.mention
        bot_username = client.me.username

        # 🔹 language safe
        if not _:
            _ = {}

        # 🔹 deep link handling
        if len(message.text.split()) > 1:
            name = message.text.split(None, 1)[1]

            if name.startswith("help"):
                keyboard = help_pannel(_)
                text = _.get("help_1", "Help Panel").format(config.SUPPORT_CHAT)
                return await send_safe(
                    message,
                    random.choice(SHASHANK_IMG),
                    text,
                    keyboard,
                    random.choice(EFFECT_IDS),
                )

            elif name.startswith("sud"):
                await sudoers_list(client=client, message=message, _=_)
                return

            elif name.startswith("inf"):
                query = name.replace("info_", "", 1)
                results = VideosSearch(query, limit=1)

                for result in (await results.next())["result"]:
                    title = result.get("title", "Unknown")
                    duration = result.get("duration", "Unknown")
                    views = result.get("viewCount", {}).get("short", "Unknown")
                    thumbnail = result.get("thumbnails", [{}])[0].get("url", "")
                    thumbnail = thumbnail.split("?")[0]
                    channellink = result.get("channel", {}).get("link", "")
                    channel = result.get("channel", {}).get("name", "Unknown")
                    link = result.get("link", "")
                    published = result.get("publishedTime", "Unknown")

                text = _.get("start_6", "Track Info").format(
                    title, duration, views, published, channellink, channel, bot_mention
                )

                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🎧 Listen", url=link),
                            InlineKeyboardButton("💬 Support", url=config.SUPPORT_CHAT),
                        ]
                    ]
                )

                return await send_safe(
                    message,
                    thumbnail,
                    text,
                    key,
                    random.choice(EFFECT_IDS),
                )

        # 🔹 MAIN START PANEL
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()

        # 🔹 language safe text
        try:
            text = _["start_2"].format(
                message.from_user.mention,
                bot_mention,
                UP,
                DISK,
                CPU,
                RAM,
                served_users,
                served_chats,
            )
        except Exception as e:
            print(f"[LANG ERROR] {e}")
            text = f"""
👋 Hello {message.from_user.mention}

🎵 Welcome to {bot_mention}

⚡ Fast • Smooth • No Lag

👥 Users: {served_users}
💬 Chats: {served_chats}
"""

        await send_safe(
            message,
            random.choice(SHASHANK_IMG),
            text,
            InlineKeyboardMarkup(out),
            random.choice(EFFECT_IDS),
        )

        if await is_on_off(2):
            await client.send_message(
                chat_id=config.LOGGER_ID,
                text=f"User started bot ➜ {message.from_user.mention}",
            )

    except Exception as e:
        print(f"[START ERROR] {e}")
        await message.reply_text("❌ Start load failed, try again.")


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        uptime = int(time.time() - boot)
        bot_mention = client.me.mention
        out = start_panel(_)

        text = _.get("start_1", "Bot is Alive").format(
            bot_mention, get_readable_time(uptime)
        )

        await send_safe(
            message,
            random.choice(SHASHANK_IMG),
            text,
            InlineKeyboardMarkup(out),
            random.choice(EFFECT_IDS),
        )

        await add_served_chat(message.chat.id)

    except Exception as e:
        print(f"[GROUP START ERROR] {e}")


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    bot_id = client.me.id
    bot_mention = client.me.mention
    bot_username = client.me.username

    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language) or {}

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == bot_id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_.get("start_4", "Use in supergroup"))
                    return await client.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _.get("start_5", "Blacklisted").format(
                            bot_mention,
                            f"https://t.me/{bot_username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await client.leave_chat(message.chat.id)

                out = start_panel(_)

                text = _.get("start_3", "Bot added").format(
                    message.from_user.mention,
                    bot_mention,
                    message.chat.title,
                    bot_mention,
                )

                await send_safe(
                    message,
                    random.choice(SHASHANK_IMG),
                    text,
                    InlineKeyboardMarkup(out),
                    random.choice(EFFECT_IDS),
                )

                await add_served_chat(message.chat.id)

        except Exception as e:
            print(f"[WELCOME ERROR] {e}")
