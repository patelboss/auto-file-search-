#from database.verified import *
import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client
from info import *
from datetime import datetime, date
import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM
from imdb import IMDb
import asyncio
from pyrogram.types import Message, InlineKeyboardButton
from pyrogram import enums
from typing import Union
import re
import os
#from datetime import datetime
from typing import List
from database.users_chats_db import db
from bs4 import BeautifulSoup
import requests
from shortzy import Shortzy
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = IMDb() 
TOKENS = {}
VERIFIED = {}
BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

# temp db for banned 
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    GETALL = {}
    SHORT = {}
    SETTINGS = {}
    
import os
from pyrogram.errors import UserNotParticipant
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Fetch the channel IDs from environment variables
AUTH_CHANNELS = os.getenv("AUTH_CHANNELS", "").split(",")  # Get the list of channel IDs
REQUEST_TO_JOIN_MODE = 'False'
import logging

async def is_subscribed(bot, query):
    missing_channels = []
    
    if REQUEST_TO_JOIN_MODE == True and join_db().isActive():
        try:
            user = await join_db().get_user(query.from_user.id)
            if user and user["user_id"] == query.from_user.id:
                return True
            else:
                for channel_id in AUTH_CHANNELS:
                    try:
                        user_data = await bot.get_chat_member(int(channel_id), query.from_user.id)
                    except UserNotParticipant:
                        channel = await bot.get_chat(int(channel_id))
                        missing_channels.append(
                            InlineKeyboardButton(f"Join {channel.title}", url=channel.invite_link)
                        )
                    except Exception as e:
                        return False  # Return False if there's an error

                # Send missing channels if needed
                if missing_channels:
                    reply_markup = InlineKeyboardMarkup([missing_channels])
                    
                    # Adjust based on object type
                    if isinstance(query, CallbackQuery):
                        await query.answer(
                            text="Please join all required channels & Unmute Them to use the bot.\nTap on Files Again",
                            show_alert=True
                        )
                        await query.message.reply("Join the channels using the buttons below.\nTap on Join Then Unmute\nTap On Files Again To Get Files", reply_markup=reply_markup)
                    else:
                        await query.reply(
                            "You need to join all the required channels & Unmute Them to get the files.",
                            reply_markup=reply_markup
                        )
                    return False

                return True

        except Exception as e:
            return False
    else:
        for channel_id in AUTH_CHANNELS:
            try:
                user = await bot.get_chat_member(int(channel_id), query.from_user.id)
                if user.status == enums.ChatMemberStatus.BANNED:
                    return False
            except UserNotParticipant:
                missing_channels.append(channel_id)
                continue

        if missing_channels:
            join_buttons = []
            for channel_id in missing_channels:
                channel = await bot.get_chat(int(channel_id))
                join_buttons.append(
                    InlineKeyboardButton(f"Join {channel.title}", url=channel.invite_link)
                )
            reply_markup = InlineKeyboardMarkup([join_buttons])

            # Adjust based on object type
            if isinstance(query, CallbackQuery):
                await query.answer(
                    text="Please join all required channels & Unmute Them to use the bot.\nTap on Files Again",
                    show_alert=True
                )
                await query.message.reply("Join the channels using the buttons below.\nTap on Join Then Unmute\nTap On Files Again To Get Files", reply_markup=reply_markup)
            else:
                await query.reply(
                    "You need to join all the required channels & Unmute Them to get the files.",
                    reply_markup=reply_markup
                )
            return False

    return True
    
async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        # https://t.me/GetTGLink/4183
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }
# https://github.com/odysseusmax/animated-lamp/blob/2ef4730eb2b5f0596ed6d03e7b05243d93e3415b/bot/utils/broadcast.py#L37
async def broadcast_messages(user_id, message, forward=False):
    try:
        if forward:
            await message.forward(chat_id=user_id)
        else:
            await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.x} seconds.")
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message, forward)
    except InputUserDeactivated:
        # Delete the user only if the account is deactivated
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - Removed from database (deleted account).")
        return False, "Deleted"
    except UserIsBlocked:
        # Do not delete, just log that the user has blocked the bot
        logger.info(f"{user_id} - Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        # Do not delete, just log that the PeerId is invalid
        logger.info(f"{user_id} - PeerIdInvalid.")
        return False, "Error"
    except Exception as e:
        logger.error(f"Error broadcasting to {user_id}: {e}")
        return False, "Error"
    

async def broadcast_messages_group(chat_id, message, forward=False):
    try:
        if forward:
            await message.forward(chat_id=chat_id)
        else:
            msg = await message.copy(chat_id=chat_id)
            try:
                await msg.pin()  # Attempt to pin the message
            except Exception as e:
                logger.warning(f"Could not pin message in group {chat_id}: {e}")
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.x} seconds.")
        await asyncio.sleep(e.x)
        return await broadcast_messages_group(chat_id, message, forward)
    except Exception as e:
        logger.error(f"Error broadcasting to group {chat_id}: {e}")
        return False, "Error"


async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
        }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all( 'h3' )
    return [title.getText() for title in titles]


async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)
    
def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]  

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
           
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

FILTER_KEYWORDS = ['[', '@', 'www.', 'movie', 'www', 'telegram', 'tg']
#from config import FILTER_KEYWORDS

def clean_file_name(file_name):
    return ' '.join(filter(lambda x: not any(keyword in x for keyword in FILTER_KEYWORDS), file_name.split()))

