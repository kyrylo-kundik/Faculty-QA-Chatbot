from aiogram import types
from aiogram.utils import executor

from settings import setup_bot

bot, dispatcher = setup_bot()


@dispatcher.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when client send `/start` or `/help` commands.
    """
    await bot.send_message(message.chat.id, "Add me to the Buddy group!!\nThat's all that I want!")


@dispatcher.message_handler(commands=['help'])
async def send_help(message: types.Message):
    text = """
Hi! I can *tag* members from this _Buddy_ group. _For example_: enter "@fi" and *I will tag all fishniks from this group!*
\n*More examples:*\n@all or @here will tag all members\n@fi or @fssst will tag only members from this faculties
@ipz @pravo @ecology will tag all people from this specializations
\nFor the full list commands type /helpm
    """
    await bot.send_message(message.chat.id, text, parse_mode='Markdown')


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=False)
