# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, SUPPORT_CHAT_ID
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings, clean_file_name
from Script import script
from pyrogram.errors import ChatAdminRequired
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import logging
from pyrogram.enums import ParseMode
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    chat_id = message.chat.id
    user = message.from_user  # Get the user object
    user_id = user.id if user else 0  # Fallback to 0 if no user ID is available

    # Check if the user is an anonymous admin
    if user_id == 0:
        await message.reply_text(
            "<b>You are an anonymous admin. I can't process your request. "
            "Please disable 'Remain Anonymous' in admin rights to continue.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        # If not in the support chat, execute manual and auto-filter logic
        if chat_id != SUPPORT_CHAT_ID:
            await message.reply_text("Please join the private group as this chat may be banned anytime.")
            await manual_filters(client, message)
            await auto_filter(client, message)
            return

        # If in the support chat, perform search and reply with results
        search = message.text
        if not search:  # Ensure a valid search query
            await message.reply_text("Please provide a search query.")
            return

        # Get search results from the database
        temp_files, temp_offset, total_results = await get_search_results(
            chat_id=chat_id, query=search.lower(), offset=0, filter=True
        )

        # If results are found, reply with the count and search group link
        if total_results > 0:
            mention = user.mention if user else "Anonymous User"
            await message.reply_text(
                f"<b>Hey {mention}, {total_results} results found for '{search}'.\n\n"
                "This is a support group, so you can't access files here.\n\n"
                "Please use the search group: https://t.me/Filmykeedha/306</b>",
                disable_web_page_preview=True
            )
        else:
            # If no results, inform the user
            await message.reply_text("<b>No results found for your query. Please try again.</b>", parse_mode=ParseMode.HTML)

    except FloodWait as e:
        # Handle FloodWait exception
        await asyncio.sleep(e.value)
        await message.reply_text(
            f"<b>FloodWait detected. Please wait {e.value} seconds before trying again.</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Handle generic exceptions
        await message.reply_text(
            f"<b>An unexpected error occurred. Please try again later.\n\nDetails: {str(e)}</b>",
            parse_mode=ParseMode.HTML
        )    
   # except Exception as e:
    #    await send_error_log(client, "123", e)
        #await send_error_log(client, "GFILTER", e)

            #settings = await get_settings(chat_id)
            
   # await message.reply_text(" Bro join Private Group also because this may ban anytime")
   # await manual_filters(client, message)
    #if k == False:
   # await auto_filter(client, message)


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This Message is not for you dear. Don't worry you can send new one !", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)} ⊙ {clean_file_name(file.file_name)}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{clean_file_name(file.file_name)}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⬅𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⬅𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("This Message is not for you dear. Don't worry you can send new one !", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(' 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐮𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 ! 𝐰𝐞 𝐚𝐫𝐞 𝐫𝐞𝐚𝐥𝐥𝐲 𝐬𝐨𝐫𝐫𝐲 𝐟𝐨𝐫 𝐢𝐧𝐜𝐨𝐧𝐯𝐞𝐧𝐢𝐞𝐧𝐜𝐞 !\n 𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐭 𝐭𝐡𝐢𝐬 𝐌𝐨𝐯𝐢𝐞 𝐨𝐫 𝐖𝐞𝐛𝐬𝐞𝐫𝐢𝐞𝐬 𝐧𝐚𝐦𝐞 𝐢𝐧 #𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐓𝐨𝐩𝐢𝐜 𝐨𝐫 𝐬𝐞𝐧𝐭 𝐮𝐬𝐢𝐧𝐠 "#𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐌𝐨𝐯𝐢𝐞 𝐍𝐚𝐦𝐞 & 𝐑𝐞𝐥𝐞𝐚𝐬𝐞 𝐘𝐞𝐚𝐫.\n 𝐨𝐮𝐫 𝐠𝐫𝐞𝐚𝐭 𝐚𝐝𝐦𝐢𝐧𝐬 𝐰𝐢𝐥𝐥 𝐮𝐩𝐥𝐨𝐚𝐝 𝐢𝐭 𝐚𝐬 𝐬𝐨𝐨𝐧 𝐚𝐬 𝐩𝐨𝐬𝐬𝐢𝐛𝐥𝐞 !')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('♥️ Love @Filmykeedha ♥️')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nमैं आपके किसी भी ग्रुप से कनेक्ट या जुड़ी नही हूं।\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞 @Filmykeedha ♥️')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!\nऐसा करने के लिए आपको समूह का owner या admin होना चाहिए!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("𝐓𝐡𝐚𝐭'𝐬 𝐧𝐨𝐭 𝐟𝐨𝐫 𝐲𝐨𝐮 𝐬𝐨𝐧𝐚!\n यह तुम्हारे लिए नहीं है!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = clean_file_name(files.file_name)
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('𝐂𝐡𝐞𝐜𝐤 𝐘𝐨𝐮𝐫 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞, 𝐈 𝐡𝐚𝐯𝐞 𝐬𝐞𝐧𝐭 𝐟𝐢𝐥𝐞𝐬 𝐢𝐧 𝐩𝐦', show_alert=True)
        except UserIsBlocked:
            await query.answer('𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐭𝐡𝐞 𝐁𝐨𝐭!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = BUTTON0.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS1.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS2.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
            
    
    
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("𝐈𝐬𝐤𝐨 𝐉𝐨𝐢𝐧 𝐊𝐚𝐫 𝐏𝐡𝐥𝐞 ✋🏻", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = clean_file_name(files.file_name)
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕↖️ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀\nमुझे GROUP में add करे। ↗️➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🧞‍♀️ 𝗦𝗲𝗮𝗿𝗰𝗵 🧐', switch_inline_query_current_chat=''),
            InlineKeyboardButton('✪𝙂𝙍𝙊𝙐𝙋✪', url='https://t.me/filmykeedha_search')
        ], [
            InlineKeyboardButton('🙆🏻 𝗛𝗲𝗹𝗽 🦾', callback_data='help'),
            InlineKeyboardButton('♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('𝗠𝗮𝗻𝘂𝗮𝗹 𝗙𝗶𝗹𝘁𝗲𝗿', callback_data='manuelfilter'),
            InlineKeyboardButton('𝗔𝘂𝘁𝗼 𝗙𝗶𝗹𝘁𝗲𝗿', callback_data='autofilter')
        ], [
            InlineKeyboardButton('𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻', callback_data='coct'),
            InlineKeyboardButton('𝗘𝘅𝘁𝗿𝗮 𝗠𝗼𝗱𝘀', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 𝗛𝗼𝗺𝗲', callback_data='start'),
            InlineKeyboardButton('🦠 𝗦𝘁𝗮𝘁𝘂𝘀', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('⁠✪𝙂𝙍𝙊𝙐𝙋✪ ', url='https://t.me/filmykeedha_search'),
            InlineKeyboardButton('♥️ 𝗦𝗼𝘂𝗿𝗰𝗲', callback_data='source')
        ], [
            InlineKeyboardButton('🏠 𝗛𝗼𝗺𝗲', callback_data='start'),
            InlineKeyboardButton('🔐 𝗖𝗹𝗼𝘀𝗲', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('◉⁠𝐁𝐮𝐭𝐭𝐨𝐧𝐬', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('♚ 𝗔𝗱𝗺𝗶𝗻', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('↺', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('↺', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    req = message.from_user.id if message.from_user else 0
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)} ⊙ {clean_file_name(file.file_name)}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}") #,
            #InlineKeyboardButton("ʟanguage", callback_data=f"languages#{key}"),
            #InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
        ])
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{clean_file_name(file.file_name)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            
        
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}") #,
           # InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
            #InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
        ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"⁠✧✧ 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="(⁠✧ 1/1 ✧", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"𝐒𝐚𝐡𝐞𝐛! 𝐌𝐮𝐣𝐡𝐞 𝐊𝐮𝐜𝐡 𝐌𝐢𝐥𝐚 𝐇𝐚𝐢 {search}\n\n"
    if imdb and imdb.get('poster'):
        try:
            await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("𝐇𝐞𝐲! 𝐌𝐮𝐣𝐡𝐞 𝐢𝐬 𝐧𝐚𝐚𝐦 𝐬𝐞 𝐤𝐨𝐢 𝐦𝐨𝐯𝐢𝐞 𝐧𝐡𝐢 𝐦𝐢𝐥𝐢,\n 𝐌𝐮𝐣𝐡𝐞 𝐥𝐠𝐭𝐚 𝐡𝐚𝐢 𝐤𝐢 𝐚𝐚𝐩𝐧𝐞 𝐬𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐠𝐚𝐥𝐚𝐭 𝐥𝐢𝐤𝐡 𝐝𝐢𝐢 𝐡 🤷‍♀️!\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐬𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐨𝐧𝐜𝐞 𝐚𝐠𝐚𝐢𝐧 🤦‍♀️... 𝐨𝐫 \n 𝐉𝐨𝐢𝐧 @Filmykeedha .")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("𝐇𝐞𝐲 𝗕𝗿𝗼! 𝐌𝐮𝐣𝐡𝐞 𝐢𝐬 𝐧𝐚𝐚𝐦 𝐬𝐞 𝐤𝐨𝐢 𝐦𝐨𝐯𝐢𝐞 𝐧𝐡𝐢 𝐦𝐢𝐥𝐢, \n𝐌𝐮𝐣𝐡𝐞 𝐥𝐠𝐭𝐚 𝐡𝐚𝐢 𝐤𝐢 𝐚𝐚𝐩𝐧𝐞 𝐬𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐠𝐚𝐥𝐚𝐭 𝐥𝐢𝐤𝐡 𝐝𝐢𝐢 𝐡 !\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐬𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐨𝐧𝐜𝐞 𝐚𝐠𝐚𝐢𝐧 ... 𝐨𝐫 \n 𝐉𝐨𝐢𝐧 @Filmykeedha ")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply("𝐇𝐞𝐲 𝗕𝗿𝗼! 𝐌𝐮𝐣𝐡𝐞 𝐢𝐬 𝐧𝐚𝐚𝐦 𝐬𝐞 𝐤𝐨𝐢 𝐦𝐨𝐯𝐢𝐞 𝐧𝐡𝐢 𝐦𝐢𝐥𝐢, \n𝐌𝐮𝐣𝐡𝐞 𝐥𝐠𝐭𝐚 𝐡𝐚𝐢 𝐤𝐢 𝐚𝐚𝐩𝐧𝐞 𝐬𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐠𝐚𝐥𝐚𝐭 𝐥𝐢𝐤𝐡 𝐝𝐢𝐢 𝐡 !\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐬𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐨𝐧𝐜𝐞 𝐚𝐠𝐚𝐢𝐧 ... 𝐨𝐫 \n 𝐉𝐨𝐢𝐧 @Filmykeedha ",
                    reply_markup=InlineKeyboardMarkup(btn))


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
