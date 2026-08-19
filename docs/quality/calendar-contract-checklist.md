# Calendar contract checklist

This is the package-level evidence ledger for the graph-native calendar
contract. It is reviewed with every calendar change so the package remains
aligned with the `prtls-graph`, `prtls-graph-operations`, and prtls-core
engineering standards.

## Package boundary

- [x] The package owns typed calendar payloads, node/edge vocabulary, graph
  specialization, graph actions, and native operations.
  Evidence: `src/prtls_calendar/graph/` and `src/prtls_calendar/operations/`.
- [x] Storage remains graph-owned; the package does not define a storage
  service, ORM model, or compatibility binding.
  Evidence: `CalendarGraph` declares `CalendarStorageSpec`; operations use the
  graph-operation service hook.
- [x] Tenant identity is inherited from graph infrastructure and is not
  re-declared by calendar operations.
  Evidence: `CalendarGraph.GRAPH_SCOPE = GraphScope.WORKSPACE` and the graph
  conformance identity fixtures.

## Graph specialization and service ownership

- [x] A concrete graph subclass declares the graph scope and closed vocabulary.
  Evidence: `src/prtls_calendar/graph/specialization.py`.
- [x] Graph selection is carried by the typed `GraphId` input coordinate.
  Evidence: `GraphOperationInput` subclasses and
  `DEFAULT_CALENDAR_GRAPH_ID`.
- [x] Domain operations do not construct `GraphService` or a domain-specific
  graph service.
  Evidence: `_CalendarGraphOperationMixin._build_graph_actions()` receives the
  graph-owned `GraphService` and returns `CalendarGraphActions(graph_id,
  graph=service)`.
- [x] Domain actions specialize `GraphActions` without owning persistence.
  Evidence: `CalendarGraphActions` subclasses `GraphActions` and delegates
  mutations to its inherited graph collaborator.

## Typed operation surface

- [x] Every public operation input is a frozen, `extra="forbid"` Pydantic
  model.
  Evidence: `CalendarCreateInput` and `CalendarEventCreateInput`.
- [x] Operations use typed generic parameters and typed protected hook
  signatures; no loose runtime-options bag is used for domain input.
  Evidence: `src/prtls_calendar/operations/native.py`.
- [x] Controlled calendar values use domain enums/constants and validated
  payload models.
  Evidence: `graph/payloads.py` and `graph/relations.py`.
- [x] No domain operation overrides the public operation lifecycle or uses a
  capability-string dispatcher.
  Evidence: operations subclass `GraphOperation` and specialize protected
  hooks only.

## Graph coordinates, tenancy, and atomicity

- [x] Workspace graph scope requires ambient organization and workspace
  identity through graph-owned resolution.
- [x] The domain does not conflate graph namespace with ambient identity;
  `graph_id` remains the explicit graph coordinate.
- [x] Graph writes use graph-owned batch and transaction behavior.
  Evidence: inherited domain and graph-service conformance suites.
- [x] Calendar vocabulary rejects undeclared node and edge kinds.
  Evidence: `CalendarStorageSpec` and graph conformance.

## Conformance and verification

- [x] Calendar subclasses `GraphOperationConformance` for every native
  operation.
  Evidence: `tests/test_operation_conformance.py`.
- [x] Calendar subclasses `DomainGraphConformanceTests` and
  `GraphServiceConformanceTests`.
  Evidence: `tests/test_graph_conformance.py`.
- [x] Happy paths, error paths, edge cases, graph coordinates, tenant
  isolation, atomic batches, rollback, context/freeze, and background/context
  rehydration are exercised by the inherited suites.
- [x] Package-specific payload and vocabulary invariants remain beside the
  inherited suites in `tests/test_graph_domain.py`.
- [x] The full local verification result for this checklist change is recorded
  here after execution:

  ```text
  pytest: 94 passed, 35 skipped
  pyright: 0 errors, 0 warnings, 0 informations
  compileall: pass
  diff check: pass
  ```

Optional provider- or environment-gated inherited cases may be reported as
skipped; they remain collected and are not removed from the conformance base.
