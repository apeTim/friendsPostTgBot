from config import bot_api_url
from pyairtable.formulas import match
from pyairtable.utils import attachment
from pyairtable import Table
from models.media_group import MediaGroup
from utils import sanitise_text

import os
import requests

AIRTABLE_API_TOKEN = os.environ.get('AIRTABLE_API_TOKEN')
AIRTABLE_APP_ID = os.environ.get('AIRTABLE_APP_ID')
AIRTABLE_USERS_TABLE_ID = os.environ.get('AIRTABLE_USERS_TABLE_ID')

class User:
    airtable_table = Table(AIRTABLE_API_TOKEN, AIRTABLE_APP_ID, AIRTABLE_USERS_TABLE_ID)
    
    def __init__(self, id: int, username: str, first_name: str, last_name: str) -> None:
        self.id = id
        self.username = username
        self.first_name = sanitise_text(first_name)
        self.last_name = sanitise_text(last_name)
        
    def get_airtable_record_fields(self):
        airtable_record_fields = {
            'IDtg': self.id,
            'Name': self.first_name,
            'Surname': self.last_name,
            'tgusername': self.username,
            'tgusername link': ('https://t.me/' + self.username) if self.username else None
        }
        
        avatar = self.get_avatar()
        if avatar:
            airtable_record_fields['Avatar'] = [attachment(avatar)]
            
        bio = self.get_bio()
        if bio:
            airtable_record_fields['Bio'] = bio
        
        return airtable_record_fields
    
    def get_airtable_record(self):
        user_data = [self.first_name, self.last_name, self.username]
        formula = match({ 'IDtg': self.id })
        airtable_record = self.airtable_table.first(formula=formula)

        if airtable_record:
            user_record_data = [None if field not in airtable_record['fields'] else airtable_record['fields'][field] for field in ['Name', 'Surname', 'tgusername']]
            need_update = any([user_data[i] != user_record_data[i] for i in range(len(user_data))])

            if need_update:                    
                airtable_record_fields = self.get_airtable_record_fields()
                self.airtable_table.update(airtable_record['id'], airtable_record_fields)
        else:
            airtable_record_fields = self.get_airtable_record_fields()
            airtable_record = self.airtable_table.create(airtable_record_fields)
            
        return airtable_record

    
    def get_avatar(self):
        avatar = None
        response = requests.get(f"{bot_api_url}/getUserProfilePhotos?user_id={self.id}&offset=0&limit=1").json()
        
        if response["result"]["total_count"]:
            file_id = response["result"]["photos"][0][-1]["file_id"]
            avatar = MediaGroup().get_url(file_id)
        
        return avatar
    
    def get_bio(self):
        bio = None
        response = requests.get(f"{bot_api_url}/getChat?chat_id={self.id}").json()
        
        if "bio" in response["result"]:
            bio = response["result"]["bio"]
            
        return bio