# ADR-0018: Typed taglines on the home page

- Date: 2026-11-26
- Status: accepted

## Context

The GitHub profile intro keeps the name fixed and types three field-based taglines in turn. The owner wanted the same effect on the site.

## Decision

Under the name on `/` and `/zh/`, a line types the three taglines from `taglines` in `data/profile.yaml` in turn (type, hold about 2.6 s, erase). English: Environmental Epidemiologist; Climate, Environment & Cardiovascular Health; R · Python · Data Science. Chinese: 环境流行病学研究者; 气候、环境与心血管健康; R · Python · 数据科学. The role and affiliation lines stay below.

## Rationale

Owner's request on 2026-11-26. A small inline script in `layouts/home.html` does the typing because the text is real page text, not an image.

## Consequences

- Without JavaScript, or with `prefers-reduced-motion: reduce`, the first tagline shows still and the caret is hidden.
- Screen readers get all three taglines once from a visually hidden span; the typed text and caret are `aria-hidden`.
- On screens up to 30rem the English line reserves two lines, so the longest tagline does not push the content down while it types.
- The site check fails if the screen-reader text differs from `data/profile.yaml`, the first tagline is missing without JavaScript, or the script stops checking reduced motion.
