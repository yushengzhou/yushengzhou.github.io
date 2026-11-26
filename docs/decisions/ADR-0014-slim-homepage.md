# ADR-0014: Slim homepage

- Date: 2026-11-26
- Status: accepted
- Supersedes: [ADR-0011](ADR-0011-timeline-scope.md) (homepage preview only; the full timeline is unchanged)

## Context

The homepage repeated most of the timeline: an education and position preview, then every awarded grant, then selected publications. It was about 4,000 px tall on desktop and 13 screens on a phone.

## Decision

The homepage shows the profile, the About prose and research interests, selected publications, and links to all publications and the full timeline. It has no timeline preview and no grants block.

## Rationale

Owner's decision on 2026-11-26. Positions, education, and grants stay on `/timeline/` and `/zh/timeline/`, where grants are milestones.

## Consequences

`layouts/partials/grants.html` is removed. The timeline partial keeps its `preview` option but the homepage no longer calls it. The site check fails if either homepage has a timeline, an experience, education, or grants block, or lacks the full-timeline link.
