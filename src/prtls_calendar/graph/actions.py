"""Calendar-specific graph actions.

These actions translate domain values into the graph vocabulary. They do not
open transactions or write storage directly; `prtls-graph` owns those mechanics.
"""

from __future__ import annotations

from prtls_graph import GraphActions, GraphEdge, GraphNode, NodeId, NodeRef

from .payloads import CalendarEventPayload, CalendarPayload
from .relations import CALENDAR, CALENDAR_EVENT, CONTAINS_EVENT


class CalendarGraphActions(GraphActions):
    """Build validated calendar graph elements and delegate graph mutations."""

    @staticmethod
    def calendar_node(payload: CalendarPayload, *, node_id: NodeId | None = None) -> GraphNode:
        return GraphNode.create(payload, kind=CALENDAR, node_id=node_id)

    @staticmethod
    def event_node(payload: CalendarEventPayload, *, node_id: NodeId | None = None) -> GraphNode:
        return GraphNode.create(payload, kind=CALENDAR_EVENT, node_id=node_id)

    @staticmethod
    def contains_event(calendar: GraphNode, event: GraphNode) -> GraphEdge:
        if calendar.kind != CALENDAR:
            raise ValueError("contains-event source must be a calendar node")
        if event.kind != CALENDAR_EVENT:
            raise ValueError("contains-event target must be a calendar event node")
        return GraphEdge.create(
            endpoint_a=NodeRef(node_id=calendar.node_id),
            endpoint_b=NodeRef(node_id=event.node_id),
            kind=CONTAINS_EVENT,
        )

    @classmethod
    def calendar_with_event(
        cls,
        calendar: CalendarPayload,
        event: CalendarEventPayload,
        *,
        calendar_id: NodeId | None = None,
        event_id: NodeId | None = None,
    ) -> tuple[GraphNode, GraphNode, GraphEdge]:
        calendar_node = cls.calendar_node(calendar, node_id=calendar_id)
        event_node = cls.event_node(event, node_id=event_id)
        return calendar_node, event_node, cls.contains_event(calendar_node, event_node)
