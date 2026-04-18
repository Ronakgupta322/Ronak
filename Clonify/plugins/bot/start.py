import time
import random
import asyncio
import traceback
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import PhotoInvalidDimensions, WebpageCurlFailed, MediaEmpty, RPCError
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
from config import BANNED_USERS, STREAMI_PICS, GREET
from strings import get_string

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADVANCED STRANGER AESTHETIC CAPTION TEMPLATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRANGER_START_CAPTION = """
**❅ ʜᴇʟʟᴏ {mention} !**

**ɪ ᴀᴍ {bot_name}** **ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ & ᴘᴏᴡᴇʀғᴜʟ ʙᴏᴛ ᴡɪᴛʜ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.**

**┏━━━━━━━━━━━━━━━━━━━━━⦊**
**┣ ⚝ ᴜᴘᴛɪᴍᴇ ➠** `{uptime}`
**┣ ⚝ ᴜsᴇʀs ➠** `{users}`
**┣ ⚝ ᴄʜᴀᴛs ➠** `{chats}`
**┣ ⚝ ᴠᴇʀsɪᴏɴ ➠** `v2.5 Pro`
**┗━━━━━━━━━━━━━━━━━━━━━⦊**

**๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs!**
"""

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    # Pro-Level System Boot Animation
    loading_1 = await message.reply_text("<b>« ɪɴɪᴛɪᴀʟɪᴢɪɴɢ sʏsᴛᴇᴍ... »</b>")
    await add_served_user(message.from_user.id)
    
    animations = [
        "<b>« ʙᴏᴏᴛɪɴɢ ᴜᴘ ᴅᴀᴛᴀʙᴀsᴇ... »</b>",
        "<b>« ᴠᴇʀɪғʏɪɴɢ ᴍᴏᴅᴜʟᴇs... »</b>",
        "<b>« sᴛᴀʀᴛɪɴɢ sᴇʀᴠɪᴄᴇs... »</b>"
    ]
    
    for frame in animations:
        await loading_1.edit_text(frame)
        await asyncio.sleep(0.3)

    if len(message.text.split()) > 1:
        await loading_1.delete()
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(STREAMI_PICS),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>✦ ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎 <b>ғᴇᴛᴄʜɪɴɢ ᴛʀᴀᴄᴋ ɪɴғᴏ...</b>")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            return
    else:
        try:
            # Stranger Repo Stats Fetching
            uptime = int(time.time() - _boot_)
            users = len(await get_served_users())
            chats = len(await get_served_chats())
            
            # Formating the Caption
            caption = STRANGER_START_CAPTION.format(
                mention=message.from_user.mention,
                bot_name=app.mention,
                uptime=get_readable_time(uptime),
                users=users,
                chats=chats
            )
            
            # Checking and setting Keyboard
            out = private_panel(_)
            markup = out if isinstance(out, InlineKeyboardMarkup) else InlineKeyboardMarkup(out)
            
            # Deleting loading message before sending final message
            await loading_1.delete()

            # SAFE IMAGE SENDER: Agar image link kharab hogi toh sirf text aayega, bot crash nahi hoga.
            try:
                await message.reply_photo(
                    photo=random.choice(STREAMI_PICS),
                    caption=caption,
                    reply_markup=markup,
                )
            except (PhotoInvalidDimensions, WebpageCurlFailed, MediaEmpty, RPCError) as img_err:
                # Fallback to text message if photo fails
                print(f"Warning: Photo send failed. Falling back to text. Error: {img_err}")
                await message.reply_text(
                    text=caption,
                    reply_markup=markup,
                    disable_web_page_preview=True
                )

            # Logger
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>",
                )

        except Exception as e:
            # FULL DEBUGGER: Error kya hai exactly screen par dikhega (Termux/VPS Logs ke liye)
            error_traceback = traceback.format_exc()
            print("========== START COMMAND ERROR ==========")
            print(error_traceback)
            print("=========================================")
            
            try:
                await message.reply_text(f"<b>❌ Bot Error:</b>\n<code>{e}</code>\n\n_Developer ko Terminal logs check karne boliye._")
            except:
                pass


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(STREAMI_PICS),
        caption=f"**❅ ᴀʟɪᴠᴇ & ᴡᴏʀᴋɪɴɢ ᴘᴇʀғᴇᴄᴛʟʏ !**\n\n**⚝ ᴜᴘᴛɪᴍᴇ ➠** `{get_readable_time(uptime)}`\n**⚝ ʙᴏᴛ ➠** {app.mention}",
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)


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
                    await message.reply_text("**[!] ᴇʀʀᴏʀ:** `ɪ ᴏɴʟʏ ᴡᴏʀᴋ ɪɴ sᴜᴘᴇʀɢʀᴏᴜᴘs !`")
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
                    text=f"**❅ ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ {message.chat.title} !**\n\n**⚝ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ғᴜɴᴄᴛɪᴏɴ ᴘʀᴏᴘᴇʀʟʏ.**",
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
