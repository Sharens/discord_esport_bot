from dataclasses import dataclass
from typing import Optional


@dataclass
class Match:
    event_id: int
    event_name: str
    match_id: int
    match_name: str
    match_status: str
    match_slug: str
    match_type: str
    match_scheduled_at: str


@dataclass
class Player:
    id: int
    name: str
    active: bool
    role: Optional[str]
    slug: str
    modified_at: str
    age: Optional[int]
    birthday: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    nationality: Optional[str]

