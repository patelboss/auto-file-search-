import re
from os import environ
from database.envs import fetch_config # Ensure this function fetches the MongoDB config properly
#import os
from Script import script 


config_name = "env_config"
config = fetch_config(config_name)
print(config)

VERIFY = bool(config.get('VERIFY')) if config.get('VERIFY') else bool(environ.get('VERIFY', False))
print(f"VERIFY = {VERIFY}")
VERIFY_SECOND_SHORTNER = bool(config.get('VERIFY_SECOND_SHORTNER')) if config.get('VERIFY_SECOND_SHORTNER') else bool(environ.get('VERIFY_SECOND_SHORTNER', False))
print(f"VERIFY_SECOND_SHORTNER = {VERIFY_SECOND_SHORTNER}")
VERIFY_SHORTLINK_URL = config.get('VERIFY_SHORTLINK_URL') if config.get('VERIFY_SHORTLINK_URL') else environ.get('VERIFY_SHORTLINK_URL', '')
print(f"VERIFY_SHORTLINK_URL= {VERIFY_SHORTLINK_URL}")
VERIFY_SHORTLINK_API = config.get('VERIFY_SHORTLINK_API') if config.get('VERIFY_SHORTLINK_API') else environ.get('VERIFY_SHORTLINK_API', '')
print(f"VERIFY_SHORTLINK_API = {VERIFY_SHORTLINK_API}")
VERIFY_SND_SHORTLINK_URL = config.get('VERIFY_SND_SHORTLINK_URL') if config.get('VERIFY_SND_SHORTLINK_URL') else environ.get('VERIFY_SND_SHORTLINK_URL', '')
print(f"VERIFY_SND_SHORTLINK_URL = {VERIFY_SND_SHORTLINK_URL}")
VERIFY_SND_SHORTLINK_API = config.get('VERIFY_SND_SHORTLINK_API') if config.get('VERIFY_SND_SHORTLINK_API') else environ.get('VERIFY_SND_SHORTLINK_API', '')
print(f"VERIFY_SND_SHORTLINK_API = {VERIFY_SND_SHORTLINK_API}")
VERIFY_TUTORIAL = config.get('VERIFY_TUTORIAL') if config.get('VERIFY_TUTORIAL') else environ.get('VERIFY_TUTORIAL', 'https://t.me/Filmykeedha/394')
print(f"VERIFY_TUTORIAL = {VERIFY_TUTORIAL}")
#CUSTOM_FILE_CAPTION = config.get("CUSTOM_FILE_CAPTION") if config.get("CUSTOM_FILE_CAPTION") else environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
#print(f"CUSTOM_FILE_CAPTION = {CUSTOM_FILE_CAPTION}")
AUTH_CHANNELS = config.get("AUTH_CHANNELS").split(",") if config.get("AUTH_CHANNELS") else environ.get(AUTH_CHANNELS).split(",")
#environ.get("AUTH_CHANNELS", "").split(",") if config.get("AUTH_CHANNELS") else []
print(f"AUTH_CHANNELS = {AUTH_CHANNELS}")
DLTTM = int(config.get("DLTTM")) if config.get("DLTTM") else int(environ.get("DLTTM", "4200"))
print(f"DLTTM: {config.get('DLTTM')}")
print(f"DLTTM = {DLTTM}")
WELCOME_VIDEO_ID = config.get("WELCOME_VIDEO_ID") if config.get("WELCOME_VIDEO_ID") else environ.get("MELCOW_VID", "BAACAgQAAxkBAAEWWw5nXJ_bgRy9MY3ZNxpLzbIaysGuswAC2hoAAuLv4VIyB40_JD42Hh4E")
print(f"WELCOME_VIDEO_ID = {WELCOME_VIDEO_ID}")
CUSTOM_FILE_CAPTION = f'{script.CAPTION}'
print(f"CUSTOM_FILE_CAPTION = {CUSTOM_FILE_CAPTION}")
