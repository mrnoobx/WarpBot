from dotenv import load_dotenv
from logging import getLogger, FileHandler, StreamHandler, basicConfig, INFO
from os import environ, path as ospath
from telethon import TelegramClient
from time import time


if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

if not ospath.exists('.mode.txt'):
    with open('.mode.txt', 'w') as f:
        f.write("True")


basicConfig(format="%(asctime)s: [%(levelname)s: %(filename)s - %(lineno)d] ~ %(message)s",
            handlers=[FileHandler('log.txt'), StreamHandler()],
            datefmt='%d-%b-%y %I:%M:%S %p',
            level=INFO)

LOGGER = getLogger(__name__)

load_dotenv("config.env", override=True)

warp_data = {}

botStartTime = time()

BOT_TOKEN = environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    LOGGER.info("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

TELEGRAM_API = environ.get("TELEGRAM_API")
if not TELEGRAM_API:
    LOGGER.info("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

TELEGRAM_HASH = environ.get("TELEGRAM_HASH")
if not TELEGRAM_HASH:
    LOGGER.info("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

OWNER_ID = int(environ.get("OWNER_ID"))
if not OWNER_ID:
    LOGGER.info("OWNER_ID variable is missing! Exiting now")
    exit(1)

CHANNEL_ID = environ.get("CHANNEL_ID", "")
CHANNEL_ID = int(CHANNEL_ID) if CHANNEL_ID else None

IMAGES = environ.get("IMAGES", "https://telegra.ph//file/96e3363f6860cf473dbec.png https://telegra.ph//file/cd1410acc55167e4d45d8.png https://telegra.ph//file/9f054f9b51ec8e97bd1fc.png https://telegra.ph//file/7c6801f387b4274be9c61.png https://telegra.ph//file/4e3776bb49127c1b61f2e.png https://telegra.ph//file/5f63dbd68e55b33034d81.png https://telegra.ph//file/6380657c5d64942d70ed2.png https://telegra.ph//file/1e8ead7038c375df15d5d.png https://telegra.ph//file/b99a7ecdbe2c7dd58c1c2.png https://telegra.ph//file/b5f1b2be2b1726872183f.png")
imgs_dict = {x: y.strip() for x, y in enumerate(IMAGES.split(), start=1)}

SEND_LOG = environ.get("SEND_LOG", "False").lower() == "true"
HIDE_ID = environ.get("HIDE_ID", "False").lower() == "true"
TIME_ZONE = environ.get("TIME_ZONE", "Asia/Jakarta")
TIME_ZONE_TITLE = environ.get("TIME_ZONE_TITLE", "UTC+7")
PICS_STATS = environ.get("PICS_STATS", "https://i.postimg.cc/gjRYbVzZ/warp.png")
PIC_OFF = environ.get('PIC_OFF', 'https://i.postimg.cc/Gmn3YmnW/Off.png')
PIC_ON = environ.get('PIC_ON', 'https://i.postimg.cc/WzK3xGKz/On.png')
COOLDOWN = int(environ.get("COOLDOWN", 20))
TASK_MAX = int(environ.get("TASK_MAX", 5))
PROG_FINISH = environ.get("PROG_FINISH", "⬢")
PROG_UNFINISH = environ.get("PROG_UNFINISH", "⬡")
START_CMD = environ.get("START_CMD", "start")
STATS_CMD = environ.get("STATS_CMD", "stats")
RESTART_CMD = environ.get("RESTART_CMD", "restart")
DEL_CMD = environ.get("DEL_CMD", "del")
LOG_CMD = environ.get("LOG_CMD", "log")
MODE_CMD = environ.get("MODE_CMD", "mode")

bot = TelegramClient(None, api_id=TELEGRAM_API, api_hash=TELEGRAM_HASH)