"""Calendar operations against the complete graph-operation contract."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from prtls_core.security.identity_context import IdentityContext
from prtls_graph_operations import GraphOperation, GraphOperationInput, GraphOperationResult
from prtls_graph_operations.testing import GraphOperationConformance

from prtls_calendar import CalendarEventPayload, CalendarPayload, DEFAULT_CALENDAR_GRAPH_ID
from prtls_calendar.operations import (
    CreateCalendarEventOperation,
    CreateCalendarOperation,
)


ORG = "calendar-operation-conformance-org"
WORKSPACE = "calendar-operation-conformance-workspace"


@pytest.mark.django_db(transaction=True)
class TestCalendarGraphOperationConformance(GraphOperationConformance):
    """Apply the inherited suite to every native calendar operation."""

    @pytest.fixture(autouse=True, params=(CreateCalendarOperation, CreateCalendarEventOperation))
    def _operation_case(self, request):
        with IdentityContext(
            org_id=ORG,
            user_id="calendar-operation-conformance-user",
            workspace_id=WORKSPACE,
        ):
            self._operation_type = request.param
            self.expected_operation_key = request.param.operation_key
            payload = (
                CalendarPayload(name="Conformance calendar")
                if request.param is CreateCalendarOperation
                else CalendarEventPayload(name="Conformance event")
            )
            self._graph_input = request.param.input_model(
                graph_id=DEFAULT_CALENDAR_GRAPH_ID,
                root_input=payload,
            )
            yield

    def build_graph_operation(self) -> GraphOperation:
        return self._operation_type()

    def build_graph_input(self) -> GraphOperationInput:
        return self._graph_input

    def _assert_graph_persistence_contract(
        self,
        operation: GraphOperation,
        result: GraphOperationResult,
    ) -> None:
        assert operation.last_execution_trace is not None
        assert result.anchor_node is not None
        with pytest.raises(TypeError, match="persistence requires"):
            operation._persist_graph_output(
                object(),
                context=operation.last_execution_trace.context,
                actions=SimpleNamespace(),
            )


def test_calendar_operations_use_the_specialized_graph_type():
    assert CreateCalendarOperation.graph_type.__name__ == "CalendarGraph"
    assert CreateCalendarEventOperation.graph_type is CreateCalendarOperation.graph_type
