import asyncio
import random
import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from Clonify import app
from Clonify.misc import _boot_
from Clonify.plugins.sudo.sudoers import sudoers_list
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
from config import BANNED_USERS, STREAMI_PICS, GREET
from strings import get_string


# =========================
# HELPERS
# =========================
def safe_mention(user) -> str:
    try:
        return user.mention if user else "User"
    except Exception:
        return "User"


def safe_username(user) -> str:
    try:
        return f"@{user.username}" if user and user.username else "No Username"
    except Exception:
        return "No Username"


def choose_start_pic():
    try:
        return random.choice(STREAMI_PICS)
    except Exception:
        return None


async def send_log(text: str):
    try:
        if await is_on_off(2):
            await app.send_message(chat_id=config.LOGGER_ID, text=text)
    except Exception:
        pass


async def loading_animation(msg: Message):
    try:
        loading = await msg.reply_text(random.choice(GREET))
    except Exception:
        loading = await msg.reply_text("Loading...")

    frames = [
        "<b>ʟᴏᴀᴅɪɴɢ</b>",
        "<b>ʟᴏᴀᴅɪɴɢ.</b>",
        "<b>ʟᴏᴀᴅɪɴɢ..</b>",
        "<b>ʟᴏᴀᴅɪɴɢ...</b>",
    ]

    for frame in frames:
        try:
            await loading.edit_text(frame)
            await asyncio.sleep(0.2)
        except Exception:
            pass

    try:
        await loading.delete()
    except Exception:
        pass


# =========================
# PRIVATE START
# =========================
@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    await loading_animation(message)

    user_mention = safe_mention(message.from_user)
    user_username = safe_username(message.from_user)

    args = ""
    try:
        if len(message.command) > 1:
            args = message.command[1].strip()
    except Exception:
        args = ""

    if args:
        args_lower = args.lower()

        # =========================
        # HELP PANEL
        # =========================
        if args_lower.startswith("help"):
            keyboard = help_pannel(_)
            pic = choose_start_pic()
            try:
                if pic:
                    return await message.reply_photo(
                        photo=pic,
                        caption=_["help_1"].format(config.SUPPORT_CHAT),
                        reply_markup=keyboard,
                    )
                else:
                    return await message.reply_text(
                        text=_["help_1"].format(config.SUPPORT_CHAT),
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                    )
            finally:
                await send_log(
                    f"✦ {user_mention} ᴏᴘᴇɴᴇᴅ <b>ʜᴇʟᴘ ᴘᴀɴᴇʟ</b>.\n\n"
                    f"✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                    f"✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> {user_username}"
                )

        # =========================
        # SUDO LIST
        # =========================
        if args_lower.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return await send_log(
                f"✦ {user_mention} ᴊᴜsᴛ ᴄʜᴇᴄᴋᴇᴅ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n"
                f"✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                f"✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> {user_username}"
            )

        # =========================
        # TRACK INFO
        # format: /start info_<videoid>
        # =========================
        if args_lower.startswith("inf"):
            m = await message.reply_text("🔎 <b>ғᴇᴛᴄʜɪɴɢ ᴛʀᴀᴄᴋ ɪɴғᴏ...</b>")

            try:
                query = args.replace("info_", "", 1).strip()
                query = query.replace("inf", "", 1).strip("_ ").strip()

                if not query:
                    return await m.edit_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴛʀᴀᴄᴋ ɪɴғᴏ ʟɪɴᴋ.</b>")

                yt_query = f"https://www.youtube.com/watch?v={query}"
                results = VideosSearch(yt_query, limit=1)
                data = await results.next()

                if not data.get("result"):
                    return await m.edit_text("❌ <b>ɴᴏ ᴛʀᴀᴄᴋ ɪɴғᴏ ғᴏᴜɴᴅ.</b>")

                result = data["result"][0]

                title = result.get("title", "Unknown")
                duration = result.get("duration", "Unknown")
                published = result.get("publishedTime", "Unknown")
                link = result.get("link", yt_query)

                views = "Unknown"
                try:
                    views = result.get("viewCount", {}).get("short", "Unknown")
                except Exception:
                    pass

                thumbnail = None
                try:
                    thumbs = result.get("thumbnails", [])
                    if thumbs:
                        thumbnail = thumbs[0]["url"].split("?")[0]
                except Exception:
                    thumbnail = None

                channel = "Unknown"
                channellink = "https://youtube.com"
                try:
                    channel = result.get("channel", {}).get("name", "Unknown")
                    channellink = result.get("channel", {}).get("link", "https://youtube.com")
                except Exception:
                    pass

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
                        ],
                    ]
                )

                try:
                    await m.delete()
                except Exception:
                    pass

                if thumbnail:
                    await app.send_photo(
                        chat_id=message.chat.id,
                        photo=thumbnail,
                        caption=searched_text,
                        reply_markup=key,
                    )
                else:
                    await message.reply_text(
                        text=searched_text,
                        reply_markup=key,
                        disable_web_page_preview=False,
                    )

                return await send_log(
                    f"✦ {user_mention} ᴊᴜsᴛ ᴄʜᴇᴄᴋᴇᴅ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n"
                    f"✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                    f"✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> {user_username}"
                )

            except Exception as e:
                try:
                    await m.edit_text(f"❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴛʀᴀᴄᴋ ɪɴғᴏ.</b>\n<code>{e}</code>")
                except Exception:
                    await message.reply_text("❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴛʀᴀᴄᴋ ɪɴғᴏ.</b>")
                return

    # =========================
    # NORMAL PRIVATE START
    # =========================
    out = private_panel(_)
    pic = choose_start_pic()

    if pic:
        await message.reply_photo(
            photo=pic,
            caption=_["start_2"].format(user_mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
    else:
        await message.reply_text(
            text=_["start_2"].format(user_mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
            disable_web_page_preview=True,
        )

    await send_log(
        f"✦ {user_mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
        f"✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
        f"✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> {user_username}"
    )


# =========================
# GROUP START
# =========================
@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    pic = choose_start_pic()

    if pic:
        await message.reply_photo(
            photo=pic,
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )
    else:
        await message.reply_text(
            text=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
            disable_web_page_preview=True,
        )

    return await add_served_chat(message.chat.id)


# =========================
# WELCOME / BOT ADDED
# =========================
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
                continue

            if member.id == app.id:
                # only supergroup allowed
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                # blacklist check
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
                        safe_mention(message.from_user),
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )

                await add_served_chat(message.chat.id)

                try:
                    await message.stop_propagation()
                except Exception:
                    pass

        except Exception as ex:
            print(f"[START ERROR] {ex}")
