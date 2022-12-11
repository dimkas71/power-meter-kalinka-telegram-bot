import logging
from typing import List

from aiogram import types
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as md

import service
from exceptions import PowerBotException
from loader import dp
from markup import create_start_markup, BEGIN_TEXT
from messages import help_info_message
from models import CounterInfo
from utils import parse


@dp.message_handler(commands="start")
async def start_cmd(msg: types.Message):
    await default_msg_handler(msg)


@dp.message_handler(Text(BEGIN_TEXT, ignore_case=True))
async def on_click_begin_text(msg: types.Message):
    await default_msg_handler(msg)


@dp.message_handler(regexp=":")
async def on_counter_value_add(msg: types.Message):
    reply_message = ""
    try:
        factory_number, value = parse(msg.text)
        counters_info: List[CounterInfo] = await service.search_by_number(factory_number)
        counters = list(filter(lambda counter_info: counter_info.counter_factory == factory_number, counters_info))
        if not counters:
            reply_message = md.text(f"Лічильник з номером {factory_number} не знайдено", "\n",
                                    "ПОВТОРІТЬ ЗАПИТ ІЗ ПРАВИЛЬНИМ НОМЕРОМ")
            raise PowerBotException(reply_message)
        if int(counters[0].current_value) > value:
            reply_message = md.text(
                md.bold("ПОМИЛКА"),
                md.text(f"Поточні показники лічильника {counters[0].current_value} > {value} більші за введені",
                        "\n"),
                md.bold("Дані по лічильнику не додано. Повторіть спробу."),
                "\n")

            raise PowerBotException(reply_message)
        try:
            await service.add_counter_value(counters[0].counter_uuid, value)
            reply_message = md.bold("ПОКАЗНИКИ ЛІЧИЛЬНИКА ДОДАНО УСПІШНО")
        except PowerBotException as ex:
            raise PowerBotException(md.bold("ПОМИЛКА ПРИ ДОДАВАННІ ПОКАЗНИКІВ.ПОВТОРІТЬ ЗАПИТ"))

    except ValueError as er:
        reply_message = md.text("Показники лічильника повинні бути числом. Повторіть операцію знову")
    except PowerBotException as er:
        reply_message = er.args[0]
    await msg.answer(reply_message, reply_markup=create_start_markup())


@dp.message_handler()
async def default_msg_handler(msg: types.Message):
    await msg.answer(help_info_message(), reply_markup=create_start_markup())
