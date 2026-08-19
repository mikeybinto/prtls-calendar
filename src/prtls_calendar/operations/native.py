"""Native calendar graph operations."""

from __future__ import annotations

from typing import ClassVar

from pydantic import ConfigDict
from prtls_graph import GraphNode, GraphId
from prtls_graph_operations import GraphOperation, GraphOperationContext, GraphOperationInput
from prtls_graph.graph_store.service import GraphService
from prtls_operations import OperationComposition, OperationRequest, OperationSnapshot

from ..graph.payloads import CalendarEventPayload, CalendarPayload
from ..graph.relations import CALENDAR, CALENDAR_EVENT
from ..graph.actions import CalendarGraphActions
from ..graph.specialization import CalendarGraph


class _CalendarGraphOperationMixin:
    """Bind calendar operations to the specialized graph vocabulary."""

    graph_type = CalendarGraph

    def _build_graph_actions(
        self,
        graph_id: GraphId,
        *,
        service: GraphService,
    ) -> CalendarGraphActions:
        return CalendarGraphActions(graph_id, graph=service)


class CalendarCreateInput(GraphOperationInput[CalendarPayload]):
    """Graph operation input for creating a calendar node."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class CalendarEventCreateInput(GraphOperationInput[CalendarEventPayload]):
    """Graph operation input for creating an event node."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class CreateCalendarOperation(
    _CalendarGraphOperationMixin,
    GraphOperation[
        CalendarCreateInput,
        GraphOperationContext,
        OperationRequest,
        CalendarPayload,
        GraphNode,
        OperationComposition,
        OperationSnapshot,
    ],
):
    """Create or reconcile one calendar node through graph storage."""

    operation_key = "prtls.calendar.create"
    input_model = CalendarCreateInput
    generated_model = CalendarPayload
    processed_output_model = GraphNode

    def _generate(
        self,
        request: OperationRequest,
        *,
        context: GraphOperationContext,
    ) -> GraphNode:
        operation_input = CalendarCreateInput.model_validate(context.input_payload)
        if operation_input.root_input is None:
            raise ValueError("calendar creation requires root_input")
        return operation_input.root_input

    def _process_output(
        self,
        generated: CalendarPayload,
        *,
        request: OperationRequest,
        context: GraphOperationContext,
    ) -> CalendarPayload:
        operation_input = CalendarCreateInput.model_validate(context.input_payload)
        return GraphNode.create(
            generated,
            kind=CALENDAR,
            node_id=(operation_input.start_node.node_id if operation_input.start_node else None),
        )


class CreateCalendarEventOperation(
    _CalendarGraphOperationMixin,
    GraphOperation[
        CalendarEventCreateInput,
        GraphOperationContext,
        OperationRequest,
        CalendarEventPayload,
        GraphNode,
        OperationComposition,
        OperationSnapshot,
    ],
):
    """Create or reconcile one calendar-event node through graph storage."""

    operation_key = "prtls.calendar.create-event"
    input_model = CalendarEventCreateInput
    generated_model = CalendarEventPayload
    processed_output_model = GraphNode

    def _generate(
        self,
        request: OperationRequest,
        *,
        context: GraphOperationContext,
    ) -> GraphNode:
        operation_input = CalendarEventCreateInput.model_validate(context.input_payload)
        if operation_input.root_input is None:
            raise ValueError("calendar-event creation requires root_input")
        return operation_input.root_input

    def _process_output(
        self,
        generated: CalendarEventPayload,
        *,
        request: OperationRequest,
        context: GraphOperationContext,
    ) -> CalendarEventPayload:
        operation_input = CalendarEventCreateInput.model_validate(context.input_payload)
        return GraphNode.create(
            generated,
            kind=CALENDAR_EVENT,
            node_id=(operation_input.start_node.node_id if operation_input.start_node else None),
        )
