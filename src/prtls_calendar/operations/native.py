"""Native calendar graph operations."""

from __future__ import annotations

from pydantic import ConfigDict
from prtls_graph import GraphNode
from prtls_graph_operations import GraphOperation, GraphOperationInput

from ..graph.payloads import CalendarEventPayload, CalendarPayload
from ..graph.relations import CALENDAR, CALENDAR_EVENT


class CalendarCreateInput(GraphOperationInput[CalendarPayload]):
    """Graph operation input for creating a calendar node."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class CalendarEventCreateInput(GraphOperationInput[CalendarEventPayload]):
    """Graph operation input for creating an event node."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class CreateCalendarOperation(GraphOperation):
    """Create or reconcile one calendar node through graph storage."""

    operation_key = "prtls.calendar.create"
    input_model = CalendarCreateInput
    generated_model = CalendarPayload
    processed_output_model = GraphNode
    mutating = True

    def _generate(self, request, *, context):
        operation_input = CalendarCreateInput.model_validate(context.input_payload)
        if operation_input.root_input is None:
            raise ValueError("calendar creation requires root_input")
        return operation_input.root_input

    def _process_output(self, generated, *, request, context):
        operation_input = CalendarCreateInput.model_validate(context.input_payload)
        return GraphNode.create(
            generated,
            kind=CALENDAR,
            node_id=(operation_input.start_node.node_id if operation_input.start_node else None),
        )


class CreateCalendarEventOperation(GraphOperation):
    """Create or reconcile one calendar-event node through graph storage."""

    operation_key = "prtls.calendar.create-event"
    input_model = CalendarEventCreateInput
    generated_model = CalendarEventPayload
    processed_output_model = GraphNode
    mutating = True

    def _generate(self, request, *, context):
        operation_input = CalendarEventCreateInput.model_validate(context.input_payload)
        if operation_input.root_input is None:
            raise ValueError("calendar-event creation requires root_input")
        return operation_input.root_input

    def _process_output(self, generated, *, request, context):
        operation_input = CalendarEventCreateInput.model_validate(context.input_payload)
        return GraphNode.create(
            generated,
            kind=CALENDAR_EVENT,
            node_id=(operation_input.start_node.node_id if operation_input.start_node else None),
        )