#InlineKeyboardButton(
#    text=f"☞{get_size(file['file_size'])} ◉ {clean_file_name(file['file_name'])}",
#    callback_data=f'{pre}#{file["file_id"]}'
#)
URL = "api.shareus.io"
SHORTLINK_API = "xLsXcbTQX2fPiDCCA1Wmh5eCLnp1"
VERIFY_SECOND_SHORTNER = "False"
VERIFY_SHORTLINK_API = "xLsXcbTQX2fPiDCCA1Wmh5eCLnp1"
VERIFY_SHORTLINK_URL = "api.shareus.io"

from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import random
import string
from datetime import date

# Initialize MongoDB client (replace with your connection details)
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]  # replace 'your_database' with your actual database name
verified_collection = db['verified_users']

# Helper function to check if a user is verified
async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    
    # Ensure the user exists in the database
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))

    # Fetch the verification status from MongoDB
    verified_user = await verified_collection.find_one({'user_id': userid})

    if verified_user:
        # Check if the verification is within the last 24 hours
        verification_time = verified_user['verified_at']
        if verification_time + timedelta(hours=24) > datetime.utcnow():
            return True  # Verified within the last 24 hours
        else:
            await verified_collection.delete_one({'user_id': userid})  # Remove expired verification
            return False  # Expired verification
    else:
        return False  # User not verified

# Save verification to the database with 24-hour expiry
async def verify_user(bot, userid, token):
    user = await bot.get_users(userid)
    
    # Ensure the user exists in the database
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))

    # Mark the token as used
    TOKENS[user.id] = {token: True}

    # Save verification status in MongoDB with timestamp
    verified_data = {
        'user_id': user.id,
        'verified_at': datetime.utcnow()  # Store the current UTC time for verification
    }

    # Insert or update the user's verification status in MongoDB
    await verified_collection.update_one(
        {'user_id': user.id},
        {'$set': verified_data},
        upsert=True  # Create the document if it doesn't exist
    )

# Function to generate token for the user
async def get_token(bot, userid, link):
    user = await bot.get_users(userid)

    # Check if user is already verified
    if await check_verification(bot, userid):
        return "You are already verified."

    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))

    # Generate a new token
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}  # Store the token in the temporary dictionary

    # Generate the verification link
    verification_link = f"{link}verify-{user.id}-{token}"
    shortened_verify_url = await get_verify_shorted_link(verification_link, VERIFY_SHORTLINK_URL, VERIFY_SHORTLINK_API)

    if VERIFY_SECOND_SHORTNER:
        snd_link = await get_verify_shorted_link(shortened_verify_url, VERIFY_SND_SHORTLINK_URL, VERIFY_SND_SHORTLINK_API)
        return str(snd_link)
    else:
        return str(shortened_verify_url)

# Function to check if the token is valid and not used
async def check_token(bot, userid, token):
    user = await bot.get_users(userid)

    # Ensure user exists in the database
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))

    # Check if the token exists and is valid
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used:
                return False  # Token already used
            else:
                return True  # Token valid and not used
    else:
        return False  # Token not found

# Helper function to get the shortened verification link (from the previous code)
async def get_verify_shorted_link(link, url, api):
    API = api
    URL = url
    if URL == "api.shareus.io":
        url = f'https://{URL}/easy_api'
        params = {
            "key": API,
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.text()
                    return data
        except Exception as e:
            logger.error(e)
            return link
    else:
        shortzy = Shortzy(api_key=API, base_site=URL)
        link = await shortzy.convert(link)
        return link

async def send_all(bot, userid, files, ident, chat_id, user_name, query):
    settings = await get_settings(chat_id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    try:
        if ENABLE_SHORTLINK:
            for file in files:
                title = file["file_name"]
                size = get_size(file["file_size"])
                if not await db.has_premium_access(userid) and SHORTLINK_MODE == True:
                    await bot.send_message(chat_id=userid, text=f"<b>Hᴇʏ ᴛʜᴇʀᴇ {user_name} 👋🏽 \n\n✅ Sᴇᴄᴜʀᴇ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ғɪʟᴇ ʜᴀs sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴇᴇɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴅᴏᴡɴʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ\n\n🗃️ Fɪʟᴇ Nᴀᴍᴇ : {title}\n🔖 Fɪʟᴇ Sɪᴢᴇ : {size}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 Dᴏᴡɴʟᴏᴀᴅ 📥", url=await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}"))]]))
        else:
            for file in files:
                    f_caption = file["caption"]
                    title = file["file_name"]
                    size = get_size(file["file_size"])
                    if CUSTOM_FILE_CAPTION:
                        try:
                            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                                    file_size='' if size is None else size,
                                                                    file_caption='' if f_caption is None else f_caption)
                        except Exception as e:
                            print(e)
                            f_caption = f_caption
                    if f_caption is None:
                        f_caption = f"{title}"
                    await bot.send_cached_media(
                        chat_id=userid,
                        file_id=file["file_id"],
                        caption=f_caption,
                        protect_content=True if ident == "filep" else False,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                                InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                            ],[
                                InlineKeyboardButton("Check What's New", url="t.me/filmykeedha")
                            ],[
                                InlineKeyboardButton("Want To Earn", url="t.me/earningdailyforyou")
                                ]
                            ]
                        )
                    )
    except UserIsBlocked:
        await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
    except PeerIdInvalid:
        await query.answer('Hᴇʏ, Sᴛᴀʀᴛ Bᴏᴛ Fɪʀsᴛ Aɴᴅ Cʟɪᴄᴋ Sᴇɴᴅ Aʟʟ', show_alert=True)
    except Exception as e:
        await query.answer('Hᴇʏ, Sᴛᴀʀᴛ Bᴏᴛ Fɪʀsᴛ Aɴᴅ Cʟɪᴄᴋ Sᴇɴᴅ Aʟʟ', show_alert=True)
        
