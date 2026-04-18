import time
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from Clonify import app
from Clonify.misc import _boot_
from Clonify.plugins.sudo.sudoers import sudoers_list
from Clonify.utils.database import get_served_chats, get_served_users, get_sudoers
from Clonify.utils import bot_sys_stats
from Clonify.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Clonify.utils.decorators.language import LanguageStart
from Clonify.utils.formatters import get_readable_time
from Clonify.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, START_IMG_URL
from strings import get_string


async def safe_send_start(message: Message, caption: str, reply_markup):
    try:
        return await message.reply_photo(
            photo=START_IMG_URL,
            caption=caption,
            reply_markup=reply_markup,
        )
    except Exception as e:
        print(f"START_PHOTO_SEND_FAILED: {e}")
        return await message.reply_text(
            text=caption,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        loading = await message.reply_text("LOADING.")
        await add_served_user(message.from_user.id)

        if len(message.text.split()) > 1:
            name = message.text.split(None, 1)[1]

            if name[0:4] == "help":
                keyboard = help_pannel(_)
                await loading.delete()
                return await safe_send_start(
                    message,
                    _["help_1"].format(config.SUPPORT_CHAT),
                    keyboard,
                )

            if name[0:3] == "sud":
                await loading.delete()
                await sudoers_list(client=client, message=message, _=_)
                if await is_on_off(2):
                    return await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=(
                            f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ sᴜᴅᴏʟɪsᴛ.\n\n"
                            f"✦ ᴜsᴇʀ ɪᴅ ➠ `{message.from_user.id}`\n"
                            f"✦ ᴜsᴇʀɴᴀᴍᴇ ➠ @{message.from_user.username}"
                        ),
                    )
                return

            if name[0:3] == "inf":
                query = str(name).replace("info_", "", 1)
                query = f"https://www.youtube.com/watch?v={query}"
                results = VideosSearch(query, limit=1)
                result_data = await results.next()

                for result in result_data["result"]:
                    title = result.get("title", "Unknown")
                    duration = result.get("duration", "Unknown")
                    views = result.get("viewCount", {}).get("short", "Unknown")
                    thumbnail = result.get("thumbnails", [{}])[0].get("url", START_IMG_URL)
                    thumbnail = thumbnail.split("?")[0]
                    channellink = result.get("channel", {}).get("link", config.SUPPORT_CHAT)
                    channel = result.get("channel", {}).get("name", "Unknown")
                    link = result.get("link", config.SUPPORT_CHAT)
                    published = result.get("publishedTime", "Unknown")

                    searched_text = _["start_6"].format(
                        title,
                        duration,
                        views,
                        published,
                        channellink,
                        channel,
                        app.mention,
                    )

                    key = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=_["S_B_8"], url=link),
                                InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                            ]
                        ]
                    )

                    await loading.delete()
                    try:
                        await app.send_photo(
                            chat_id=message.chat.id,
                            photo=thumbnail,
                            caption=searched_text,
                            reply_markup=key,
                        )
                    except Exception as e:
                        print(f"INFO_PHOTO_SEND_FAILED: {e}")
                        await message.reply_text(
                            searched_text,
                            reply_markup=key,
                            disable_web_page_preview=True,
                        )

                    if await is_on_off(2):
                        return await app.send_message(
                            chat_id=config.LOGGER_ID,
                            text=(
                                f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.\n\n"
                                f"✦ ᴜsᴇʀ ɪᴅ ➠ `{message.from_user.id}`\n"
                                f"✦ ᴜsᴇʀɴᴀᴍᴇ ➠ @{message.from_user.username}"
                            ),
                        )
                    return

        out = private_panel(_)
        await loading.delete()
        await safe_send_start(
            message,
            _["start_2"].format(message.from_user.mention, app.mention),
            InlineKeyboardMarkup(out),
        )

        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                    f"✦ ᴜsᴇʀ ɪᴅ ➠ `{message.from_user.id}`\n"
                    f"✦ ᴜsᴇʀɴᴀᴍᴇ ➠ @{message.from_user.username}"
                ),
            )

    except Exception as e:
        print(f"START_PM_ERROR: {e}")
        try:
            await message.reply_text("Start panel load nahi ho paaya. Dobara /start bhejo.")
        except Exception as inner:
            print(f"START_PM_FALLBACK_ERROR: {inner}")


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        out = start_panel(_)
        uptime = int(time.time() - _boot_)
        try:
            await message.reply_photo(
                START_IMG_URL,
                caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
                reply_markup=InlineKeyboardMarkup(out),
            )
        except Exception as e:
            print(f"GROUP_START_PHOTO_FAILED: {e}")
            await message.reply_text(
                _["start_1"].format(app.mention, get_readable_time(uptime)),
                reply_markup=InlineKeyboardMarkup(out),
                disable_web_page_preview=True,
            )
        return await add_served_chat(message.chat.id)
    except Exception as e:
        print(f"START_GP_ERROR: {e}")


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_text(
                    text=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(f"WELCOME_ERROR: {ex}")
