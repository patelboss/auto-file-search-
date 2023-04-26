from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired

"""-----------------------------------------https://t.me/pankaj_patel_p --------------------------------------"""

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            total=await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous" 
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, r_j))       
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            # Inspired from a boat of a banana tree
            buttons = [[
                InlineKeyboardButton('𝐒𝐮𝐩𝐩𝐨𝐫𝐭', url=f'https://t.me/pankaj_patel_p')
            ]]
            reply_markup=InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>𝘾𝙃𝘼𝙏 𝙉𝙊𝙏 𝘼𝙇𝙇𝙊𝙒𝙀𝘿 🐞\n\n𝗠𝘆 𝗔𝗱𝗺𝗶𝗻𝘀 𝗛𝗮𝘀 𝗥𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗠𝗲 𝗙𝗿𝗼𝗺 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 𝗛𝗲𝗿𝗲 ! 𝗜𝗳 𝗬𝗼𝘂 𝗪𝗮𝗻𝘁 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗠𝗼𝗿𝗲 𝗔𝗯𝗼𝘂𝘁 𝗜𝘁 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗦𝘂𝗽𝗽𝗼𝗿𝘁..मेरे एडमिन ने मुझे यहाँ काम करने से प्रतिबंधित कर दिया है! यदि आप इसके बारे में अधिक जानना चाहते हैं तो 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 पर संपर्क करें</b>',
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [[
            InlineKeyboardButton('🤥सहायता 𝗛𝗲𝗹𝗽', url=f"https://t.me/{temp.U_NAME}?start=help"),
            InlineKeyboardButton('🔔 सूचना 𝗦𝘂𝗽𝗽𝗼𝗿𝘁', url='https://t.me/Pankaj_patel_p')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>𝐓𝐡𝐚𝐧𝐤𝐲𝐨𝐮 𝐅𝐨𝐫 𝐀𝐝𝐝𝐢𝐧𝐠 𝐌𝐞 𝐈𝐧 मुझे जोड़ने के लिए धन्यवाद {message.chat.title} ❣️\n\n𝗜𝗳 𝗬𝗼𝘂 𝗛𝗮𝘃𝗲 𝗔𝗻𝘆 𝗤𝘂𝗲𝘀𝘁𝗶𝗼𝗻𝘀 & 𝗗𝗼𝘂𝗯𝘁𝘀 𝗔𝗯𝗼𝘂𝘁 𝗨𝘀𝗶𝗻𝗴 𝗠𝗲 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗦𝘂𝗽𝗽𝗼𝗿𝘁. यदि मुझे उपयोग करने में कोई समस्या हो तो सहायता के लिए 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 पर संपर्क करें।</b>",
            reply_markup=reply_markup)
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply(f"<b>𝗛𝗲𝘆 , {u.mention}, 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 {message.chat.title} मुस्कुराइए आप {message.chat.title} में है</b>")


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐂𝐡𝐚𝐭 𝐈𝐃')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('𝐒𝐮𝐩𝐩𝐨𝐫𝐭', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text=f'<b>𝐇𝐞𝐥𝐥𝐨 𝐅𝐫𝐢𝐞𝐧𝐝𝐬, \n𝐌𝐲 𝐀𝐝𝐦𝐢𝐧 𝐇𝐚𝐬 𝐓𝐨𝐥𝐝 𝐌𝐞 𝐓𝐨 𝐋𝐞𝐚𝐯𝐞 𝐅𝐫𝐨𝐦 𝐆𝐫𝐨𝐮𝐩 , 𝐈𝐟 𝐘𝐨𝐮 𝐖𝐚𝐧𝐧𝐚 𝐀𝐝𝐝 𝐌𝐞 𝐀𝐠𝐚𝐢𝐧 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐌𝐲 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝐆𝐫𝐨𝐮𝐩.मेरे एडमिन ने मुझे यहाँ काम करने से रोक दिया है! खतम टाटा बाई बाय! यदि आप इसके बारे में अधिक जानना चाहते हैं तो 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 पर संपर्क करें</b> \n𝐑𝐞𝐚𝐬𝐨𝐧 : <code>{reason}</code>',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐂𝐡𝐚𝐭 𝐈𝐃')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "𝐍𝐨 𝐑𝐞𝐚𝐬𝐨𝐧 𝐏𝐫𝐨𝐯𝐢𝐝𝐞𝐝"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐂𝐡𝐚𝐭 𝐈𝐃')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("𝐂𝐡𝐚𝐭 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝 𝐈𝐧 𝐃𝐁")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/Pankaj_patel_p')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>𝐇𝐞𝐥𝐥𝐨 𝐅𝐫𝐢𝐞𝐧𝐝𝐬, \n𝐌𝐲 𝐀𝐝𝐦𝐢𝐧 𝐇𝐚𝐬 𝐓𝐨𝐥𝐝 𝐌𝐞 𝐓𝐨 𝐋𝐞𝐚𝐯𝐞 𝐅𝐫𝐨𝐦 𝐆𝐫𝐨𝐮𝐩 , 𝐈𝐟 𝐘𝐨𝐮 𝐖𝐚𝐧𝐧𝐚 𝐀𝐝𝐝 𝐌𝐞 𝐀𝐠𝐚𝐢𝐧 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐌𝐲 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝐆𝐫𝐨𝐮𝐩.मेरे एडमिन ने मुझे यहाँ काम करने से रोक दिया है! खतम टाटा बाई बाय! यदि आप इसके बारे में अधिक जानना चाहते हैं तो 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 पर संपर्क करें</b> \n𝐑𝐞𝐚𝐬𝐨𝐧 : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id मुझे Chat ID दीजिए')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID कृपया मुझे सही chat id दे')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB यह Chat हमारे दस्तावेजों में नहीं है !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled. यह Chat अभी बंद नहीं किया गया')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('Fetching stats..')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await rju.edit(script.STATUS_TXT.format(files, total_users, totl_chats, size, free))


