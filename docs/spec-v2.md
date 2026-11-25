# Academic site v2: modular multi-page redesign

**Repo:** `yushengzhou/yushengzhou.github.io` (public, MIT, account `yushengzhou`). **Base:** `main` @ `11a81ac` (PR #1 merged 2026-11-25 23:16 UTC; default branch `main`). **Branch/PR:** one new branch `feat/site-v2`, one PR. **Extends:** the v1 site specification and `docs/spec-timeline.md`. **Where v2 conflicts with v1 or an ADR, v2 wins** (supersedes the vertical timeline and the home preview). Spec date 2026-11-26. Owner confirmed.

## Goal

A modular multi-page academic site: a one-screen About home with entry points, a horizontal timeline that puts education and work on one line with location flags, and a Grants page with no amounts. EN and ZH, light and dark, shipped together in one PR.

## Features

1. **F1 Home trimmed.** `/` and `/zh/` show only the existing hero, an intro of at most 60 words EN / 100 characters ZH, the five research directions, and four entry cards (Publications, Timeline / CV, Grants, Projects & Code). The timeline preview, the grants block, and selected publications leave the home page. The former About paragraph moves unchanged to the top of the Timeline / CV page as "Summary".
2. **F2 Top nav + separate pages.** Header nav, in order: About, Publications, Timeline / CV, Grants, Projects & Code. New pages: `content/grants.en.md` and `content/grants.zh.md` with `data: "grants"`. Labels come from i18n. The language toggle keeps the sibling-page behaviour. At 375px the nav wraps and each link stays at least 44px.
3. **F3 Horizontal merged timeline** at `/timeline/` and `/zh/timeline/`. One scrollable track, oldest left and newest right, year ticks from 2008 through the build year. Education and work share the axis. Year-only dates cover 1 January through 31 December. An empty `end` runs to now. Ends are exclusive at the start of the named month, so adjacent jobs touch without stacking. Overlaps stack in a second row. Each bar shows a flag with empty alt text, the city, the CV dates, and a text type label plus a stripe or border cue. Details open with the native `details` element and also on hover. The track scrolls inside its own container.
4. **F4 Grants page.** `/grants/` and `/zh/grants/` list the four awarded grants (title, role, funder, dates). No amount is stored or shown.

## Out of scope

Framework change, CV PDF download, awards, blog, talks, teaching, search, analytics, new fonts or JS packages, publications or grants on the timeline, and province flags. Phone number, referees, unsuccessful grants, and grants under review stay excluded. Rewriting git history is out of scope.

## Data

`country` (ISO 3166-1 alpha-2) is stored on each education and experience record. `data/countries.yaml` maps `cn`, `au`, `de`, `ca`, and `dk` to a flag file and a localized country name. `data/timeline.yaml` keeps only `education` and `position` rows. `data/grants.yaml` has no `amount` key.

The only timeline rows are zcmu-bs (cn), uq-msc (au), mhh-phd (de), mhh-grad-2021 (de), muhc-2023 (ca), uhn-kite-2025 (ca), and au-dph-2026 (dk). The gap from August 2015 to December 2016 stays empty. The graduate-researcher dates stay year-only and may stack over the doctorate.

## Flags

Vendor only `cn`, `au`, `de`, `ca`, and `dk` from lipis/flag-icons tag v7.6.0, `flags/4x3/`, into `static/flags/`. `static/flags/LICENSE-flag-icons.txt` holds the MIT text. Credit line: "Flag SVGs from flag-icons v7.6.0 by Panayiotis Lipiridis, MIT licence, https://github.com/lipis/flag-icons".

## Acceptance criteria

- **AC1.** Home pages contain only the hero, intro, research directions, and four entry cards. The English intro is at most 60 words and the Chinese intro is at most 100 characters.
- **AC2.** The header nav has the five links in order, each page exists, the current page sets `aria-current="page"`, and the language toggle opens the sibling page.
- **AC3.** The timeline has year ticks and seven education or position entries, with flags and details in the HTML, and no publication or grant rows.
- **AC4.** At a narrow viewport the year track scrolls inside its own container. The page itself does not grow sideways.
- **AC5.** The build and the data files contain no currency amount and no `amount` field. The grants page lists four awarded grants.
- **AC6.** New styling uses the existing CSS variables. Dark mode still switches those variables.
- **AC7.** The English and Chinese i18n tables have the same keys, and the new pages exist in both languages.
- **AC8.** The five flag files match the published SHA-256 list, the licence file is present, and the credit line is in `README.md` and `docs/references.md`.
- **AC9.** Phone number, referee contact details, non-awarded grants, an awards list, a blog, and a CV PDF are absent.
- **AC10.** The originality check passes outside `docs/`, and the reference screenshot is not committed.
- **AC11.** The work is one pull request from `feat/site-v2` into `main`, and the MIT licence text stays in place.
