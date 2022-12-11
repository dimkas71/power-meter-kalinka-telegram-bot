from dataclasses import dataclass
from datetime import date
from uuid import UUID

from dataclasses_json import dataclass_json, Undefined


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


