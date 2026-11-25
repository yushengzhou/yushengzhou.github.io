# ADR-0001: Hugo 0.170.1 with layouts in this repository

- Date: 2026-11-25
- Status: accepted

## Context

The site needs English and Chinese pages, a static build, and a deploy path that a single maintainer can run from Git. Theme packages and a Node or Ruby toolchain were available alternatives.

## Decision

Use Hugo 0.170.1 and write the layouts in `layouts/`. Do not use a theme.

## Rationale

Hugo has built-in multilingual support (translations by file suffix, i18n tables, and hreflang), and it is one binary with no Ruby or Node toolchain. GitHub publishes a Pages Actions workflow for it. Jekyll was rejected because it has no built-in i18n, GitHub Pages limits which plugins can run, and it needs Ruby. Astro was rejected because it needs Node, and fallback plus hreflang are more manual there. Eleventy was rejected because its i18n comes from a plugin and it needs Node.

## Consequences

`hugo.toml` sets no `theme`. Layouts, partials, and `assets/css/main.css` live in this repository. CI installs the Hugo 0.170.1 release archive and checks its checksum.
