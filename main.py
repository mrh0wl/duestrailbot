# /usr/bin/python3

# imports from default libs
from os import environ

# imports from pyrogram
from pyrogram import Client

# imports from src
from src.commands import Commands

if __name__ == '__main__':
    api_id = environ.get('API_ID')
    api_hash = environ.get('API_HASH')
    bot_token = environ.get('BOT_TOKEN')
    string_session = environ.get('STRING_SESSION')

    app = Client(
        string_session,
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token
    )
    Commands(app)
