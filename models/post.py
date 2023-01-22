from datetime import datetime
from pyairtable import Table
from models.media_group import MediaGroup
from pyairtable.utils import attachment
from models.user import User
from utils import sanitise_text

import re
import os

AIRTABLE_API_TOKEN = os.environ.get('AIRTABLE_API_TOKEN')
AIRTABLE_APP_ID = os.environ.get('AIRTABLE_APP_ID')
AIRTABLE_POSTS_TABLE_ID = os.environ.get('AIRTABLE_POSTS_TABLE_ID')

class Post():
    airtable_table = Table(AIRTABLE_API_TOKEN, AIRTABLE_APP_ID, AIRTABLE_POSTS_TABLE_ID)

    def __init__(self, id: int, chat_id: int, chat_airtable_record_id: str, text: str, creator: User, media_group_id: str) -> None:
        text = sanitise_text(text)
        self.id = id
        self.chat_id = chat_id
        self.chat_airtable_record_id = chat_airtable_record_id
        self.text = text
        self.creator = creator
        self.media_group_id = media_group_id
        self.media_group = None
        self.created_at = datetime.now()
        self.email = self.get_email_from_text(text)
        self.phone = self.get_phone_from_text(text)
    
    def get_email_from_text(self, text: str) -> str:
        match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        return match[0] if len(match) > 0 else None
    
    def get_phone_from_text(self, text: str) -> str:
        match = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
        return match[0] if len(match) > 0 else None

    def load_media_group(self, media_group: MediaGroup) -> None:
        self.media_group = media_group

    def get_airtable_record_fields(self):
        user_record = self.creator.get_airtable_record()
        
        airtable_record_fields = {
            'PostID': self.id,
            'Text': self.text,
            'User': [user_record['id']],
            'City': [self.chat_airtable_record_id],
            'Email': self.email,
            'Phone': self.phone,
            'tgusername': self.creator.username,
            'tgusername link': ('https://t.me/' + self.creator.username) if self.creator.username else None
        }

        if self.media_group:
            media_group_urls = [attachment(url) for url in self.media_group.get_urls()]
            airtable_record_fields['Attachment'] = media_group_urls
        
        return airtable_record_fields
    
    def save_to_airtable(self):
        airtable_record_fields = self.get_airtable_record_fields()
        self.airtable_table.create(airtable_record_fields)