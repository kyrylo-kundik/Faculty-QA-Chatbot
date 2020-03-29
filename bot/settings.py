import logging

from aiogram import Bot, Dispatcher


def setup_bot(token: str) -> (Bot, Dispatcher):
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize bot and dispatcher
    bot = Bot(token=token)
    dp = Dispatcher(bot)

    return bot, dp
