"""Break-point status command module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from deebot_client.events.status import BreakPointStatusEvent
from deebot_client.message import HandlingResult

from .common import JsonGetCommand

if TYPE_CHECKING:
    from deebot_client.event_bus import EventBus


class GetBreakPointStatus(JsonGetCommand):
    """Get break-point status command."""

    NAME = "getBreakPointStatus"

    @classmethod
    def _handle_body_data_dict(
        cls, event_bus: EventBus, data: dict[str, Any]
    ) -> HandlingResult:
        """Handle message->body->data and notify the correct event subscribers.

        :return: A message response
        """
        event_bus.notify(
            BreakPointStatusEvent(
                status=int(data.get("status", 0)),
                is_conflict=bool(data.get("isConflict", 0)),
                continue_left_time=int(data.get("continueLeftTime", 0)),
            )
        )
        return HandlingResult.success()
