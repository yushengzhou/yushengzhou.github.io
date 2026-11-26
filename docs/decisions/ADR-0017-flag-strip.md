# ADR-0017: Flag strip on the full timeline

- Date: 2026-11-26
- Status: accepted

## Context

The full timeline is a vertical list. The owner wanted the "All" view to also show, at a glance, where each period was spent, like a horizontal year axis with a flag for each place.

## Decision

`/timeline/` and `/zh/timeline/` show a horizontal year axis above the list, with one flag per stay and a bar for its dates. `data/stays.yaml` lists the stays. Each stay points at ids in `data/timeline.yaml`; its dates come from those rows and its city label from the first record's `place`. The strip is shown with the All filter and hidden by the other filters.

Every stay uses its country flag, so Montréal and Toronto both show the flag of Canada (owner's correction on 2026-11-26; the first version used the Quebec and Ontario flags). Flags are the public-domain SVGs from the `region-flags` npm package (1.1.0), copied to `static/img/flags/`.

## Rationale

Owner's request on 2026-11-26. Pointing at timeline ids keeps one source for dates (ADR-0013). Flags alternate between two lanes so short consecutive stays (Toronto, then Aarhus) do not overlap. On narrow screens the strip scrolls sideways inside its box and opens scrolled to the most recent years. Gaps with no recorded place stay empty.

## Consequences

An open-ended stay runs to the end of the build month, so the strip moves forward only when the site is rebuilt. The site check fails if a stay points at an unknown id, a flag file is missing, the rendered flags differ from `data/stays.yaml`, the strip is hidden without JavaScript, or the strip appears on another page.
