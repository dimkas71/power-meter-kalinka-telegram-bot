import aiogram.utils.markdown as md
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.callback_data import CallbackData

from typing import List, Tuple

from models import CounterInfo

counter_callback_data = CallbackData('counter', 'uuid')
delete_counter_callback_data = CallbackData('delete-counter', 'uuid')

def create_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    add_power_meter_value_btn = types.KeyboardButton("Додати показник лічильника")
    add_power_meter_btn = types.KeyboardButton("Додати лічильник")
    add_power_meter_by_contract_btn = types.KeyboardButton('Додати лічильник по договору')
    delete_power_meter_btn = types.KeyboardButton("Видалити лічильник")
    help_btn = types.KeyboardButton("Допомога")

    markup.add(*[add_power_meter_value_btn, add_power_meter_btn, add_power_meter_by_contract_btn, delete_power_meter_btn, help_btn])

    return markup

def create_help_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    main_menu_btn = types.KeyboardButton('Головне меню')
    markup.add(main_menu_btn)

    return markup

def create_add_power_meter_value_markup(counter_infos: List[Tuple[str, str, str, str]]):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for ci in counter_infos:
        btn = types.KeyboardButton(text=f"Рр: {ci[2]}:{ci[0]}:{ci[1]}")
        markup.add(btn)
    markup.add(types.KeyboardButton('Головне меню'))
    return markup

def create_add_power_meter_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    main_menu_btn = types.KeyboardButton("Головне меню")
    markup.add(main_menu_btn)

    return markup
   

def create_inline_counter_markup(counter_infos: List[CounterInfo]):
    ikm = InlineKeyboardMarkup()
    for ci in counter_infos:
        ikm.add(
            InlineKeyboardButton(
                text = f"{ci.contract_number} {ci.counter_factory} {ci.owner_name}",
                callback_data=counter_callback_data.new(uuid=ci.counter_uuid)
            )
        )
    return ikm

def delete_power_meter_markup(counter_infos: List[Tuple[str, str, str, str]]):
    ikm = InlineKeyboardMarkup()
    for ci in counter_infos:
        ikm.add(
            InlineKeyboardButton(
                text=f"{ci[2]} {ci[0]} {ci[1]}",
                callback_data=delete_counter_callback_data.new(uuid=ci[3])
            )
        )    
    return ikm