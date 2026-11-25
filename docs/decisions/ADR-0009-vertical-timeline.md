# ADR-0009: Vertical timeline

- Date: 2026-11-25
- Status: accepted

## Context

The timeline needs to be scannable on a phone and in the existing narrow column. A studied reference presents a career as a horizontal rail of nodes. That rail is distinctive enough that imitating it would be a copying risk. The borrowing limits are in `docs/references.md`.

## Decision

Use a vertical, original timeline. Do not build a horizontal rail.

## Rationale

Owner's decision on 2026-11-25. A vertical ordered list fits the current layout, works at a narrow width without a side column, and does not reproduce the reference rail, its node treatment, or its class names.

## Consequences

`layouts/partials/timeline.html` renders an `<ol class="timeline">`. Dates stack with the item. There is no connector-and-dot graphic and no horizontal track. `prefers-reduced-motion` is respected by not adding required motion.
