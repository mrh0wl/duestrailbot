# imports from pyrogram
from pyrogram import Client
from pyrogram.types import Message

# imports from src
from src.utils.docs import Docs, InfoMode


async def start(client: Client, message: Message) -> None:
    m, ik = Docs(message, 'text_messages').get_inline_with_message(
        mode=InfoMode.START)
    await message.reply_text(m, reply_markup=ik)


async def creator(client: Client, message: Message) -> None:
    m, ik = Docs(message, 'text_messages').get_inline_with_message(
        mode=InfoMode.CREATOR)
    await message.reply_text(m, reply_markup=ik)
