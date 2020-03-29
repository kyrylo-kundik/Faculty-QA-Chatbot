import os

from aiogram import types
from aiogram.utils import executor

from api_client import ApiClient
from phrase_handler import PhraseHandler
from phrase_types import PhraseTypes
from settings import setup_bot
from utils import bot_typing

bot, dispatcher = setup_bot(os.getenv("API_TOKEN"))

phrase_handler = PhraseHandler()
api_client = ApiClient(api_url=f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}")


@dispatcher.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await bot_typing(bot, message.chat.id, 2.0)

    await bot.send_message(
        message.chat.id,
        phrase_handler.get_phrase(PhraseTypes.WELCOME_PHRASE),
        parse_mode="Markdown"
    )


@dispatcher.message_handler(commands=["help"])
async def send_help(message: types.Message):
    await bot_typing(bot, message.chat.id)

    await bot.send_message(
        message.chat.id,
        phrase_handler.get_phrase(PhraseTypes.HELP_PHRASE),
        parse_mode="Markdown"
    )


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
