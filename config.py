import os

BOT_API_TOKEN = os.environ.get('BOT_API_TOKEN')

bot_api_url = f"https://api.telegram.org/bot{BOT_API_TOKEN}"
bot_file_api_url = f"https://api.telegram.org/file/bot{BOT_API_TOKEN}"