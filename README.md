# prtls-calendar

`prtls-calendar` is the graph-native calendar domain for the Protellus ecosystem.

It specializes `prtls-graph` and `prtls-graph-operations` with typed calendar
payloads, calendar node and edge vocabulary, date invariants, graph bindings, and
domain actions. Graph storage remains owned by `prtls-graph`.

This package deliberately has no Django, Seije, Shopify, spreadsheet, email, or
provider dependencies. Product applications compose it through graph operations
and their own integration layers.

## Domain vocabulary

The initial graph contains two node kinds:

- `prtls.calendar/calendar`
- `prtls.calendar/event`

and one directed relationship:

- `prtls.calendar/contains-event`: calendar → event

Calendar and event nodes are mutable graph entities. Updates retain their stable
`NodeId`, advance the graph-owned version, and use `payload_hash` only as equality
evidence.
