# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed (2026-11-26)

- The homepage is slimmer: profile, About, research interests, selected publications, and links to all publications and the full timeline. The timeline preview and the grants block are gone from the homepage (ADR-0014).
- Grant amounts are no longer published and are removed from `data/grants.yaml` (ADR-0015).
- The portrait is the owner's pixel-art avatar, `static/img/portrait.jpg`, so no placeholder is left (ADR-0016).

### Added

- Bilingual Hugo 0.170.1 site with layouts in this repository and no theme. English is at `/` and Chinese is at `/zh/`.
- Home page prose, profile, awarded grants, and selected publications. The publications page lists the ORCID works. The projects section shows an empty state until project pages are added.
- Light, dark, and system color theme. The default is system. A blocking script in `head` applies the theme before CSS loads.
- Language toggle that uses the translated page or that language's home page, plus `hreflang` for `en`, `zh`, and `x-default`.
- GitHub Actions workflow that checks pull requests and deploys `public/` to GitHub Pages on a push to `main`.
- Vertical timeline at `/timeline/` and `/zh/timeline/`. `data/timeline.yaml` points at existing education, position, publication, and grant ids. The full page lists every row. Type filters are buttons and need JavaScript. With JavaScript off, every item stays visible.
- `public/en/index.html`, a `noindex` refresh to the English home page.
- Placeholder badge (`PLACEHOLDER` / `占位`).
- Owner notes in this file, the README, `docs/spec-timeline.md`, `docs/references.md`, and `docs/decisions/`.

v1 has no CV download by design. The three `cv` params are empty, and `static/` contains no PDF.

### Changed

- The homepage Experience and Education blocks are replaced by a timeline preview of education and positions. Awarded grants and selected publications stay on the homepage.
- Institution names on Chinese pages are the English names. City and country names stay translated.
- The Actions install checks the Hugo release checksum. Nav links, the language toggle, and the CV link styles use a hit area of at least 44px.
- The site check covers the timeline pages, order, filters, semantics, and exclusions, and it expects at least 21 timeline rows.

### Fixed

- The i18n gate fails the job only when the build log contains Hugo's warning id `i18n|MISSING_TRANSLATION`.
- The site check reads the tree in Python, so the pull-request job does not need ripgrep.
