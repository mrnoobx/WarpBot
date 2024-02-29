import asyncio
import datetime
import json
import random
import string
import urllib.request

from pytz import timezone
from telethon import Button
from time import time

from bot import warp_data, imgs_dict, COOLDOWN, LOGGER, HIDE_ID, CHANNEL_ID, PROG_FINISH, PROG_UNFINISH, SEND_LOG, TIME_ZONE, TIME_ZONE_TITLE, OWNER_ID
from bot.helpers.utils import get_readable_time, get_readable_file_size, editMessage, sendMessage


LOGGER.info("WARP+ Cloudflare")

def genString(stringLength):
    try:
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(stringLength))
    except Exception as error:
        LOGGER.error(error)

def digitString(stringLength):
    try:
        digit = string.digits
        return ''.join((random.choice(digit) for i in range(stringLength)))
    except Exception as error:
        LOGGER.error(error)


class WrapPlus:
    def __init__(self, user_id, warp_id, message):
        self.__uid = user_id
        self.__wid  = warp_id
        self.__message = message
        self.__edited = None
        self.__succ = 0
        self.__fail = 0
        self.__bw = 0
        self.__count = 1
        self.__start = time()
        self.__dt = message.date.astimezone(timezone(TIME_ZONE))
        self.__add_data()

    def __add_data(self):
        if self.__uid in warp_data:
            warp_data[self.__uid][self.__message.id] = {'data': self}
        else:
            warp_data[self.__uid] = {self.__message.id:{'data': self}}

    async def onStart(self):
        buttons = [Button.inline('Stop', f'stop {self.__message.id}')]
        while True:
            text_log = f"<b>├ Received:</b> {get_readable_file_size(self.__bw)}\n"
            text_log += f"<b>├ Success:</b> {self.__succ}\n"
            text_log += f"<b>├ Failed:</b> {self.__fail}\n"
            text_log += f"<b>├ Total:</b> {self.__succ + self.__fail}\n"
            text_log += f"<b>├ Elapsed:</b> {get_readable_time(time() - self.__start)}\n"
            text_log += f"<b>├ At:</b> {self.__dt.strftime('%H:%M:%S')} ({TIME_ZONE_TITLE})\n"
            text_log += f"<b>└ Add:</b> {self.__dt.strftime('%B %d, %Y')}"
            F, UF = PROG_FINISH, PROG_UNFINISH
            prgss_bar = [F*2 + UF*8, F*4 + UF*6, F*6 + UF*4, F*8 + UF*2, F*10]
            prgss_prcn = ["20%", "40%", "60%", "80%", "100%"]
            for i in range(len(prgss_bar)):
                text = "<b>WARP+ INJECTOR</b>\n"
                if not HIDE_ID:
                    text += f"<code>{self.__wid}</code>\n"
                text += f"<b>┌ </b>{prgss_bar[i % len(prgss_bar)]}\n"
                text += f"<b>├ Progress:</b> {prgss_prcn[i % len(prgss_bar)]}\n"
                self.__edited = await editMessage(text + text_log, self.__message, buttons, imgs_dict[self.__count])
                await self.__check()
            if self.__run == 200:
                self.__succ += 1
                self.__bw += 1 * 1024**3
                if SEND_LOG:
                    await sendMessage(text_log, None, chat=CHANNEL_ID)
                for i in range(COOLDOWN, -1, -5):
                    text = "<b>WARP+ INJECTOR</b>\n"
                    if not HIDE_ID:
                        text += f"<code>{self.__wid}</code>\n"
                    text += f"<b>┌ Cooldown:</b> {i}s\n"
                    text += f"<b>├ Progress:</b> 0%\n"
                    self.__edited = await editMessage(text + text_log, self.__message, buttons, imgs_dict[self.__count])
                    await self.__check()
            else:
                self.__fail += 1
                LOGGER.info(f"Total: {self.__succ} Good {self.__fail} Bad")
                for i in range(COOLDOWN, -1, -5):
                    text = "<b>WARP+ INJECTOR</b>\n"
                    if not HIDE_ID:
                        text += f"<code>{self.__wid}</code>\n"
                    text += f"<b>┌ Cooldown:</b> {i}s\n"
                    text += f"<b>├ Progress:</b> 0%\n"
                    self.__edited = await editMessage(text + text_log, self.__message, buttons, imgs_dict[self.__count])
                    await self.__check()

    async def __check(self):
        if not self.__edited:
            warp_data[self.__uid][self.__message.id]['task'].cancel()
            await sendMessage(f'Message has been deleted and task stopped\n\n{self.result}',self.__message, file=imgs_dict[5])
            self.clean_data()
            return
        self.__count += 1
        if self.__count == len(imgs_dict):
            self.__count = 1
        await asyncio.sleep(3)

    def clean_data(self):
        try:
            if self.__uid == OWNER_ID:
                del warp_data[self.__uid][self.__message.id]
            else:
                del warp_data[self.__uid]
        except:
            pass

    @property
    def result(self):
        LOGGER.info(f"Task stopped!: {self.__wid}")
        text = "<b>TASK STOPPED!</b>\n"
        if not HIDE_ID:
            text += f"<code>{self.__wid}</code>\n"
        text += f"<b>┌ Received: </b>{get_readable_file_size(self.__bw)}\n"
        text += f"<b>├ Task Success: </b>{self.__succ}\n"
        text += f"<b>├ Task Failed: </b>{self.__fail}\n"
        text += f"<b>├ Task Total: </b>{self.__succ + self.__fail}\n"
        text += f"<b>└ Elapsed: </b>{get_readable_time(time() - self.__start)}"
        return text

    @property
    def __run(self):
        try:
            install_id = genString(22)
            body = {"key": f"{genString(43)}=",
                    "install_id": install_id,
                    "fcm_token": f"{install_id}:APA91b{genString(134)}",
                    "referrer": self.__wid,
                    "warp_enabled": False,
                    "tos": f"{datetime.datetime.now().isoformat()[:-3]}+02:00",
                    "type": "Android",
                            "locale": "es_ES"}
            headers = {'Content-Type': 'application/json; charset=UTF-8',
                    'Host': 'api.cloudflareclient.com',
                    'Connection': 'Keep-Alive',
                    'Accept-Encoding': 'gzip',
                    'User-Agent': 'okhttp/3.12.1'}
            data = json.dumps(body).encode('utf8')
            url = f'https://api.cloudflareclient.com/v0a{digitString(3)}/reg'
            req = urllib.request.Request(url, data, headers)
            response = urllib.request.urlopen(req)
            return response.getcode()
        except Exception as error:
            LOGGER.error(f"Error: {error}")