# ADR-0011: Full timeline and homepage preview

- Date: 2026-11-25
- Status: accepted; homepage preview superseded by [ADR-0014](ADR-0014-slim-homepage.md)

## Context

The same career facts should not appear twice on the home page. Visitors still need a full chronological list, and the home page already has awarded grants and selected publications.

## Decision

The full timeline shows all 10 ORCID publications and the 4 awarded grants as milestones, plus education and positions. The homepage preview shows education and positions only, and it replaces the Experience and Education blocks.

## Rationale

Owner's decision on 2026-11-25. `layouts/home.html` calls the timeline partial with `preview` set, then awarded grants, then selected publications. The preview keeps rows whose `type` is `education` or `position`. The full page passes `preview` false and lists every row in `data/timeline.yaml`.

## Consequences

`layouts/partials/experience.html` and `layouts/partials/education.html` are not on the home page. Awarded grants and selected publications stay where they were. Filter chips exist only on `/timeline/` and `/zh/timeline/`. The site check requires the preview to be education and positions only, and at least 21 timeline rows.
