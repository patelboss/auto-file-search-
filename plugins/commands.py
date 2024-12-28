import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_file_details1
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, clean_file_name
from utils import *
#from verify import *
from database.connections_mdb import active_connection
import re
from info import *
import json
import base64
logger = logging.getLogger(__name__)

BATCH_FILES = {}
STREAM_MODE = "False"
VERIFY = "False"
AUTO_DELETE = "False"
GRP_LNK = "https://t.me/Filmykeedha/306"
OFR_CNL = "https://t.me/+4dWp2gDjwC43YmJl"
VERIFY_TUTORIAL = "https://t.me/Filmykeedha/394"
sticker_ids = [
    "CAACAgIAAxkBAAItAmdbY-9IY20HNfLFeeboOOex74M0AAL9AQACFkJrCqSvYaKm6vLJHgQ",
    "CAACAgIAAxkBAAIs1GdbWBhGfsD2U3Z2pGiR-d64z08mAAJvAAPb234AAZlbUKh7k4B0HgQ",
    "CAACAgIAAxkBAAIsz2dbV_286mg26Vx67MOWmyG-WvK7AAJtAAPb234AAXUe7IXy-0SlHgQ",
    "CAACAgQAAxkBAAIs_mdbY-Zk1JR7yRLoWsi8NbJEMFerAALVGAACOqGIUIer-Up9iv5aHgQ",
    "CAACAgQAAxkBAAIs-mdbY96brNo0bbqiAT0h9aHmGjfZAAISDgACQln9BFRvgD6jmKybHgQ"
]

