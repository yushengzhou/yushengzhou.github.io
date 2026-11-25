# ADR-0006: Dark mode without a theme flash

- Date: 2026-11-25
- Status: accepted

## Context

The site offers a light theme, a dark theme, and the visitor's system theme. Applying the choice after CSS loads flashes the other theme.

## Decision

Offer light, dark, and system themes through a blocking inline script in `head`. The default is system.

## Rationale

`layouts/partials/theme-init.html` is included from `layouts/partials/head.html` before the stylesheet. The script reads `localStorage` key `theme` (`light`, `dark`, or `system`). When the stored value is missing it uses `system`, then sets `data-theme` from `prefers-color-scheme`. Applying the theme before CSS loads avoids a flash of the other theme.

## Consequences

`meta name="color-scheme"` is `light dark`. The header buttons set the same preference after load. The timeline uses the existing color variables.
