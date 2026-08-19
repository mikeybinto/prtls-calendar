# Calendar package checks

Run these commands from the package root before review:

```powershell
python -m pytest -q
python -m compileall -q src
git diff --check
```

The graph and graph-operation conformance suites are inherited from
`prtls-graph` and `prtls-graph-operations`; their optional provider/environment
coverage is reported as skipped by pytest rather than removed from collection.