def get_random_sticker():
    return random.choice(sticker_ids)
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('🔔 𝗨𝗽𝗱𝗮𝘁𝗲 🤖', url='https://t.me/iAmRashmibot')
            ],
            [
                InlineKeyboardButton('🙆🏻𝗛𝗲𝗹𝗽 🦾', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/patelboss/Rashmibot/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕↖️ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀\nमुझे GROUP में add करे। ↗️➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('🔎 𝗦𝗲𝗮𝗿𝗰𝗵 🧐', switch_inline_query_current_chat=''),
            InlineKeyboardButton('✪𝙂𝙍𝙊𝙐𝙋✪', url=GRP_LNK)
            ],[
            InlineKeyboardButton('🙆🏻 𝗛𝗲𝗹𝗽 🦾', callback_data='help'),
            InlineKeyboardButton('♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("𝗛𝗲𝘆 𝘀𝗼𝗻𝗮, 𝗘𝗸 𝗱𝗳𝗮 𝗰𝗵𝗲𝗰𝗸 𝗸𝗿 𝗹𝗼 𝗸𝗶 𝗺𝗮𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗺𝗲𝗶 𝗔𝗱𝗱 𝗵𝘂 𝘆𝗮 𝗻𝗵𝗶...!")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "⚠️ 𝗝𝗼𝗶𝗻 𝗨𝗽𝗱𝗮𝘁𝗲𝘀 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 ⚠️", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton(" 🔄 𝗧𝗿𝘆 𝗔𝗴𝗮𝗶𝗻", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(" 🔄 𝗧𝗿𝘆 𝗔𝗴𝗮𝗶𝗻", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**𝗣𝗹𝗲𝗮𝘀𝗲 𝗝𝗼𝗶𝗻 𝗠𝘆 𝗨𝗽𝗱𝗮𝘁𝗲𝘀 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗕𝗼𝘁!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕↖️ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀\nमुझे GROUP में add करे। ↗️➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('🔎 𝗦𝗲𝗮𝗿𝗰𝗵 🧐', switch_inline_query_current_chat=''),
            InlineKeyboardButton('✪𝙂𝙍𝙊𝙐𝙋✪', url='https://t.me/Filmykeedha_search')
            ],[
            InlineKeyboardButton('🙆🏻 𝗛𝗲𝗹𝗽 🦾', callback_data='help'),
            InlineKeyboardButton('♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Please wait")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return

    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all movies till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )

        
    if data.startswith("sendfiles"):
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        settings = await get_settings(chat_id)
        #g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")
        k = await client.send_message(chat_id=message.from_user.id,text=f"<b>Get All Files in a Single Click!!!\n\n📂 ʟɪɴᴋ ➠ : {g}</i></b>", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)
                    ], [
                        InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')
                    ]
                ]
            )
        )
        await asyncio.sleep(120)
        await k.edit("<b>Your message is successfully deleted!!!</b>")
        return

    
    elif data.startswith("all"):
        logger.info("Processing 'all' command.")
        random_sticker = get_random_sticker()
        logger.info("Random sticker selected.")
        
        files = temp.GETALL.get(file_id)
        if not files:
            logger.warning("No such file exists for the given file_id.")
            return await message.reply('<b><i>No such file exist.</b></i>')
        
        logger.info(f"Found {len(files)} files associated with file_id: {file_id}.")
        filesarr = []
    
    # Check verification status first, outside the loop
        if VERIFY:
            is_verified = await check_verification(client, message.from_user.id)
            if not is_verified:
                btn = [[
                    InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                ],[
                    InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                ]]
                await message.reply_text(
                    text="<b>You are not verified!\nKindly verify to continue!</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                logger.info(f"User {message.from_user.id} is not verified. Verification prompt sent.")
                return  # Stop further execution if user is not verified
    
    # Process files if verified
        for file in files:
            file_id = file["file_id"]
            logger.info(f"Processing file with file_id: {file_id}.")
            
            logger.info(f"Awaiting file details.")
            files_ = await get_file_details1(file_id)
            logger.debug(f"File details retrieved: {files_}.")
            
            files1 = files_
            title = clean_file_name(files1['file_name'])
            size = get_size(files1['file_size'])
            f_caption = files1['caption']
            
            logger.info(f"File details: title={title}, size={size}.")
            
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title,
                        file_size=size,
                        file_caption=f_caption
                    )
                    logger.info("Custom caption applied successfully.")
                except Exception as e:
                    logger.exception("Error applying custom caption.")
                    f_caption = f_caption or title
            
            if not f_caption:
                f_caption = title
                logger.info("Fallback caption applied.")

            if STREAM_MODE:
                button = [
                    [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
                    [InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')]
                ]
                logger.info("Stream mode enabled. Buttons configured.")
            else:
                button = [
                    [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
                    [InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')]
                ]
                logger.info("Default mode enabled. Buttons configured.")
            
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(button)
            )
            logger.info(f"File sent to user: {message.from_user.id}, message_id: {msg.id}.")
            filesarr.append(msg)
        
        logger.info("All files sent. Sending confirmation message.")
        k = await client.send_message(chat_id=message.from_user.id, text="waah yar 😛")
        await asyncio.sleep(30)
        
        logger.info("Deleting sent files after delay.")
        for x in filesarr:
            await x.delete()
            logger.info(f"Deleted message: {x.id}.")
        
        await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        logger.info("Confirmation message edited to indicate deletion.")
        return
    
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()

    files_ = await get_file_details(file_id)
    if VERIFY:
        is_verified = await check_verification(client, message.from_user.id)
        if not is_verified:
            btn = [[
                InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
            ], [
                InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
            ]]
            await message.reply_text(
                text="<b>You are not verified!\nKindly verify to continue!</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            logger.info(f"User {message.from_user.id} is not verified. Verification prompt sent.")
            return  # Stop execution if the user is not verified

    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = clean_file_name(file.file_name)
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name='' if title is None else title,
                        file_size='' if size is None else size,
                        file_caption=''
                    )
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('𝗡𝗼 𝘀𝘂𝗰𝗵 𝗳𝗶𝗹𝗲 𝗲𝘅𝗶𝘀𝘁.')
    files = files_[0]
    title = clean_file_name(files.file_name)
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name='' if title is None else title,
                file_size='' if size is None else size,
                file_caption='' if f_caption is None else f_caption
            )
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:    
        f_caption = f"{files.file_name}"

    button = [
        [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
        [InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')]
    ]
    logger.info("Default mode enabled. Buttons configured.")
            
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(button)
        )

                     

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("𝗨𝗻𝗲𝘅𝗽𝗲𝗰𝘁𝗲𝗱 𝘁𝘆𝗽𝗲 𝗼𝗳 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴...⏳", quote=True)
    else:
        await message.reply('𝗥𝗲𝗽𝗹𝘆 𝘁𝗼 𝗳𝗶𝗹𝗲 𝘄𝗶𝘁𝗵 /delete 𝘄𝗵𝗶𝗰𝗵 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('𝗧𝗵𝗶𝘀 𝗶𝘀 𝗻𝗼𝘁 𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱 𝗳𝗶𝗹𝗲 𝗳𝗼𝗿𝗺𝗮𝘁')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('𝗙𝗶𝗹𝗲 𝗶𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('𝗙𝗶𝗹𝗲 𝗶𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲')
        else:
            # files indexed before https://github.com/LazyDeveloperr/lazyPrincess/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('𝗙𝗶𝗹𝗲 𝗶𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        '𝗧𝗵𝗶𝘀 𝘄𝗶𝗹𝗹 𝗱𝗲𝗹𝗲𝘁𝗲 𝗮𝗹𝗹 𝗶𝗻𝗱𝗲𝘅𝗲𝗱 𝗳𝗶𝗹𝗲𝘀.\n 𝗗𝗼 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('♥️ Thank You Filmykeedha ♥️')
    await message.message.edit('𝗦𝘂𝗰𝗰𝗲𝘀𝗳𝘂𝗹𝗹𝘆 𝗗𝗲𝗹𝗲𝘁𝗲𝗱 𝗔𝗹𝗹 𝗧𝗵𝗲 𝗜𝗻𝗱𝗲𝘅𝗲𝗱 𝗙𝗶𝗹𝗲𝘀.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗻𝗼𝗻𝘆𝗺𝗼𝘂𝘀 𝗮𝗱𝗺𝗶𝗻. 𝗨𝘀𝗲 /connect {message.chat.id} 𝗶𝗻 𝗣𝗠")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝗜'𝗺 𝗽𝗿𝗲𝘀𝗲𝗻𝘁 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽!!", quote=True)
                return
        else:
            await message.reply_text("𝗜'𝗺 𝗻𝗼𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝘁𝗼 𝗮𝗻𝘆 𝗴𝗿𝗼𝘂𝗽𝘀!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Filter Button',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Single' if settings["button"] else 'Double',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bot PM',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["botpm"] else '❌ No',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'File Secure',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["file_secure"] else '❌ No',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Spell Check',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["spell_check"] else '❌ No',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>𝗖𝗵𝗮𝗻𝗴𝗲 𝗬𝗼𝘂𝗿 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀 𝗳𝗼𝗿 {title} 𝗔𝘀 𝗬𝗼𝘂𝗿 𝗪𝗶𝘀𝗵 ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗻𝗼𝗻𝘆𝗺𝗼𝘂𝘀 𝗮𝗱𝗺𝗶𝗻. 𝗨𝘀𝗲 /connect {message.chat.id} 𝗶𝗻 𝗣𝗠")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝗜'𝗺 𝗽𝗿𝗲𝘀𝗲𝗻𝘁 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽!!", quote=True)
                return
        else:
            await message.reply_text("𝗜'𝗺 𝗻𝗼𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝘁𝗼 𝗮𝗻𝘆 𝗴𝗿𝗼𝘂𝗽𝘀!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗲𝗺𝗽𝗹𝗮𝘁𝗲 𝗳𝗼𝗿 {title}  𝘁𝗼\n\n{template}")
@Client.on_callback_query(filters.regex("donation"))
async def donation_callback(client, callback_query):
    await callback_query.answer()
    buttons = [
        [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.reply_photo(
        photo=PAYMENT_QR,
        caption=PAYMENT_TEXT,
        reply_markup=reply_markup
    )
