import logging
import os

from aiogram import Bot, Dispatcher


def setup_bot() -> (Bot, Dispatcher):
    token = os.getenv("API_TOKEN")

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize bot and dispatcher
    bot = Bot(token=token)
    dp = Dispatcher(bot)

    return bot, dp
