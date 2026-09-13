from __future__ import annotations

from typing import Any

import pytest

from deebot_client.events import FirmwareEvent
from deebot_client.events.station import State, StationErrorEvent, StationEvent
from deebot_client.message import HandlingState
from deebot_client.messages.json.station_state import OnStationState
from tests.messages.json import assert_message


@pytest.mark.parametrize(
    ("state", "additional_content", "expected"),
    [
        (0, {"type": 0}, State.IDLE),
        (1, {"type": 1, "motionState": 1}, State.EMPTYING_DUSTBIN),
        (1, {"type": 2, "motionState": 1}, State.DRYING_MOP),
    ],
)
@pytest.mark.benchmark
def test_onStationState(
    state: int,
    additional_content: dict[str, Any],
    expected: State,
) -> None:
    data: dict[str, Any] = {
        "header": {
            "pri": 1,
            "tzm": 60,
            "ts": "1734719921057",
            "ver": "0.0.1",
            "fwVer": "1.30.0",
            "hwVer": "0.1.1",
            "wkVer": "0.1.54",
        },
        "body": {
            "data": {"content": {"error": [], **additional_content}, "state": state},
            "code": 0,
            "msg": "ok",
        },
    }

    assert_message(
        OnStationState,
        data,
        (FirmwareEvent("1.30.0"), StationErrorEvent(()), StationEvent(expected)),
    )


@pytest.mark.parametrize(
    ("state", "additional_content"),
    [
        # content missing
        (1, {}),
        # type present but motionState missing
        (1, {"type": 2}),
        # type matches but motionState different
        (1, {"type": 2, "motionState": 0}),
        # unexpected state value
        (2, {"type": 2, "motionState": 1}),
    ],
)
@pytest.mark.benchmark
def test_onStationState_analyse(state: int, additional_content: dict[str, Any]) -> None:
    """Cases that should fall through to analyse() (not handled)."""
    data: dict[str, Any] = {
        "header": {
            "pri": 1,
            "tzm": 60,
            "ts": "1734719921057",
            "ver": "0.0.1",
            "fwVer": "1.30.0",
            "hwVer": "0.1.1",
            "wkVer": "0.1.54",
        },
        "body": {
            "data": {"content": {"error": [], **additional_content}, "state": state},
            "code": 0,
            "msg": "ok",
        },
    }

    assert_message(
        OnStationState,
        data,
        (FirmwareEvent("1.30.0"),),
        expected_state=HandlingState.ANALYSE_LOGGED,
    )


def _payload(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "header": {
            "pri": 1,
            "tzm": 60,
            "ts": "1734719921057",
            "ver": "0.0.1",
            "fwVer": "1.30.0",
            "hwVer": "0.1.1",
            "wkVer": "0.1.54",
        },
        "body": {"data": data, "code": 0, "msg": "ok"},
    }


@pytest.mark.benchmark
def test_onStationState_error_not_a_list() -> None:
    """A non-list error field means 'unknown', not 'no errors'."""
    data = _payload({"content": {"error": "301", "type": 0}, "state": 0})
    assert_message(
        OnStationState,
        data,
        (FirmwareEvent("1.30.0"), StationEvent(State.IDLE)),
    )


@pytest.mark.benchmark
def test_onStationState_string_error_codes() -> None:
    """Error codes sent as strings are coerced to ints."""
    data = _payload({"content": {"error": ["301", "302"], "type": 0}, "state": 0})
    assert_message(
        OnStationState,
        data,
        (
            FirmwareEvent("1.30.0"),
            StationErrorEvent((301, 302)),
            StationEvent(State.IDLE),
        ),
    )


@pytest.mark.benchmark
def test_onStationState_analyse_does_not_clear_errors() -> None:
    """An unrecognised frame must not emit the all-clear error event."""
    data = _payload(
        {"content": {"error": [301], "type": 99, "motionState": 1}, "state": 1}
    )
    assert_message(
        OnStationState,
        data,
        (FirmwareEvent("1.30.0"),),
        expected_state=HandlingState.ANALYSE_LOGGED,
    )


@pytest.mark.benchmark
def test_onStationState_without_content() -> None:
    """A frame without a content/error channel must not assert 'no errors'."""
    data: dict[str, Any] = {
        "header": {
            "pri": 1,
            "tzm": 60,
            "ts": "1734719921057",
            "ver": "0.0.1",
            "fwVer": "1.30.0",
            "hwVer": "0.1.1",
            "wkVer": "0.1.54",
        },
        "body": {"data": {"state": 0}, "code": 0, "msg": "ok"},
    }

    assert_message(
        OnStationState,
        data,
        (FirmwareEvent("1.30.0"), StationEvent(State.IDLE)),
    )


@pytest.mark.parametrize("errors", [[301], [301, 314], [305, 318, 323]])
@pytest.mark.benchmark
def test_onStationState_errors(errors: list[int]) -> None:
    """Station error codes are surfaced even when the state is known."""
    data: dict[str, Any] = {
        "header": {
            "pri": 1,
            "tzm": 60,
            "ts": "1734719921057",
            "ver": "0.0.1",
            "fwVer": "1.30.0",
            "hwVer": "0.1.1",
            "wkVer": "0.1.54",
        },
        "body": {
            "data": {"content": {"error": errors, "type": 0}, "state": 0},
            "code": 0,
            "msg": "ok",
        },
    }

    assert_message(
        OnStationState,
        data,
        (
            FirmwareEvent("1.30.0"),
            StationErrorEvent(tuple(errors)),
            StationEvent(State.IDLE),
        ),
    )
