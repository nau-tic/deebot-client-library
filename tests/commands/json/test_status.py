from __future__ import annotations

from typing import Any

import pytest

from deebot_client.commands.json import (
    GetBreakPointStatus,
    GetMapState,
    GetRelocationState,
)
from deebot_client.events.status import (
    BreakPointStatusEvent,
    MapStateEvent,
    RelocationStateEvent,
)
from tests.helpers import get_request_json, get_success_body

from . import assert_command


@pytest.mark.parametrize(
    ("json", "expected"),
    [
        (
            {"status": 0, "isConflict": 0, "continueLeftTime": 0},
            BreakPointStatusEvent(status=0, is_conflict=False, continue_left_time=0),
        ),
        (
            {"status": 1, "isConflict": 1, "continueLeftTime": 600},
            BreakPointStatusEvent(status=1, is_conflict=True, continue_left_time=600),
        ),
    ],
)
async def test_GetBreakPointStatus(
    json: dict[str, Any], expected: BreakPointStatusEvent
) -> None:
    json, firmware_event = get_request_json(get_success_body(json))
    await assert_command(GetBreakPointStatus(), json, (firmware_event, expected))


@pytest.mark.parametrize(
    ("json", "expected"),
    [
        ({"state": "built"}, MapStateEvent(state="built")),
        ({"state": "idle"}, MapStateEvent(state="idle")),
    ],
)
async def test_GetMapState(json: dict[str, Any], expected: MapStateEvent) -> None:
    json, firmware_event = get_request_json(get_success_body(json))
    await assert_command(GetMapState(), json, (firmware_event, expected))


@pytest.mark.parametrize(
    ("json", "expected"),
    [
        (
            {"isHasMap": 0, "mode": "lift", "state": "break"},
            RelocationStateEvent(is_has_map=False, mode="lift", state="break"),
        ),
        (
            {"isHasMap": 1, "mode": "move", "state": "ready"},
            RelocationStateEvent(is_has_map=True, mode="move", state="ready"),
        ),
    ],
)
async def test_GetRelocationState(
    json: dict[str, Any], expected: RelocationStateEvent
) -> None:
    json, firmware_event = get_request_json(get_success_body(json))
    await assert_command(GetRelocationState(), json, (firmware_event, expected))
