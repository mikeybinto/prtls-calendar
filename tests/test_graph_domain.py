from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from prtls_graph import GraphNode

from prtls_calendar.graph import (
    CALENDAR,
    CALENDAR_EVENT,
    CONTAINS_EVENT,
    CalendarEventPayload,
    CalendarEventType,
    CalendarGraphActions,
    CalendarPayload,
    CalendarStorageSpec,
    DateSource,
)


def _event(**overrides):
    values = {
        "name": "Passover",
        "description": "Family meals and hosting.",
        "starts_at": datetime(2027, 4, 21, tzinfo=timezone.utc),
        "ends_at": datetime(2027, 4, 29, tzinfo=timezone.utc),
        "all_day": False,
    }
    values.update(overrides)
    return CalendarEventPayload(**values)


def test_calendar_payload_is_typed_and_strips_display_text():
    payload = CalendarPayload(name="  Store Calendar  ", timezone=" America/Toronto ")

    assert payload.name == "Store Calendar"
    assert payload.timezone == "America/Toronto"
    assert payload.payload_hash()


def test_event_rejects_reversed_ranges():
    with pytest.raises(ValidationError, match="ends_at"):
        _event(
            starts_at=datetime(2027, 4, 29, tzinfo=timezone.utc),
            ends_at=datetime(2027, 4, 21, tzinfo=timezone.utc),
        )


def test_all_day_event_requires_midnight_timestamps():
    with pytest.raises(ValidationError, match="midnight"):
        _event(
            starts_at=datetime(2027, 4, 21, 9, tzinfo=timezone.utc),
            ends_at=None,
            all_day=True,
        )


def test_event_embedding_is_the_occasion_text_only():
    assert _event().embedding_text() == "Passover Family meals and hosting."


def test_calendar_vocabulary_is_closed_and_typed():
    assert CalendarStorageSpec.node_kinds[CALENDAR.key] == CALENDAR
    assert CalendarStorageSpec.node_kinds[CALENDAR_EVENT.key] == CALENDAR_EVENT
    assert CalendarStorageSpec.edge_kinds[CONTAINS_EVENT.key] == CONTAINS_EVENT
    assert CalendarStorageSpec.edge_state_types == {}


def test_calendar_actions_build_the_complete_calendar_event_subgraph():
    calendar_payload = CalendarPayload(name="Store Calendar")
    event_payload = _event(
        event_type=CalendarEventType.HOLIDAY,
        date_source=DateSource.IMPORTED,
    )

    calendar, event, edge = CalendarGraphActions.calendar_with_event(
        calendar_payload,
        event_payload,
    )

    assert isinstance(calendar, GraphNode)
    assert isinstance(event, GraphNode)
    assert calendar.kind == CALENDAR
    assert event.kind == CALENDAR_EVENT
    assert edge.kind == CONTAINS_EVENT
    assert edge.endpoint_a.node_id == calendar.node_id
    assert edge.endpoint_b.node_id == event.node_id


def test_contains_event_rejects_wrong_endpoint_kinds():
    calendar = CalendarGraphActions.calendar_node(CalendarPayload(name="Calendar"))
    wrong = GraphNode.create(CalendarPayload(name="Not an event"), kind=CALENDAR)

    with pytest.raises(ValueError, match="target"):
        CalendarGraphActions.contains_event(calendar, wrong)
