"""Base station event module."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, unique

from .base import Event as _Event

__all__ = ["State", "StationErrorEvent", "StationEvent", "StationInfoEvent"]


@unique
class State(IntEnum):
    """Enum class for all possible base station statuses."""

    IDLE = 0
    EMPTYING_DUSTBIN = 1
    WASHING_MOP = 2
    DRYING_MOP = 3


@dataclass(frozen=True)
class StationEvent(_Event):
    """Base Station Event representation."""

    state: State


@dataclass(frozen=True)
class StationErrorEvent(_Event):
    """Errors reported by the base station, e.g. a water-tank condition.

    Empty means no current station errors. Codes are Ecovacs error codes (see
    ``deebot_client.const.ERROR_CODES``), e.g. 301 "FreshWaterBox empty".
    """

    errors: tuple[int, ...]


@dataclass(frozen=True)
class StationInfoEvent(_Event):
    """Base station identity and firmware."""

    name: str
    model: str
    firmware: str
