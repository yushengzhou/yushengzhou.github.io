# ADR-0015: No grant amounts

- Date: 2026-11-26
- Status: accepted

## Context

`data/grants.yaml` stored an `amount` for each awarded grant, and the homepage and timeline showed it.

## Decision

Grant amounts are not published. `data/grants.yaml` has no `amount` field, and no template renders one.

## Rationale

Owner's decision on 2026-11-26. The repository is public, so the values are removed from the data file as well as from the pages.

## Consequences

Grants show title, dates, role, and funder. The site check fails if `amount` returns to `data/grants.yaml`. Earlier values remain in git history.
