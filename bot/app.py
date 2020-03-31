import asyncio
import logging
import os
import random
import traceback

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData

from api.api_client import ApiClient, ApiClientError
from api.models import Answer, User
from phrases.phrase_handler import PhraseHandler
from phrases.phrase_types import PhraseTypes
from settings import setup_bot
from utils import bot_typing

bot, dispatcher = setup_bot(os.getenv("API_TOKEN"))

phrase_handler = PhraseHandler()
api_client = ApiClient(
    api_url=f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}",
    loop=bot.loop
)

predictors = bot.loop.run_until_complete(api_client.get_all_predictors())

answer_cb = CallbackData('answer_callback', 'id', 'rating', 'predictor')


@dispatcher.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await bot_typing(bot, message.chat.id)

    await bot.send_message(
        message.chat.id,
        phrase_handler.get_phrase(PhraseTypes.WELCOME_PHRASE),
        parse_mode="Markdown"
    )

    await bot_typing(bot, message.chat.id, 3.0)

    phrase = phrase_handler.get_phrase(
        PhraseTypes.ASK_QUESTION_PHRASE
    ) if message.chat.id == message.from_user.id else phrase_handler.get_phrase(
        PhraseTypes.ASK_QUESTION_IN_GROUP_PHRASE
    )

    await bot.send_message(
        message.chat.id,
        phrase,
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

    await bot_typing(bot, message.chat.id, 3.0)

    phrase = phrase_handler.get_phrase(
        PhraseTypes.ASK_QUESTION_PHRASE
    ) if message.chat.id == message.from_user.id else phrase_handler.get_phrase(
        PhraseTypes.ASK_QUESTION_IN_GROUP_PHRASE
    )

    await bot.send_message(
        message.chat.id,
        phrase,
        parse_mode="Markdown"
    )


@dispatcher.message_handler(regexp="@FIChatbot", content_types=types.ContentTypes.TEXT)
async def in_group_question(message: types.Message):
    message.text = message.text.replace("@FIChatbot", "").strip()
    await process_question(message)


@dispatcher.message_handler(content_types=types.ContentTypes.TEXT)
async def user_question(message: types.Message):
    if message.chat.id != message.from_user.id:
        return

    await process_question(message)


@dispatcher.callback_query_handler(lambda callback: callback.data.startswith("ask_exp"))
async def process_callback_button1(query: types.CallbackQuery):
    await bot.edit_message_text(
        text=f"{query.message.text}\n\n_Експерти вже розбирають Ваше питання!_",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
        parse_mode="Markdown"
    )
    msg: types.Message = await bot.send_message(os.getenv("SUPPORT_CHAT_ID"), query.data.replace("ask_exp_", ""))


@dispatcher.callback_query_handler()
async def rate_answer(query: types.CallbackQuery):
    callback_data = answer_cb.parse(query.data)

    msg_id = query.message.message_id
    user_id = query.from_user.id
    answer_id = int(callback_data["id"])
    rating = int(callback_data["rating"])
    predictor = callback_data["predictor"]

    logging.info(
        f"user: {user_id} mark question msg_id: {msg_id} "
        f"from predictor: {predictor} with rate: {rating}"
    )

    try:
        await api_client.update_answer(Answer(
            id_=answer_id,
            predictor=predictor,
            rating=rating,
            msg_id=msg_id
        ))

    except ApiClientError:
        logging.error("Got error from api_client.update_answer. See the full trace in console.")
        traceback.print_exc()

    text = query.message.text.replace(predictor.replace('\\_', '_'), predictor)
    await bot.edit_message_text(
        text=f"{text}\n\n*ДЯКУЮ ЗА ТЕ, ЩО РОБИШ МЕНЕ КРАЩЕ!*",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
        parse_mode="Markdown"
    )


async def process_question(message: types.Message):
    logging.info(f"adding user: {message.from_user.id}")
    try:
        await api_client.add_user(User(
            tg_id=message.from_user.id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        ))
    except ApiClientError:
        logging.error("Got error from api_client.add_user. See the full trace in console.")
        traceback.print_exc()

    question: str = message.text
    logging.info(f"Processing question from user ({message.from_user.first_name}): {question}")

    await bot_typing(bot, message.chat.id, 1.0)

    await bot.send_message(
        message.chat.id,
        phrase_handler.get_phrase(PhraseTypes.PLEASE_WAIT_PHRASE),
        parse_mode="Markdown",
    )

    await bot_typing(bot, message.chat.id)  # bot will have "typing" status until first search done

    tasks = [
        api_client.publish_question(
            message.text,
            predictor,
            message.from_user.id,
            message.message_id,
            message.chat.id
        ) for predictor in predictors
    ]

    for task in asyncio.as_completed(tasks, loop=bot.loop):
        try:
            answer: Answer = await task

        except ApiClientError:
            logging.error("Got error from api_client.search. See the full trace in console.")
            traceback.print_exc()

            continue

        if answer is None:
            continue

        answer.predictor = answer.predictor.replace('_', '\\_')  # due to markdown parse errors

        await bot.send_message(
            message.chat.id,
            f"{answer.predictor} said:\n\n{answer.text}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(row_width=5).add(
                InlineKeyboardButton(
                    "⭐️1", callback_data=answer_cb.new(id=answer.id_, rating=1, predictor=answer.predictor)
                ),
                InlineKeyboardButton(
                    "⭐️2", callback_data=answer_cb.new(id=answer.id_, rating=2, predictor=answer.predictor)
                ),
                InlineKeyboardButton(
                    "⭐️3", callback_data=answer_cb.new(id=answer.id_, rating=3, predictor=answer.predictor)
                ),
                InlineKeyboardButton(
                    "⭐️4", callback_data=answer_cb.new(id=answer.id_, rating=4, predictor=answer.predictor)
                ),
                InlineKeyboardButton(
                    "⭐️5", callback_data=answer_cb.new(id=answer.id_, rating=5, predictor=answer.predictor)
                )
            )
        )

        await bot_typing(bot, message.chat.id, float(random.randint(2, 4)))  # set typing status until next search done

    await bot_typing(bot, message.chat.id)

    await bot.send_message(
        message.chat.id,
        phrase_handler.get_phrase(PhraseTypes.PLEASE_RANK_PHRASE),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Запитати у експертів?", callback_data=f"ask_exp_{message.text}")
        )
    )


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
