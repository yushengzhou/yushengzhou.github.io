# ADR-0004: ORCID is the source of truth for publications

- Date: 2026-11-25
- Status: accepted

## Context

A CV draft and the public ORCID record do not always use the same title, date, or author list. The site needs one rule when they disagree.

## Decision

Publication records follow the public ORCID record <https://orcid.org/0009-0003-6736-6496>. Where the CV draft and ORCID disagree, ORCID wins. Positions and education follow the CV.

## Rationale

Owner's decision. The `orcid` field in `data/profile.yaml`, the publications page, and each publication row in `data/timeline.yaml` (`source: orcid`) cite that record.

## Consequences

`data/publications.yaml` stores the ORCID title, venue, year, and month. Chinese title and venue keys are omitted unless that string is the title of record, and `layouts/partials/loc.html` then shows the English string. The site check expects 10 publication entries.
