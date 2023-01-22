from typing import List
from config import bot_api_url, bot_file_api_url

import requests

class MediaGroup:
    def __init__(self) -> None:
        self.files: List[str] = []
    
    def add_media(self, file_id: str) -> None:
        self.files.append(file_id)
    
    def get_urls(self) -> List[str]:
        return [self.get_url(file_id) for file_id in self.files]
    
    def get_url(self, file_id: str) -> str:
        file_data = requests.get(f"{bot_api_url}/getFile?file_id={file_id}").json()
        file_path = file_data['result']['file_path']
        return f"{bot_file_api_url}/{file_path}"
