import time
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

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
from config import BANNED_USERS, STREAMI_PICS
from strings import get_string


# 🔹 Safe send function (image fail → text fallback)
async def send_start(message, caption, keyboard):
    try:
        return await message.reply_photo(
            photo=random.choice(STREAMI_PICS),
            caption=caption,
            reply_markup=keyboard,
        )
    except Exception as e:
        print(f"PHOTO ERROR: {e}")
        return await message.reply_text(
            text=caption,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        # 🔹 simple loading (NO animation = no lag)
        loading = await message.reply_text("⚡ Starting...")

        await add_served_user(message.from_user.id)

        # 🔹 deep link check
        if len(message.text.split()) > 1:
            name = message.text.split(None, 1)[1]

            if name.startswith("help"):
                await loading.delete()
                keyboard = help_pannel(_)
                return await send_start(
                    message,
                    _["help_1"].format(config.SUPPORT_CHAT),
                    keyboard,
                )

            if name.startswith("sud"):
                await loading.delete()
                await sudoers_list(client=client, message=message, _=_)
                return

        # 🔹 main start panel
        await loading.delete()
        keyboard = InlineKeyboardMarkup(private_panel(_))

        await send_start(
            message,
            _["start_2"].format(message.from_user.mention, app.mention),
            keyboard,
        )

        # 🔹 logging
        if await is_on_off(2):
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"User started bot ➜ {message.from_user.mention}",
            )

    except Exception as e:
        print(f"START ERROR: {e}")
        try:
            await message.reply_text("❌ Start load failed, try again.")
        except:
            pass


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        uptime = int(time.time() - _boot_)
        keyboard = InlineKeyboardMarkup(start_panel(_))

        try:
            await message.reply_photo(
                random.choice(STREAMI_PICS),
                caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
                reply_markup=keyboard,
            )
        except:
            await message.reply_text(
                _["start_1"].format(app.mention, get_readable_time(uptime)),
                reply_markup=keyboard,
            )

        await add_served_chat(message.chat.id)

    except Exception as e:
        print(f"GROUP START ERROR: {e}")


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
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
                    )
                    return await app.leave_chat(message.chat.id)

                keyboard = InlineKeyboardMarkup(start_panel(_))

                await message.reply_text(
                    text=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=keyboard,
                )

                await add_served_chat(message.chat.id)

        except Exception as e:
            print(f"WELCOME ERROR: {e}")
