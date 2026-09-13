"""Station state messages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from deebot_client.events.station import State, StationErrorEvent, StationEvent
from deebot_client.message import HandlingResult, MessageBodyDataDict

if TYPE_CHECKING:
    from deebot_client.event_bus import EventBus


def _parse_error_codes(value: Any) -> tuple[int, ...] | None:
    """Return the station error codes, or None when the field is not a list.

    None means "the device did not report the error channel", which must not be
    confused with an empty list ("no current errors").
    """
    if not isinstance(value, list):
        return None
    codes: list[int] = []
    for entry in value:
        if isinstance(entry, bool):
            continue
        if isinstance(entry, int):
            codes.append(entry)
        elif isinstance(entry, str):
            try:
                codes.append(int(entry))
            except ValueError:
                continue
    return tuple(codes)


class OnStationState(MessageBodyDataDict):
    """On station state message."""

    NAME = "onStationState"

    @classmethod
    def _handle_body_data_dict(
        cls, event_bus: EventBus, data: dict[str, Any]
    ) -> HandlingResult:
        """Handle message->body->data and notify the correct event subscribers.

        :return: A message response
        """
        content = data.get("content")
        content = content if isinstance(content, dict) else {}
        state = data.get("state")

        if state == 0:
            reported_state = State.IDLE
        elif (
            state == 1 and content.get("type") == 1 and content.get("motionState") == 1
        ):
            reported_state = State.EMPTYING_DUSTBIN
        elif (
            state == 1 and content.get("type") == 2 and content.get("motionState") == 1
        ):
            reported_state = State.DRYING_MOP
        else:
            # Unrecognised frame: do not touch the latched error state.
            return HandlingResult.analyse()

        errors = _parse_error_codes(content.get("error"))
        if errors is not None:
            event_bus.notify(StationErrorEvent(errors))

        event_bus.notify(StationEvent(reported_state))
        return HandlingResult.success()