# a function for trespassing into others groups, Inspired by a Vazha
# Not to be used , But Just to showcase his vazhatharam.
# @Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐂𝐡𝐚𝐭 𝐈𝐃 \nमुझे सही chat id दे')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID  कृपया मुझे सही chat id दे !')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("𝐈𝐧𝐯𝐢𝐭𝐞 𝐋𝐢𝐧𝐤 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐅𝐚𝐢𝐥𝐞𝐝, 𝐈 𝐚𝐦 𝐍𝐨𝐭 𝐇𝐚𝐯𝐢𝐧𝐠 𝐒𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐑𝐢𝐠𝐡𝐭𝐬. आमंत्रण लिंक बनाने में असमर्थ, शायद मुझे पर्याप्त अधिकार प्राप्त नहीं है")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'𝐇𝐞𝐫𝐞 𝐈𝐬 𝐘𝐨𝐮𝐫 𝐈𝐧𝐯𝐢𝐭𝐞 𝐋𝐢𝐧𝐤 {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply('𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐔𝐬𝐞𝐫 𝐈𝐝 / 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞\nमुझे यूजर id या यूजरनेम दीजिए')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "𝐍𝐨 𝐑𝐞𝐚𝐬𝐨𝐧 𝐏𝐫𝐨𝐯𝐢𝐝𝐞𝐝"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("𝐓𝐡𝐢𝐬 𝐈𝐬 𝐀𝐧 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫, 𝐌𝐚𝐤𝐞 𝐒𝐮𝐫𝐞 𝐈 𝐇𝐚𝐯𝐞 𝐌𝐞𝐭 𝐇𝐢𝐦 𝐁𝐞𝐟𝐨𝐫𝐞. यह id गलत है क्योंकि यह उनमें से नही है जिनसे मेने संपर्क किया है।")
    except IndexError:
        return await message.reply("𝐓𝐡𝐢𝐬 𝐦𝐢𝐠𝐡𝐭 𝐛𝐞 𝐚 𝐜𝐡𝐚𝐧𝐧𝐞𝐥, 𝐦𝐚𝐤𝐞 𝐬𝐮𝐫𝐞 𝐢𝐭𝐬 𝐚 𝐮𝐬𝐞𝐫. आप पहले प्रमाणित करे की यह एक यूजर है। मुझे लगता है की यह किसी चैनल की id है")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} 𝐈𝐬 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐁𝐚𝐧𝐧𝐞𝐝 पहले से ही प्रतिबंधित है\n𝐑𝐞𝐚𝐬𝐨𝐧 (कारण): {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐁𝐚𝐧𝐧𝐞𝐝 ! सुधर जाओ तो फिर आ जाना {k.mention}")


    
@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐔𝐬𝐞𝐫 𝐈𝐝 / 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "𝐍𝐨 𝐑𝐞𝐚𝐬𝐨𝐧 𝐏𝐫𝐨𝐯𝐢𝐝𝐞𝐝"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("𝐓𝐡𝐢𝐬 𝐈𝐬 𝐀𝐧 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫, 𝐌𝐚𝐤𝐞 𝐒𝐮𝐫𝐞 𝐈 𝐇𝐚𝐯𝐞 𝐌𝐞𝐭 𝐇𝐢𝐦 𝐁𝐞𝐟𝐨𝐫𝐞.यह id गलत है क्योंकि यह उनमें से नही है जिनसे मेने संपर्क किया है।")
    except IndexError:
        return await message.reply("𝐓𝐡𝐢𝐬 𝐦𝐢𝐠𝐡𝐭 𝐛𝐞 𝐚 𝐜𝐡𝐚𝐧𝐧𝐞𝐥, 𝐦𝐚𝐤𝐞 𝐬𝐮𝐫𝐞 𝐢𝐭𝐬 𝐚 𝐮𝐬𝐞𝐫.आप पहले प्रमाणित करे की यह एक यूजर है। मुझे लगता है की यह किसी चैनल की id है")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} 𝐢𝐬 𝐧𝐨𝐭 𝐲𝐞𝐭 𝐛𝐚𝐧𝐧𝐞𝐝. अभी बैन नही हुआ")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐔𝐧𝐛𝐚𝐧𝐧𝐞𝐝 ! सुबह का भूला अगर शाम को घर आ जाए तो उसे भुला नहीं कहते। {k.mention}")


    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply('𝐆𝐞𝐭𝐭𝐢𝐧𝐠 𝐋𝐢𝐬𝐭 𝐎𝐟 𝐔𝐬𝐞𝐫 𝐁𝐚𝐛𝐲 !')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('𝐆𝐞𝐭𝐭𝐢𝐧𝐠 𝐋𝐢𝐬𝐭 𝐎𝐟 𝐂𝐡𝐚𝐭𝐬 𝐁𝐄𝐁𝐒 !')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
