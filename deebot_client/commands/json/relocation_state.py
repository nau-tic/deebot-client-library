"""Relocation state command module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from deebot_client.events.status import RelocationStateEvent
from deebot_client.message import HandlingResult

from .common import JsonGetCommand

if TYPE_CHECKING:
    from deebot_client.event_bus import EventBus


class GetRelocationState(JsonGetCommand):
    """Get relocation state command."""

    NAME = "getRelocationState"

    @classmethod
    def _handle_body_data_dict(
        cls, event_bus: EventBus, data: dict[str, Any]
    ) -> HandlingResult:
        """Handle message->body->data and notify the correct event subscribers.

        :return: A message response
        """
        event_bus.notify(
            RelocationStateEvent(
                is_has_map=bool(data.get("isHasMap", 0)),
                mode=str(data.get("mode", "")),
                state=str(data.get("state", "")),
            )
        )
        return HandlingResult.success()
