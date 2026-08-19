"""Calendar graph specialization over graph-owned storage infrastructure."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from prtls_graph import Graph, GraphId, GraphScope, NodePayload

from .spec import CalendarStorageSpec


DEFAULT_CALENDAR_GRAPH_ID = GraphId(
    uuid5(NAMESPACE_URL, "https://protellus.ca/graphs/prtls-calendar/default")
)


class CalendarGraph(Graph[NodePayload]):
    """Workspace-contained calendar graph.

    The graph id selects the graph address; the inherited graph service resolves
    and enforces the ambient organization/workspace tenant boundary.
    """

    GRAPH_SCOPE = GraphScope.WORKSPACE
    GRAPH_SPEC = CalendarStorageSpec


__all__ = ["CalendarGraph", "DEFAULT_CALENDAR_GRAPH_ID"]
