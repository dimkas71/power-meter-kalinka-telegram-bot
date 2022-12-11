import os
from typing import List
from uuid import UUID

from aiohttp import ClientSession, BasicAuth

from exceptions import PowerBotException
from models import CounterInfo, HistoryCounterValue


async def search_by_number(counter_number: str) -> List[CounterInfo]:

    async with ClientSession() as session:
        params = {'number': counter_number}
        async with session.get(f"{os.environ.get('API_BASE_URL')}/search",
                             auth=BasicAuth(os.environ.get('API_USER'), os.environ.get('API_PASSWORD')),
                             params=params) as response:
            if (response.status == 200):
                content = await response.text(encoding='utf-8-sig')
                return CounterInfo.schema().loads(content, many=True)
            else:
                return []                         
async def search_by_contract(contract: str) -> List[CounterInfo]:
    async with ClientSession() as session:
        async with session.get(f"{os.environ.get('API_BASE_URL')}/list",
                             auth=BasicAuth(os.environ.get('API_USER'), os.environ.get('API_PASSWORD'))) as response:
            if (response.status == 200):
                content = await response.text(encoding='utf-8-sig')
                infos:List[CounterInfo] = CounterInfo.schema().loads(content, many=True)
                return list(filter(lambda ci: ci.contract_number.startswith(contract), infos))
            else:
                return []     
async def last_counter_value(uuid: UUID):
    async with ClientSession() as session:
        params = {'uuid': str(uuid)}
        async with session.get(
                f"{os.environ.get('API_BASE_URL')}/history",
                auth=BasicAuth(os.environ.get('API_USER'), os.environ.get('API_PASSWORD')),
                params=params
            ) as response:
            if response.status == 200:
                content = await response.text(encoding='utf-8-sig')
                history_infos = HistoryCounterValue.schema().loads(content, many=True)
                if history_infos:
                    return history_infos[::-1][0].value
                else:
                    return None    
            else:
                return None    


async def add_counter_value(uuid: str, value: int) -> None:
    import json
    async with ClientSession() as session:
        data = {'uuid':str(uuid), 'value': value}
        async with session.post(
            f"{os.environ.get('API_BASE_URL')}/add",
            auth=BasicAuth(os.environ.get('API_USER'), os.environ.get('API_PASSWORD')),
            data=json.dumps(data)) as r:
            if r.status != 200:
                raise PowerBotException("Не вдалось записати дані. Повторіть ще раз або повторіть запит пізніше")
