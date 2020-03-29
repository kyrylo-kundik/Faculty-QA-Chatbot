import asyncio

from aiogram import Bot


async def bot_typing(bot: Bot, chat_id: int, delay: float = 2.0):
    await bot.send_chat_action(chat_id, "typing")

    await asyncio.sleep(delay, loop=bot.loop)
