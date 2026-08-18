"""Closed storage vocabulary for the calendar domain."""

from prtls_graph import EdgeKindDefinition, GraphStorageServiceSpec

from .relations import CALENDAR, CALENDAR_EVENT, CONTAINS_EVENT


CalendarStorageSpec = GraphStorageServiceSpec.define(
    EdgeKindDefinition(kind=CONTAINS_EVENT),
    node_kinds=(CALENDAR, CALENDAR_EVENT),
)
