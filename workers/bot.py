from aiogram import Bot as BotInstance, Dispatcher, executor
from aiogram.types import Message
from workers.loader import Loader

class Bot:
    prev_notification_reply: Message = None
    
    def __init__(self, token: str) -> None:
        self.instance = BotInstance(token)
        self.dispatcher = Dispatcher(self.instance)
        self.loader = Loader()
        
    def start_polling(self) -> None:
        executor.start_polling(self.dispatcher)
    
    async def text_message_handler(self, message: Message) -> None:
        await self.check_username(message)
        await self.loader.post_create(message)
    
    async def photo_message_handler(self, message: Message) -> None:
        await self.check_username(message)
        await self.loader.post_create_with_photo(message)
    
    async def media_group_message_handler(self, message: Message) -> None:
        await self.check_username(message)
        await self.loader.post_create_with_media_group(message)
        
    async def check_username(self, message: Message) -> None:
        if not message.from_user.username:
            if self.prev_notification_reply:
                await self.prev_notification_reply.delete()
            reply = await message.reply(f'{message.from_user.full_name}, добавьте username, [подробнее](https://t.me/miamifriends/71513)', parse_mode='MarkdownV2', disable_web_page_preview=True)
            self.prev_notification_reply = reply
    