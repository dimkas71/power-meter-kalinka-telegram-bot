import aiosqlite
import os
import logging

from typing import List, Tuple
from uuid import UUID

from exceptions import PowerBotException

async def add_counter_with_user(
                                user_id: str,
                                user_name: str,
                                counter_uuid: UUID,
                                counter_factory: str,
                                owner: str,
                                contract: str) -> None:
    async with aiosqlite.connect(os.environ.get('DB_NAME')) as conn:
        try:
            await conn.execute('insert into user values(?,?)', (user_id, user_name))
            await conn.commit()  
        except aiosqlite.IntegrityError as e:
            pass

        try:
            await conn.execute('insert into counter values(?, ?, ?, ?)', (str(counter_uuid), counter_factory, owner, contract))
            await conn.commit()
        except aiosqlite.IntegrityError as e:
            pass

        try:
            await conn.execute('insert into user_counter values(?, ?)', (str(counter_uuid), user_id))
            await conn.commit()
        except aiosqlite.IntegrityError as e:
            pass    

        row = await conn.execute('select * from user_counter where counter_uuid=:uuid and user_id=:id', {'uuid':str(counter_uuid), 'id':user_id})
        if not row: 
            raise PowerBotException(f"Помилка бази данних. Не вдалось записати дані по лічильнику {counter_factory} користувача {user_name}")  
            


async def get_counter_info_by_user(user_id: str) -> List[Tuple[str, str, str, str]]:
    async with aiosqlite.connect(os.environ.get('DB_NAME')) as conn:
        cur = await conn.execute("""
                    select factory, owner, contract, uuid from counter where uuid in (

                        select counter_uuid from user_counter where user_id = :id)
                    """, (user_id,)
                    )
        result = []
        if cur:
            rows = await cur.fetchall()
            for row in rows:
                result.append((row[0], row[1], row[2],row[3],))

        return result


async def get_counter_uuid(contract: str, factory: str, owner: str):
    async with aiosqlite.connect(os.environ.get('DB_NAME')) as conn:
        curr = await conn.execute("""
            select uuid as uuid from counter where contract = :contract and factory = :factory and owner = :owner
        """, (contract, factory, owner,))

        row = await curr.fetchone()
        if row:
            return UUID(row[0])
        else:
            return None    

async def delete_counter_by_uuid(uuid: str) -> None:
    async with aiosqlite.connect(os.environ.get('DB_NAME')) as conn:
        await conn.execute("""
            delete from user_counter where counter_uuid = :uuid
        """, (str(uuid), ))
        await conn.commit()

        row = await conn.execute('select * from user_counter where counter_uuid = :uuid', {'uuid':str(uuid)})
        if not row: 
            raise PowerBotException(f"Помилка бази данних. Не вдалось вилучити лічильник")  



