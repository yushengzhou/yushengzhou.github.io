# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

v1 of the academic site.

### Added

- Hugo 0.170.1 static site. Layouts are in `layouts/`. The repository has no theme.
- English pages at `/` and Chinese pages at `/zh/`, with `*.en.md` / `*.zh.md` translations, `i18n/en.yaml` and `i18n/zh.yaml`, and `hreflang` for `en`, `zh`, and `x-default`.
- Language toggle. A page with no translation links to that language's home page.
- Home page with about text, research interests, profile, experience, education, awarded grants, and selected publications.
- Publications page. Ten journal articles from ORCID 0009-0003-6736-6496 live in `data/publications.yaml` and are ordered by year, then month.
- Projects section. With no project pages, the section shows an empty state.
- Light, dark, and system color theme. The default is system. A blocking inline script in `head` applies the theme before CSS loads.
- GitHub Actions workflow `.github/workflows/hugo.yaml`. Pull requests run the Hugo build, fail on the `i18n|MISSING_TRANSLATION` warning, and run `scripts/check_site.py`. A push to `main` deploys `public/` to GitHub Pages.
- `public/en/index.html`, a `noindex` refresh redirect to the English home page (`layouts/alias.html`).
- Placeholder badge (`PLACEHOLDER` / `占位`). The only placeholder is the portrait, `static/img/portrait.svg`.

v1 has no CV download by design. `[params] cv`, `[languages.en.params] cv`, and `[languages.zh.params] cv` are empty, and `static/` contains no PDF. Institution names are English on Chinese pages. City and country names are translated. The portrait placeholder is `static/img/portrait.svg` with `portrait_placeholder: true` in `data/profile.yaml`.
