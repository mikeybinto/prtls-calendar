"""Calendar graph and graph-service conformance against the shared suites."""

from __future__ import annotations

from types import MethodType
from uuid import NAMESPACE_URL, uuid5

import pytest
from prtls_core.security.identity_context import IdentityContext
from prtls_graph import (
    EdgeKind,
    EdgeKindDefinition,
    GraphId,
    GraphStorageServiceSpec,
    KernelGraphEdge,
    KernelGraphNode,
    NodeRef,
)
from prtls_graph.elements import GraphEdge, GraphElementBase, GraphNode
from prtls_graph.graph_elements import GraphElementError
from prtls_graph.graph_store.service import GraphService
from prtls_graph.tests.conformance import (
    CONFORMANCE_NODE_KIND,
    DomainGraphCase,
    DomainBoundaryClosureCase,
    DomainSearchCase,
    DomainGraphConformanceTests,
    GraphServiceConformanceTests,
)
from prtls_graph.tests.conformance.node_ids import node_id as nid
from prtls_io import CallPlan

from prtls_calendar import (
    CALENDAR,
    CALENDAR_EVENT,
    CONTAINS_EVENT,
    CalendarEventPayload,
    CalendarGraph,
    CalendarPayload,
    CalendarStorageSpec,
)


ORG = "calendar-conformance-org"
WORKSPACE = "calendar-conformance-workspace"
GRAPH_ID = GraphId(uuid5(NAMESPACE_URL, "https://protellus.ca/graphs/prtls-calendar/conformance"))
ISOLATED_GRAPH_ID = GraphId(uuid5(NAMESPACE_URL, "https://protellus.ca/graphs/prtls-calendar/isolated"))

TEST_TRAVERSAL = EdgeKind("prtls.calendar.testing", "traverses", directed=True)
TEST_REPLACEMENT = EdgeKind("prtls.calendar.testing", "replacement", directed=True)
TEST_STATEFUL = EdgeKind("prtls.calendar.testing", "stateful", directed=True)
TEST_BOUNDARY = EdgeKind("prtls.calendar.testing", "boundary", directed=True)
TEST_UNDIRECTED = EdgeKind("prtls.calendar.testing", "undirected", directed=False)

CONFORMANCE_SPEC = GraphStorageServiceSpec.compose(
    CalendarStorageSpec,
    GraphStorageServiceSpec.define(
        EdgeKindDefinition(kind=TEST_TRAVERSAL),
        EdgeKindDefinition(kind=TEST_REPLACEMENT),
        EdgeKindDefinition(kind=TEST_STATEFUL, state_type=str),
        EdgeKindDefinition(kind=TEST_BOUNDARY),
        EdgeKindDefinition(kind=TEST_UNDIRECTED),
        node_kinds=(CONFORMANCE_NODE_KIND,),
    ),
)


class CalendarConformanceGraph(CalendarGraph):
    GRAPH_SPEC = CONFORMANCE_SPEC


def _calendar(name: str) -> KernelGraphNode:
    return KernelGraphNode.create(CalendarPayload(name=name), kind=CALENDAR, id=nid(name))


def _event(name: str) -> KernelGraphNode:
    return KernelGraphNode.create(CalendarEventPayload(name=name), kind=CALENDAR_EVENT, id=nid(name))


