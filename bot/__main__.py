import asyncio

from os import path as ospath, remove as osremove, execl as osexecl
from platform import system, architecture, release
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from subprocess import check_output, run as srun
from sys import executable
from telethon import events, Button
from time import time

from bot import bot, botStartTime, warp_data, imgs_dict, BOT_TOKEN, MODE_CMD, DEL_CMD, LOG_CMD, RESTART_CMD, LOGGER, OWNER_ID, \
                COOLDOWN, TASK_MAX, START_CMD, STATS_CMD, PICS_STATS
from bot.helpers.utils import sendMessage, deleteMessage, editMessage, get_readable_time, get_readable_file_size, \
                              progress_bar, check, private_mode, get_mode, GSetMode
from bot.helpers.warp_plus import WrapPlus


async def start(event):
    await sendMessage('This is <b>Warp+ Injector</b>. Just send your id here...', event, [Button.inline('Close', 'close')])

async def stats(event):
    last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd\n<b>├ Commit Change:</b> %cr'"],
                               shell=True).decode() if ospath.exists('.git') else 'No UPSTREAM_REPO'
    stats = f'''
<b>UPSTREAM AND BOT STATUS</b>
<b>┌ Commit Date:</b> {last_commit}
<b>├ Bot Uptime:</b> {get_readable_time(time() - botStartTime)}
<b>└ OS Uptime:</b> {get_readable_time(time() - boot_time())}\n
<b>SYSTEM STATUS</b>
<b>┌ SWAP:</b> {get_readable_file_size(swap_memory().total)}
<b>├ Total Cores:</b> {cpu_count(logical=True)}
<b>├ Physical Cores:</b> {cpu_count(logical=False)}
<b>├ Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}
<b>├ Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}
<b>├ Disk Free:</b> {get_readable_file_size(disk_usage('/')[2])}
<b>├ Disk Used:</b> {get_readable_file_size(disk_usage('/')[1])}
<b>├ Disk Space:</b> {get_readable_file_size(disk_usage('/')[0])}
<b>├ Memory Free:</b> {get_readable_file_size(virtual_memory().available)}
<b>├ Memory Used:</b> {get_readable_file_size(virtual_memory().used)}
<b>├ Memory Total:</b> {get_readable_file_size(virtual_memory().total)}
<b>├ CPU:</b> {progress_bar(cpu_percent(interval=1))} {cpu_percent(interval=1)}%
<b>├ RAM:</b> {progress_bar(virtual_memory().percent)} {virtual_memory().percent}%
<b>├ DISK:</b> {progress_bar(disk_usage('/')[3])} {disk_usage('/')[3]}%
<b>├ SWAP:</b> {progress_bar(swap_memory().percent)} {swap_memory().percent}%
<b>└ OS:</b> {system()}, {architecture()[0]}, {release()}
'''
    await sendMessage(stats, event, [Button.inline('Close', 'close')], PICS_STATS)

async def send_log(event):
    if await check(event):
        return
    await sendMessage('Logs', event, file='log.txt')

async def restart(event):
    if await check(event):
        return
    rmsg = await sendMessage('<i>Resatarting...</i>', event)
    srun(['python3', 'update.py'])
    with open('.restartmsg', 'w') as f:
        f.truncate(0)
        f.write(f'{event.chat.id}\n{rmsg.id}\n')
    osexecl(executable, executable, '-m', 'bot')

async def del_msg(event):
    start_time  = time()
    reply = await event.get_reply_message()
    if not reply:
        await sendMessage('Reply to a message!', event)
        return
    msg = await sendMessage('<i>Deleting messages...</i>', event)
    delmsg = await deleteMessage(event, [x for x in range(reply.id, event.id)])
    if not delmsg:
        await editMessage('Old message!', msg)
        return
    await deleteMessage(event)
    await editMessage(f'Complete deleted messages in {get_readable_time(time() - start_time)}', msg)

async def mode(event):
    if await check(event):
        return
    text, image, button,  = get_mode()
    await sendMessage(text, event, button, image)

async def warp_handler(event):
    sender = await event.get_sender()
    wid = event.raw_text.strip()
    if len(wid) != 36 or await private_mode(event):
        return
    elif '-' not in wid:
        await sendMessage('Invalid ID!', event)
    elif sender.id in warp_data and sender.id != OWNER_ID:
        await sendMessage(f'Ups, you can only add 1 task!', event)
    elif len(warp_data) >= TASK_MAX:
        await sendMessage(f'Ups, bot task limit is {TASK_MAX}!', event)
    else:
        msg = await sendMessage('<i>Cheching your ID, please wait...</i>', event)
        LOGGER.info(f'Found Warp ID: {wid}')
        await asyncio.sleep(3)
        await deleteMessage(msg)
        uname = f"<a href='https://t.me/{sender.id}'>{sender.first_name}</a>"
        caption = f'{uname}... This ID will proccess to added 1GB warp+ quota every {COOLDOWN} seconds...\n<code>{wid}</code>'
        msg = await sendMessage(caption, event, file=imgs_dict[5])
        await asyncio.sleep(5)
        wplus = WrapPlus(sender.id, wid, msg)
        task = asyncio.create_task(wplus.onStart())
        warp_data[sender.id][msg.id]['task'] = task

async def callback(event):
    message = await event.get_message()
    sender = await event.get_sender()
    data = event.data.decode('utf-8').split()
    if data[0] == 'mode':
        await event.answer()
        gset = GSetMode()
        gset.set_mode(not gset.is_private())
        text, image, button  = get_mode()
        await editMessage(text, message, button, image)
    elif data[0] == 'stop':
        if wdata := warp_data.get(sender.id, {}).get(int(data[1]), {}):
            await event.answer('Stopping task...')
            wdata['task'].cancel()
            await editMessage(wdata['data'].result, message)
            wdata['data'].clean_data()
        else:
            await event.answer('Old task!', alert=True)
    else:
        await deleteMessage(event, [message, await message.get_reply_message()])

async def main():
    bot.parse_mode = 'HTML'
    if ospath.isfile('.restartmsg'):
        with open('.restartmsg') as f:
            chat_id, msg_id = map(int, f)
        msg = 'Restart Successfully!'
    else:
        msg = '⚡️ Bot Ready...'
    if 'Restart Successfully!' in msg:
        await bot.edit_message(chat_id, msg_id, msg)
        osremove('.restartmsg')
    else:
        await sendMessage(msg, None, chat=OWNER_ID)
    bot.add_event_handler(start, events.NewMessage(pattern=f'/{START_CMD}'))
    bot.add_event_handler(stats, events.NewMessage(pattern=f'/{STATS_CMD}'))
    bot.add_event_handler(del_msg, events.NewMessage(pattern=f'/{DEL_CMD}'))
    bot.add_event_handler(restart, events.NewMessage(pattern=f'/{RESTART_CMD}'))
    bot.add_event_handler(send_log, events.NewMessage(pattern=f'/{LOG_CMD}'))
    bot.add_event_handler(mode, events.NewMessage(pattern=f'/{MODE_CMD}'))
    bot.add_event_handler(warp_handler, events.NewMessage(incoming=True))
    bot.add_event_handler(callback, events.CallbackQuery())
    LOGGER.info('Bot Started!')

bot.flood_sleep_threshold = 24*60*60
bot.start(bot_token=BOT_TOKEN)
bot.loop.run_until_complete(main())
bot.loop.run_forever()
