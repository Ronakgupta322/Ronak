# -----------------------------------------------
# 🔸 Clonify Project
# 🔹 Start Module - Fixed & Stable Version
# -----------------------------------------------

import random
import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from Clonify import app
from Clonify.misc import boot
from Clonify.plugins.sudo.sudoers import sudoers_list
from Clonify.utils import bot_sys_stats
from Clonify.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
    is_on_off,
)
from Clonify.utils.decorators.language import LanguageStart
from Clonify.utils.formatters import get_readable_time
from Clonify.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, STREAMI_PICS
from strings import get_string


EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]


async def send_safe(
    message: Message,
    photo: str,
    caption: str,
    reply_markup=None,
    effect_id=None,
):
    try:
        return await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            message_effect_id=effect_id,
        )
    except Exception as e:
        print(f"[START PHOTO ERROR] {e}")
        return await message.reply_text(
            text=caption,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        await add_served_user(message.from_user.id)

        bot_mention = client.me.mention
        bot_username = client.me.username

        if not _:
            _ = {}

        if len(message.text.split()) > 1:
            name = message.text.split(None, 1)[1]

            if name.startswith("help"):
                keyboard = help_pannel(_)
                text = _.get("help_1", "Help panel").format(config.SUPPORT_CHAT)
                return await send_safe(
                    message=message,
                    photo=random.choice(STREAMI_PICS),
                    caption=text,
                    reply_markup=keyboard,
                    effect_id=random.choice(EFFECT_IDS),
                )

            if name.startswith("sud"):
                await sudoers_list(client=client, message=message, _=_)
                if await is_on_off(2):
                    await client.send_message(
                        chat_id=config.LOGGER_ID,
                        text=(
                            f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ "
                            f"ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n"
                            f"<b>✦ ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                            f"<b>✦ ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}"
                        ),
                    )
                return

            if name.startswith("inf"):
                query = name.replace("info_", "", 1)
                results = VideosSearch(query, limit=1)
                result_data = await results.next()

                title = "Unknown"
                duration = "Unknown"
                views = "Unknown"
                thumbnail = random.choice(STREAMI_PICS)
                channellink = config.SUPPORT_CHAT
                channel = "Unknown"
                link = config.SUPPORT_CHAT
                published = "Unknown"

                for result in result_data.get("result", []):
                    title = result.get("title", "Unknown")
                    duration = result.get("duration", "Unknown")
                    views = result.get("viewCount", {}).get("short", "Unknown")
                    thumbnail = result.get("thumbnails", [{}])[0].get("url", thumbnail)
                    thumbnail = thumbnail.split("?")[0]
                    channellink = result.get("channel", {}).get("link", config.SUPPORT_CHAT)
                    channel = result.get("channel", {}).get("name", "Unknown")
                    link = result.get("link", config.SUPPORT_CHAT)
                    published = result.get("publishedTime", "Unknown")
                    break

                searched_text = _.get("start_6", "Track Info").format(
                    title,
                    duration,
                    views,
                    published,
                    channellink,
                    channel,
                    bot_mention,
                )

                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=_.get("S_B_8", "🎧 Listen"),
                                url=link,
                            ),
                            InlineKeyboardButton(
                                text=_.get("S_B_9", "💬 Support"),
                                url=config.SUPPORT_CHAT,
                            ),
                        ],
                    ]
                )

                await send_safe(
                    message=message,
                    photo=thumbnail,
                    caption=searched_text,
                    reply_markup=key,
                    effect_id=random.choice(EFFECT_IDS),
                )

                if await is_on_off(2):
                    await client.send_message(
                        chat_id=config.LOGGER_ID,
                        text=(
                            f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ "
                            f"ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n"
                            f"<b>✦ ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                            f"<b>✦ ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}"
                        ),
                    )
                return

        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        up, cpu, ram, disk = await bot_sys_stats()

        try:
            caption = _["start_2"].format(
                message.from_user.mention,
                bot_mention,
                up,
                disk,
                cpu,
                ram,
                served_users,
                served_chats,
            )
        except Exception as e:
            print(f"[START_2 FORMAT ERROR] {e}")
            caption = (
                f"👋 Hello {message.from_user.mention}\n\n"
                f"🎵 Welcome to {bot_mention}\n\n"
                f"⚡ Fast • Smooth • Stable\n"
                f"👥 Users: {served_users}\n"
                f"💬 Chats: {served_chats}\n"
            )

        await send_safe(
            message=message,
            photo=random.choice(STREAMI_PICS),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(out),
            effect_id=random.choice(EFFECT_IDS),
        )

        if await is_on_off(2):
            await client.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                    f"✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                    f"✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}"
                ),
            )

    except Exception as e:
        print(f"[PRIVATE START ERROR] {e}")
        await message.reply_text("❌ Start load failed, try again.")


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        if not _:
            _ = {}

        out = start_panel(_)
        uptime = int(time.time() - boot)
        bot_mention = client.me.mention

        try:
            caption = _["start_1"].format(bot_mention, get_readable_time(uptime))
        except Exception as e:
            print(f"[START_1 FORMAT ERROR] {e}")
            caption = (
                f"🎵 {bot_mention} is alive.\n\n"
                f"⏱ Uptime: {get_readable_time(uptime)}"
            )

        await send_safe(
            message=message,
            photo=random.choice(STREAMI_PICS),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(out),
            effect_id=random.choice(EFFECT_IDS),
        )
        return await add_served_chat(message.chat.id)

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
                except Exception:
                    pass

            if member.id == bot_id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_.get("start_4", "Use me in supergroup only."))
                    return await client.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _.get("start_5", "{}\n{}\n{}").format(
                            bot_mention,
                            f"https://t.me/{bot_username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await client.leave_chat(message.chat.id)

                out = start_panel(_)

                try:
                    caption = _["start_3"].format(
                        message.from_user.mention,
                        bot_mention,
                        message.chat.title,
                        bot_mention,
                    )
                except Exception as e:
                    print(f"[START_3 FORMAT ERROR] {e}")
                    caption = (
                        f"👋 Thanks {message.from_user.mention}\n\n"
                        f"{bot_mention} added successfully in {message.chat.title}"
                    )

                await send_safe(
                    message=message,
                    photo=random.choice(STREAMI_PICS),
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(out),
                    effect_id=random.choice(EFFECT_IDS),
                )

                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(f"[WELCOME ERROR] {ex}")