@pytest.mark.django_db(transaction=True)
class TestCalendarDomainGraphConformance(DomainGraphConformanceTests):
    def make_graph_binding(self) -> GraphService:
        return GraphService(graph_id=GRAPH_ID, graph_type=CalendarConformanceGraph)

    def make_isolated_graph_binding(self) -> GraphService:
        return GraphService(graph_id=ISOLATED_GRAPH_ID, graph_type=CalendarConformanceGraph)

    def domain_case(self) -> DomainGraphCase:
        parent = _calendar("calendar-parent")
        child = _event("calendar-child")
        return DomainGraphCase(
            elements=(parent, child, KernelGraphEdge(endpoint_a=parent.id, endpoint_b=child.id, kind=TEST_TRAVERSAL)),
            parent_id=parent.id,
            child_id=child.id,
            revised_parent=KernelGraphNode.create(CalendarPayload(name="revised-parent"), kind=CALENDAR, id=parent.id),
            competing_parent=KernelGraphNode.create(CalendarPayload(name="competing-parent"), kind=CALENDAR, id=parent.id),
            revised_child=KernelGraphNode.create(CalendarEventPayload(name="revised-child"), kind=CALENDAR_EVENT, id=child.id),
            competing_child=KernelGraphNode.create(CalendarEventPayload(name="competing-child"), kind=CALENDAR_EVENT, id=child.id),
            replacement_kind=TEST_REPLACEMENT,
            stateful_kind=TEST_STATEFUL,
            competing_states=("planned", "active"),
            unknown_kind=EdgeKind("prtls.calendar.unknown", "relation", directed=True),
        )

    def ambient_identity_context(self) -> IdentityContext:
        return IdentityContext(org_id=ORG, user_id="calendar-conformance-user", workspace_id=WORKSPACE)

    def boundary_closure_case(self) -> DomainBoundaryClosureCase:
        root = _calendar("boundary-root")
        internal = _event("boundary-internal")
        reference = _event("boundary-reference")
        beyond = _event("boundary-beyond")
        return DomainBoundaryClosureCase(
            elements=(
                root,
                internal,
                reference,
                beyond,
                KernelGraphEdge(endpoint_a=root.id, endpoint_b=internal.id, kind=TEST_TRAVERSAL),
                KernelGraphEdge(endpoint_a=internal.id, endpoint_b=reference.id, kind=TEST_BOUNDARY),
                KernelGraphEdge(endpoint_a=reference.id, endpoint_b=beyond.id, kind=TEST_TRAVERSAL),
            ),
            root_id=root.id,
            reference_id=reference.id,
            beyond_id=beyond.id,
            traversal_kind=TEST_TRAVERSAL,
            boundary_kind=TEST_BOUNDARY,
            revised_reference=KernelGraphNode.create(
                CalendarEventPayload(name="boundary-reference-revised"),
                kind=CALENDAR_EVENT,
                id=reference.id,
            ),
        )

    def search_case(self) -> DomainSearchCase:
        case = self.domain_case()
        return DomainSearchCase(elements=case.elements, query=[1.0], expected_node_id=case.parent_id)

    def rollback_scope(self, service: GraphService):
        return service.caller_transaction()

    @staticmethod
    def _inject_failure(service: GraphService, *, element_id: str) -> None:
        original_create = service._create

        def failing_create(
            bound_service: GraphService,
            payload: GraphElementBase,
            *,
            plan: CallPlan | None = None,
            **kwargs: object,
        ) -> GraphElementBase:
            del bound_service
            if str(payload.id) == element_id:
                raise RuntimeError("injected graph write failure")
            return original_create(payload, plan=plan, **kwargs)

        service._create = MethodType(failing_create, service)

    def inject_atomic_graph_write_failure(self, service: GraphService, *, element_id: str) -> None:
        self._inject_failure(service, element_id=element_id)

    def inject_edge_establishment_failure(self, service: GraphService, *, edge_id: str) -> None:
        self._inject_failure(service, element_id=edge_id)

    def test_tree_edge_swap_uses_parent_child_vocabulary(self):
        service = self.make_graph_binding()
        case = self.domain_case()
        original = next(element for element in case.elements if isinstance(element, KernelGraphEdge))
        self._assert_write_ok(service.ensure_graph(case.elements))
        tree_swap = service.swap_child_edge(
            parent=original.endpoint_a,
            child=original.endpoint_b,
            current_kinds=(original.kind,),
            replacement_kind=case.replacement_kind,
            expected_current_edge_id=original.id,
        )
        assert tree_swap.status.value == "applied"
        with pytest.raises(GraphElementError, match="directed tree-compatible"):
            service.swap_child_edge(
                parent=original.endpoint_a,
                child=original.endpoint_b,
                current_kinds=(TEST_UNDIRECTED,),
                replacement_kind=case.replacement_kind,
            )


@pytest.mark.django_db(transaction=True)
class TestCalendarGraphServiceConformance(GraphServiceConformanceTests):
    @pytest.fixture(autouse=True)
    def _identity(self):
        with IdentityContext(org_id=ORG, user_id="calendar-service-user", workspace_id=WORKSPACE):
            yield

    def make_service(self) -> GraphService:
        return GraphService(graph_id=GRAPH_ID, graph_type=CalendarConformanceGraph)

    def sample_graph(self) -> tuple[list[GraphElementBase], object, object]:
        parent = GraphNode.from_node(_calendar("service-parent"))
        child = GraphNode.from_node(_event("service-child"))
        edge = GraphEdge.from_edge(KernelGraphEdge(endpoint_a=parent.id, endpoint_b=child.id, kind=CONTAINS_EVENT))
        return [parent, child, edge], parent.id, child.id

    def unknown_kind_element(self) -> GraphElementBase:
        return GraphEdge.create(
            endpoint_a=NodeRef(node_id=nid("unknown-a")),
            endpoint_b=NodeRef(node_id=nid("unknown-b")),
            kind=EdgeKind("prtls.calendar.unknown", "relation", directed=True),
        )

    def tenant_actors(self) -> tuple[IdentityContext, IdentityContext]:
        return (
            IdentityContext(org_id="calendar-tenant-a", user_id="user-a", workspace_id="workspace-a"),
            IdentityContext(org_id="calendar-tenant-b", user_id="user-b", workspace_id="workspace-b"),
        )
