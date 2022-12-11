import logging
from typing import List, Tuple
from uuid import UUID

import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

import db
import service
from exceptions import PowerBotException
from loader import dp
from markup import create_add_power_meter_markup, create_main_markup, create_inline_counter_markup, \
    create_add_power_meter_value_markup, \
    delete_power_meter_markup
from models import CounterInfo
from utils import enter_counter_info_message, enter_contract_info_message


#TODO: change the class name to more adequate
class FSM(StatesGroup):
    pmv_start = State()

class ForSearchByContractFSM(StatesGroup):
    start = State()    


@dp.message_handler(commands="start")
async def start_cmd(msg: types.Message):
    await msg.answer("Виберіть дію:", reply_markup=create_main_markup())

@dp.message_handler(Text("Головне меню", ignore_case=True), state="*")
async def main_menu_handler(msg: types.Message, state: FSMContext):
    #logging.warning("Main menu handled")
    if state:
        await state.finish()
    await msg.answer("Виберіть дію:", reply_markup=create_main_markup())

@dp.message_handler(regexp='^\d{7,}')
async def power_meter_number_handler(msg: types.Message, state: FSMContext):
    
    counter_infos: List[CounterInfo] = await service.search_by_number(msg.text)

    async with state.proxy() as data:
        data['counter_info'] = {ci.counter_uuid: (ci.owner_name, ci.counter_factory, ci.contract_number, ci.current_value) for ci in counter_infos}

    if counter_infos:
        await msg.answer("Виберіть лічильник", reply_markup=create_inline_counter_markup(counter_infos))
    else:

        await msg.answer(
            md.text(
                md.bold("Лічильник не знайдено"),
             enter_counter_info_message(), sep="\n")
        )


@dp.message_handler(Text('додати лічильник', ignore_case=True))
async def add_power_meter_handler(msg: types.Message):
    await msg.answer(enter_counter_info_message(),
     reply_markup=create_add_power_meter_markup())

@dp.message_handler(regexp="\d{1,}", state=ForSearchByContractFSM.start)
async def add_power_meter_by_contract_entered_handler(msg: types.Message, state: FSMContext):
    contract = msg.text.strip() 
    infos: List[CounterInfo] = await service.search_by_contract(contract)
    #logging.info(f"List: {infos}")
    async with state.proxy() as data:
        data['counter_info'] = {ci.counter_uuid: (ci.owner_name, ci.counter_factory, ci.contract_number, ci.current_value) for ci in infos}

    if infos:
        await msg.answer("Виберіть лічильник", reply_markup=create_inline_counter_markup(infos))
    else:

        await msg.answer(
            md.text(
                md.bold("Лічильник не знайдено"),
             enter_counter_info_message(), sep="\n")
        )
    #await state.finish()
    #await msg.answer(msg.text, reply_markup=create_add_power_meter_markup())

@dp.message_handler(Text('додати лічильник по договору', ignore_case=True))
async def add_power_meter_by_contract_handler(msg: types.Message):
    await ForSearchByContractFSM.start.set()
    await msg.answer(enter_contract_info_message(),
        reply_markup=create_add_power_meter_markup())

@dp.message_handler(Text('Видалити лічильник', ignore_case=True))
async def delete_power_meter_handler(msg: types.Message, state: FSMContext):
    user_id = msg.chat.id
    counter_infos: List[Tuple[str,str, str, str]] = await db.get_counter_info_by_user(user_id=user_id)
    async with state.proxy() as data:
        data['counter_infos'] = counter_infos
    await msg.answer("Виберіть лічильник для вилучення:",
            reply_markup=delete_power_meter_markup(counter_infos))     

@dp.message_handler(Text('додати показник лічильника', ignore_case=True))
async def add_power_meter_value_handler(msg: types.Message):
    user_id = msg.chat.id
    counter_infos = await db.get_counter_info_by_user(user_id)
    await msg.answer("Виберіть лічильник:", reply_markup=create_add_power_meter_value_markup(counter_infos))

@dp.callback_query_handler(text_contains='delete-counter')
async def delete_counter_chooser_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer(cache_time=60)
    uuid = query.data.split(":")[1]
    
    try:
        await db.delete_counter_by_uuid(uuid)
        await query.message.answer("лічильник вилучено успішно")
    except PowerBotException as e:
        await query.message.answer(e)
    
    await query.message.edit_reply_markup(reply_markup=None)

@dp.callback_query_handler(text_contains='counter', state="*")
async def counter_chooser_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer(cache_time=60)
    if state:
        async with state.proxy() as data:
            counter_uuid = UUID(query.data.split(":")[1])
            counter_info: Tuple(str, str, str, str) = data['counter_info'][counter_uuid]
            try:
                await db.add_counter_with_user(
                                                query.message.chat.id,
                                                query.message.chat.username,
                                                counter_uuid,
                                                counter_info[1],
                                                counter_info[0],
                                                counter_info[2]
                    )
                await query.message.answer("Ваш лічильник успішно додано в список")    
            except PowerBotException as e:
                await query.message.answer(f"{e}")
                await query.message.edit_reply_markup(reply_markup=None)
        
        await state.finish()
    await query.message.edit_reply_markup(reply_markup=None)

@dp.message_handler(regexp="\d{1,}", state=FSM.pmv_start)
async def add_power_meter_value_handler(msg: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        if data:
            prev_value = data['ci']['value'] or 0
            curr_value = int(msg.text)
            uuid = data['ci']['uuid']
            logging.info(f"UUID: {uuid}, with value: {curr_value}")
            if curr_value < prev_value: 
                await msg.answer("Поточне значення показчика менш ніж попереднє.\n Введіть показник лічильника:")
            else:
                try:
                    await service.add_counter_value(uuid, curr_value)
                    await msg.answer("Поточне значення показника записано успішно!!!")
                except PowerBotException as e:
                    await msg.answer(e)

                await state.finish()

        else:
            await state.finish()    


@dp.message_handler(text_contains="Рр:")
async def add_power_meter_value_start_handler(msg: types.Message, state: FSMContext):
    
    _, contract, factory, owner = msg.text.split(":")

    uuid = await db.get_counter_uuid(contract.strip(), factory.strip(), owner.strip())
    if uuid:
        current_value: int  = await service.last_counter_value(uuid) or 0

        if current_value:
            await FSM.pmv_start.set()

            async with state.proxy() as data:
                data['ci'] = {'uuid':uuid, 'value': current_value}
            await msg.answer(
                md.text("Попередній показник:", md.bold(current_value), "\n",
                "Введіть поточний показник:", sep = ' ')
            )    
        else:
            #TODO: Message should be with hint. XXXX as format data
            await msg.answer(f"Лічильник не знайдено. Спробуйте додати лічильник у базу")    
    else:
        await msg.answer('Не знайшли лічильника в базі даних. Спробуйте додати лічильник у базу.')    
   

@dp.message_handler()
async def default_msg_handler(msg: types.Message):
    await msg.answer(msg.text)
