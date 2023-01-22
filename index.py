from aiogram.types import ContentType, Message
from threading import Thread
from asyncio import new_event_loop, set_event_loop
from workers.bot import Bot
from workers.loader import Loader

import os
import time
import traceback

BOT_API_TOKEN = os.environ.get('BOT_API_TOKEN')

bot = Bot(BOT_API_TOKEN)
dp = bot.dispatcher

@dp.message_handler(content_types=[ContentType.TEXT])
async def handler(message: Message):
    try:
        await bot.text_message_handler(message)
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(is_media_group=True, content_types=[ContentType.PHOTO])
async def handler(message: Message):
    try:
        await bot.media_group_message_handler(message)
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=[ContentType.PHOTO])
async def handler(message: Message):
    try:
        await bot.photo_message_handler(message)
    except Exception as e:
        traceback.print_exc()

def start_bot():
    print('Bot Started!')
    
    set_event_loop(new_event_loop())
    
    bot.start_polling()

def start_post_loader():
    print('Post Loader Started!')
    
    loader = Loader()
    
    while True:
        loader.posts_load()
        time.sleep(1)
    
def start_member_parser():
    print('Member Parser Started!')
    
    loader = Loader()
    
    while True:
        loader.update_chat_members_count()
        time.sleep(10)
        
if __name__ == '__main__':
    bot_thread = Thread(target=start_bot)
    loader_thread = Thread(target=start_post_loader)
    member_parser_thread = Thread(target=start_member_parser)

    threads = [bot_thread, loader_thread, member_parser_thread]

    for t in threads:
        t.start()
    for t in threads:
        t.join()