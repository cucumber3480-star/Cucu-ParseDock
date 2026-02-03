from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Person:
    rank: str
    rank_category: str
    last_name: str
    first_name: str
    patronymic: Optional[str]

@dataclass
class Movement:
    unit_from: Optional[str]
    unit_to: Optional[str]
    destination: Optional[str]
    destination_detail: Optional[str]

@dataclass
class ArrivalDetails:
    arrival_type: str

@dataclass
class Position:
    position_to: Optional[str]
    temporary: Optional[bool]

@dataclass
class Classification:
    reason: Optional[str]
    excluded_state: Optional[str]

@dataclass
class Legal:
    basis: str
    order_number: str
    order_date: date

@dataclass
class ParsedEvent:
    event_type: str
    status: str
    date: date
    person: Person
    movement: Movement
    arrival_details: Optional[ArrivalDetails]
    position: Position
    classification: Classification
    legal: Legal
    raw_text: str
