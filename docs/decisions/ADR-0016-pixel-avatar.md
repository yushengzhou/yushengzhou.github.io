# ADR-0016: Pixel-art avatar as the portrait

- Date: 2026-11-26
- Status: accepted

## Context

The portrait was the last placeholder (`static/img/portrait.svg`).

## Decision

The portrait is the owner's pixel-art avatar, `static/img/portrait.jpg` (190 × 190). It renders with `image-rendering: pixelated` so the pixels stay sharp at 88 px.

## Rationale

Owner's choice on 2026-11-26.

## Consequences

`portrait_placeholder` is `false`, so no placeholder badge is left on the site. The alt text says it is a pixel-art avatar.
