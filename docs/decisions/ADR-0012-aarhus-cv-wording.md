# ADR-0012: Aarhus role uses the CV wording

- Date: 2026-11-25
- Status: accepted

## Context

ORCID lists the Aarhus job more than once. One listing is an open-ended postdoc researcher role. Another uses the title "VIP, Postdoc" and an end date in October 2028. The CV wording is different.

## Decision

The Aarhus entry uses the CV wording "Postdoctoral Researcher, Nov 2026 – Present". It does not use the ORCID "VIP, Postdoc" title or the 2028 end date.

## Rationale

Owner's decision on 2026-11-25. Positions follow the CV ([ADR-0004](ADR-0004-orcid-publications.md)). The experience record `au-dph-2026` stores that role and the open-ended dates. Its timeline row sets `end: null` and `source: cv`.

## Consequences

The timeline shows the CV role and the current-role label from `when` ("Nov 2026 – Present" / "2026年11月–至今"). The site check fails if the built timeline contains the VIP title or `2028-10`. A later ORCID end date is not shown unless the owner changes this decision.
