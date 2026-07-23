# Live Unraid introspection diff

- Captured: 2026-07-23T19:28:22Z
- Source: production Unraid API used by `runraid`
- Snapshot: `schema/live-introspection.json`
- Compared with: `schema/unraid-schema.graphql`
- Comparison: normalized structural contract
- Result: no semantic differences

The comparison covers operation roots, named types, field return types, field
arguments, input fields, enum values, implemented interfaces, and union member
types. Descriptions, ordering, default values, and applied directive locations
are excluded because standard introspection cannot reproduce the complete SDL
source representation.

The four deprecated Docker `skipCache` arguments on `containers`, `networks`,
`organizer`, and `portConflicts` are present in both the live API and vendored
SDL. An earlier diff incorrectly reported them as removed because its
introspection query did not request deprecated arguments. The committed capture
uses `includeDeprecated: true`.

Refresh and check:

```bash
just schema-live-capture
just schema-live-diff
```

The daily `.github/workflows/schema-drift.yml` job runs the same live check on
the self-hosted Unraid runner using the upstream configuration from the running
`runraid` container.
