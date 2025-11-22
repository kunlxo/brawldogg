from datetime import datetime

from pydantic import BaseModel, Field

from ..utils.validators import time_validator
from .constants import GAME_MODE


class GameMode(BaseModel):
    id: int
    name: str


class Event(BaseModel):
    id: int
    mode_id: int = Field(alias="modeId")
    mode: GAME_MODE | None = None  # missing when playing community maps
    map: None | str = None  # missing when playing community maps


class EventEntry(BaseModel):
    event: Event = Field(alias="event")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    slot_id: int = Field(alias="slotId")

    _validate_time = time_validator
