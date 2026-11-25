# ADR-0005: No CV download in v1

- Date: 2026-11-25
- Status: accepted

## Context

A CV draft exists outside the repository. v1 still needs a public page built from the parts of that text that are meant to be published.

## Decision

v1 has no CV download by design. The `cv` params stay empty.

## Rationale

Owner's decision. `[params] cv`, `[languages.en.params] cv`, and `[languages.zh.params] cv` are empty, so `layouts/partials/cv.html` renders no download link. The pages list awarded grants only and leave out referees.

## Consequences

`static/` contains no PDF. The home page has no CV link. The site check fails if a PDF is present in the build.
