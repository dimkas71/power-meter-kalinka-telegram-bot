from uuid import UUID
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined
from datetime import date 
from typing import List, Optional 
import json


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(frozen=True)
class CounterInfo:
    counter_uuid: UUID
    counter_factory: str
    owner_name: str
    owner_uuid: UUID
    contract_uuid: UUID
    contract_number: str
    current_value: str 


@dataclass_json
@dataclass(frozen=True)
class HistoryCounterValue:
    value: int
    date: date


@dataclass_json
@dataclass(frozen=True)
class CounterValue:
    uuid: UUID
    value: int

@dataclass_json
@dataclass(frozen=True)
class User:
    id: str
    name: str


