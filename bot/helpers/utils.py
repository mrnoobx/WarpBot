import asyncio

from os import path as ospath
from telethon import Button
from telethon.errors import FloodWaitError

from bot import bot, warp_data, LOGGER, PROG_UNFINISH, PROG_FINISH, PROG_UNFINISH, OWNER_ID, PIC_ON, PIC_OFF


class GSetMode:
    def __init__(self):
        self.__text = '.mode.txt'
        self.__verify()

    def __verify(self):
        if not ospath.exists(self.__text):
            self.set_mode('True')

    def is_private(self):
        with open(self.__text, 'r') as file:
            return file.read().lower() == 'true'

    def set_mode(self, mode):
        with open(self.__text, 'w') as f:
            f.write(str(mode).strip())

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def get_readable_file_size(size_in_bytes) -> str:
    if not size_in_bytes:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f"{round(size_in_bytes, 2)}{['B', 'KB', 'MB', 'GB', 'TB', 'PB'][index]}"
    except IndexError:
        return 'File to big.'

def progress_bar(percentage):
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage = int(percentage)
    except:
        percentage = 0
    return ''.join(PROG_FINISH if i <= percentage // 10 else PROG_UNFINISH for i in range(1, 11))

async def check(event):
    if event.sender_id != OWNER_ID:
        return await sendMessage('<b>Upss...</b> You can\'t do this, owner only!', event)

async def private_mode(event):
    if event.sender_id != OWNER_ID and GSetMode().is_private():
        return await sendMessage('<b>Upss...</b> private mode active! Contact the owner to make it public access!', event)

def get_mode():
    if GSetMode().is_private():
        mode, bkey, image = 'Enable', 'Disable', PIC_ON
    else:
        mode, bkey, image = 'Disable', 'Enable', PIC_OFF
    return f'Private Mode Is <b>{mode}</b>!', image, [Button.inline(bkey, 'mode')]

async def sendMessage(text, event, buttons=None, file=None, chat=None):
    try:
        if not chat:
            chat = await event.get_chat()
        return await bot.send_message(entity=chat, message=text, buttons=buttons, file=file,
                                      reply_to=event, link_preview=False)
    except FloodWaitError as e:
        LOGGER.warning(e)
        await asyncio.sleep(e.seconds * 1.5)
        return await sendMessage(text, event, buttons, file, chat)
    except Exception as e:
        LOGGER.error(str(e))
        return

async def editMessage(text, message, buttons=None, file=None):
    try:
        return await bot.edit_message(entity=message, message=text, buttons=buttons, file=file)
    except FloodWaitError as e:
        LOGGER.warning(e)
        await asyncio.sleep(e.seconds * 1.5)
        return await editMessage(text, message, buttons, file)
    except Exception as e:
        LOGGER.error(str(e))

async def deleteMessage(event, messages=None):
    try:
        return await bot.delete_messages(entity=await event.get_chat(), message_ids=messages or event.id)
    except Exception as e:
        LOGGER.error(e)
