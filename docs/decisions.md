# Decisions

## 1. Hugo 0.170.1 with layouts in this repository

**Decision.** Use Hugo 0.170.1 and write the layouts in `layouts/`. Do not use a theme.

**Why.** Hugo has built-in multilingual support (translations by file suffix, i18n tables, and hreflang), and it is one binary with no Ruby or Node toolchain. GitHub publishes a Pages Actions workflow for it. Jekyll was rejected because it has no built-in i18n, GitHub Pages limits which plugins can run, and it needs Ruby. Astro was rejected because it needs Node, and fallback plus hreflang are more manual there. Eleventy was rejected because its i18n comes from a plugin and it needs Node.

**Date.** 2026-11-25

## 2. Translations by file name

**Decision.** Translate by file name (`.en.md` / `.zh.md`). Serve English at `/` and Chinese at `/zh/`. The language toggle always has a real target.

**Why.** `defaultContentLanguage` is `en` and `defaultContentLanguageInSubdir` is `false`, so English stays at the root and Chinese is under `/zh/`. `layouts/partials/href.html` links to the translated page when it exists, and otherwise to that language's home page.

**Date.** 2026-11-25

## 3. Publications in one YAML file

**Decision.** Keep publications in `data/publications.yaml` rather than BibTeX.

**Why.** Hugo has no BibTeX pipeline. One YAML file can be edited in the GitHub web UI.

**Date.** 2026-11-25

## 4. ORCID is the source of truth for publications

**Decision.** Publication records follow the public ORCID record <https://orcid.org/0009-0003-6736-6496>. Where the CV draft and ORCID disagree, ORCID wins.

**Why.** Owner's decision. The YAML file and the publications page both cite that record.

**Date.** 2026-11-25

## 5. No CV PDF in v1

**Decision.** v1 has no CV download by design. The `cv` params stay empty.

**Why.** Owner's decision. `[params] cv`, `[languages.en.params] cv`, and `[languages.zh.params] cv` are empty, so the home page renders no download link. The pages list awarded grants only and leave out referees.

**Date.** 2026-11-25

## 6. Dark mode without a theme flash

**Decision.** Offer light, dark, and system themes through a blocking inline script in `head`. The default is system.

**Why.** `layouts/partials/theme-init.html` is included from `layouts/partials/head.html` before the stylesheet. The script reads `localStorage` key `theme` (`light`, `dark`, or `system`). When the stored value is missing it uses `system`, then sets `data-theme` from `prefers-color-scheme`. Applying the theme before CSS loads avoids a flash of the other theme.

**Date.** 2026-11-25

## 7. Deploy with GitHub Actions

**Decision.** GitHub Actions builds and deploys on push to `main`. The GitHub Pages source is GitHub Actions.

**Why.** `.github/workflows/hugo.yaml` deploys on push to `main` and on manual `workflow_dispatch`. Pull requests run the build, the `i18n|MISSING_TRANSLATION` check, and `scripts/check_site.py`, and they do not deploy. One-time repository setup is Settings > Pages > Source = GitHub Actions.

**Date.** 2026-11-25

## 8. Institution names stay in English on Chinese pages

**Decision.** Write institution names in English on Chinese pages. Translate city and country names.

**Why.** Owner's content rule. Experience and education `org.zh` values repeat the English institution name. Grant `funder` values have no Chinese string, so `layouts/partials/loc.html` keeps the English name. `place.zh` holds the translated city and country.

**Date.** 2026-11-25
