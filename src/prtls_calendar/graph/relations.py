"""Calendar node and edge vocabulary."""

from prtls_graph import EdgeKind, NodeKind

from .payloads import CalendarEventPayload, CalendarPayload


CALENDAR = NodeKind("prtls.calendar", "calendar", CalendarPayload)
CALENDAR_EVENT = NodeKind("prtls.calendar", "event", CalendarEventPayload)

CONTAINS_EVENT = EdgeKind(
    namespace="prtls.calendar",
    name="contains-event",
    directed=True,
    reverse_name="contained-by-calendar",
    a_payload_types=frozenset({CalendarPayload}),
    b_payload_types=frozenset({CalendarEventPayload}),
)
