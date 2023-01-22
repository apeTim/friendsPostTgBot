from typing import List, Dict
from models.post import Post
from random import randint
from models.media_group import MediaGroup
from aiogram.types import Message
from pyairtable import Table
from models.user import User
import requests
from config import bot_api_url
 
from datetime import datetime
import os
import traceback

AIRTABLE_API_TOKEN = os.environ.get('AIRTABLE_API_TOKEN')
AIRTABLE_APP_ID = os.environ.get('AIRTABLE_APP_ID')
AIRTABLE_CITIES_TABLE_ID = os.environ.get('AIRTABLE_CITIES_TABLE_ID')

class Loader:
    LOAD_WAIT_PERIOD = 5
    MIN_TEXT_LEN = 15

    # telegram id -> airtable record id
    cities_id: Dict[int, str] = {}
    posts: List[Post] = []
    media_groups: Dict[str, MediaGroup] = {}

    cities_table = Table(AIRTABLE_API_TOKEN, AIRTABLE_APP_ID, AIRTABLE_CITIES_TABLE_ID)

    def __init__(self) -> None:
        for row in self.cities_table.all():
            try:
                city_id = row['fields']['IDtg']
                self.cities_id[city_id] = row['id']
            except:
                continue

    async def post_create(self, message: Message) -> None:
        chat_id = message.chat.id
        user = message.from_user
        id = message.message_id
        text = message.text or message.caption or ''
        creator = User(user.id, user.username, user.first_name, user.last_name)
        media_group_id = message.media_group_id
        
        if chat_id not in self.cities_id:
            return
        if len(text) <= self.MIN_TEXT_LEN:
            return

        post = Post(id, chat_id, self.cities_id[chat_id], text, creator, media_group_id)

        self.posts.append(post)
    
    async def post_create_with_photo(self, message: Message) -> None:
        media_group_id = 'c' + str(randint(10 ** 17, 10 ** 18))
        message.media_group_id = media_group_id

        file_id = message.photo[-1].file_id

        self.media_group_create(media_group_id)
        await self.post_create(message)

        self.media_groups[media_group_id].add_media(file_id)

    async def post_create_with_media_group(self, message: Message) -> None:
        media_group_id = message.media_group_id
        file_id = message.photo[-1].file_id

        if media_group_id not in self.media_groups:
            self.media_group_create(media_group_id)
            await self.post_create(message)

        self.media_groups[media_group_id].add_media(file_id)

    def media_group_create(self, media_group_id: str) -> None:
        self.media_groups[media_group_id] = MediaGroup()
    
    def posts_load(self) -> None:
        for post in self.posts:
            if (datetime.now() - post.created_at).total_seconds() < self.LOAD_WAIT_PERIOD:
                continue

            self.post_load(post)
            self.posts.remove(post)

    def post_load(self, post: Post) -> None:
        try:
            if not post.creator.username:
                return

            if post.media_group_id:
                media_group = self.media_groups.pop(post.media_group_id)
                post.load_media_group(media_group)
            
            post.save_to_airtable()
        except Exception as e:
            traceback.print_exc()
    
    def update_chat_members_count(self) -> None:
        for city in self.cities_id:
            record_id = self.cities_id[city]
            response = requests.get(f"{bot_api_url}/getChatMemberCount?chat_id={city}")
            
            if response.status_code != 200:
                continue
            
            members = response.json()['result']
            self.cities_table.update(record_id, { 'Auditorium': members })
