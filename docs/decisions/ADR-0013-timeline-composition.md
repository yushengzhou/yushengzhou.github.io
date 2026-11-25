# ADR-0013: Timeline rows compose existing records by id

- Date: 2026-11-25
- Status: accepted

## Context

Education, positions, publications, and awarded grants already live in their own YAML files. Copying titles and authors into a second file would drift.

## Decision

`data/timeline.yaml` composes existing records by id. A row adds `type`, `from`, `start`, `end`, and `source`. It does not duplicate display fields.

## Rationale

Owner's decision on 2026-11-25, matching the timeline addendum. `layouts/partials/timeline.html` loads the record with the same id from `data/experience.yaml`, `data/education.yaml`, `data/publications.yaml`, or `data/grants.yaml` according to `from`. `start` is `YYYY` or `YYYY-MM`. `end` uses that form, or `null` when the role is open. Sort is newest `start`, then newest `end`, with an empty `end` first inside the same `start`, then `id` descending.

## Consequences

Editing a title, role, or organization happens in the source file and shows up on the timeline. Adding an item means a source record plus one timeline row. Publications on the timeline use `source: orcid`. The visible date text still comes from the source record. `start` is what `<time datetime>` uses.
