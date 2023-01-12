# imports from pyrogram lib
from pyrogram import Client, filters, idle
from pyrogram.handlers import (CallbackQueryHandler, InlineQueryHandler,
                               MessageHandler)

from .callback_query import Callback
# imports from src
from .info_commands import creator, start
from .inline_search import inline


async def disconnect(client):
    print('Hello')


class Commands(Client):
    def __init__(self, app: Client):
        super().__init__(
            session_string=app.session_string,
            api_id=app.api_id,
            api_hash=app.api_hash,
            bot_token=app.bot_token,
            workdir=app.workdir,
            plugins=app.plugins,
            name=app.name,
        )
        self.app = app

        self.add_handler(
            MessageHandler(
                start,
                (filters.command(['help', 'start']) & filters.private)
            )
        )
        self.add_handler(
            MessageHandler(
                creator,
                (filters.command(['creator']) & filters.private)
            )
        )
        self.add_handler(
            InlineQueryHandler(
                inline
            )
        )
        self.add_handler(
            CallbackQueryHandler(
                Callback
            )
        )
        self.add_handler(
            MessageHandler(
                Callback,
                (filters.inline_keyboard & filters.private)
            )
        )

        self.start()
        idle()
        self.stop()
