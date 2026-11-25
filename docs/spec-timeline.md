# Addendum: academic timeline

**Extends:** the v1 site specification (PR #1). **Target branch:** `feat/site-v1` at `9f89d73` (PR #1, approved, not merged). **Reference studied (ideas only):** https://www.lizheng.ai/ (fetched 2026-11-25). Owner decisions recorded below (2026-11-25 23:40 Europe/Copenhagen); ready to implement.

## Goal

Add an original, accessible vertical timeline of real education, positions, publications, and confirmed milestones so visitors can scan the career chronologically in English or Chinese, in light or dark mode, on a phone, without copying the lizheng.ai design or shipping private or unsuccessful-grant data.

## Features

1. **Full timeline page.** Renders one semantic `<ol>` of items (type, dates in `<time datetime>`, title, organization/venue, optional one-line summary, optional link). **In:** composed site data (below). **Out:** `/timeline/` and `/zh/timeline/`, listed in the existing header nav (`nav_timeline` i18n). Language toggle uses the same `href.html` sibling-or-home rule as other pages.
2. **Homepage preview.** After About / research interests, a compact timeline of **education + positions only**, same visual language as the full page, with a “Full timeline” link. **Replace** the standalone Experience and Education homepage blocks so the same facts are not listed twice. Keep Awarded grants and Selected publications as they are.
3. **Chronological order.** Sort by machine `start` descending, then `end` descending; ongoing roles (`end` empty) sort first within the same `start`. This matches the current CV and `data/experience.yaml` (current role first) and is deliberately not the reference site’s left-to-right early-to-late rail.
4. **Type filters (progressive enhancement).** On the full page only, optional chips (All / Education / Position / Publication / Milestone) hide or show items with a few lines of vanilla JS. **Without JS, every item is visible.** Chips are buttons in a labelled group, `aria-pressed`, 44px targets; type is also a text label on each item (colour is not the only cue).
5. **Progressive detail.** Position summaries and extra publication/grant detail sit in native `<details>` (closed by default). No custom fold animation required. `prefers-reduced-motion: reduce` must disable any motion if any is added later.
6. **Current role.** The open-ended Aarhus position is labelled with the existing “Present” / “至今” copy, using current typography and `--muted` / `--text`. Not a glowing node or a special brand mark.

## Out of scope

Teaching, presentations, professional memberships, peer review, **grants under review**, unsuccessful grants, referees, the phone number printed on the CV, a CV PDF, BibTeX, new NPM/Hugo-module dependencies, dark-mode or i18n rewrites, and any copy of lizheng.ai layout, CSS, JS, typography, assets, names, or branding. Do not invent Chinese publication titles (follow `docs/decisions.md` §4 and §8).

## Stack / approach

Keep Hugo 0.170.1. New work: `content/timeline.en.md` + `content/timeline.zh.md`, a `layouts/partials/timeline.html` used by the new page and the homepage, CSS in `assets/css/main.css` using **existing variables only** (`--bg`, `--surface`, `--text`, `--muted`, `--link`, `--line`, `--badge-bg`, `--badge-text`, `--focus`, `--header`), and optional vanilla JS for filters only. Update `layouts/partials/header.html` and `i18n/en.yaml` + `i18n/zh.yaml`. Extend `scripts/check_site.py` and CI (already runs the checker on pull requests). No theme, no new fonts, no new packages.

## Data model

Do **not** duplicate bibliographic fields. A small `data/timeline.yaml` **composes** existing files and only adds dates plus milestones that are not already stored:

```yaml
# Each row points at an existing record, or is a milestone with its own fields.
- id: au-dph-2026
  type: position          # education | position | publication | milestone
  from: experience        # experience | education | publications | grants
  start: "2026-11"        # ISO year or year-month; no finer date than the source
  end: null               # null = ongoing
  source: cv              # cv | orcid | cv+orcid
```

Templates read title/role/org/place/summary/DOI from `data/experience.yaml`, `data/education.yaml`, `data/publications.yaml`, or `data/grants.yaml` by `id`. Add `start`/`end` either on those records or only in `timeline.yaml`. Publications on the **full** page: all 10 ORCID works, links to the existing publications page / DOI. Homepage preview omits publications (selected pubs already follow). Awarded grants (already in `data/grants.yaml`) appear on the full page as `type: milestone` with `source: cv`.

**Source-of-truth (same as PR #1):** positions and education follow the **CV**; publications follow **ORCID**. ORCID has **no education** and omits the Hannover Graduate Researcher role. ORCID lists the Aarhus job twice (open-ended “Postdoc Researcher” and “VIP, Postdoc” ending 2028-10-31); the site keeps the CV wording (“Postdoctoral Researcher”, “Nov 2026 – Present”) and does not show the VIP title or contract end unless the owner says otherwise. Institution names stay English on ZH pages; cities/countries and UI strings are translated; missing ZH fields fall back through `loc.html`.

**Exclude always:** the phone number printed on the CV; the three referees and their emails; both unsuccessful grants; both grants under review.

### Real data already available

From the CV text used for v1, and already encoded in the PR data files unless noted:

- Positions: Aarhus University, Dept. of Public Health, Postdoctoral Researcher, Nov 2026 – Present; KITE / Toronto Rehab / UHN, Post-Doctoral Fellow, Oct 2025 – Oct 2026; RI-MUHC, Post-Doctoral Fellow, Jan 2023 – Oct 2025; Hannover Medical School, Graduate Researcher, 2021 – 2022 (no description in the CV; do not invent one).
- Education: Ph.D. Public Health, Hannover Medical School, Dec 2016 – Oct 2021; M.Sc. Public Health, University of Queensland, Sep 2013 – Jul 2015; B.S. Chinese Medicine, Zhejiang Chinese Medicine University, Sep 2008 – Jul 2013.
- Awarded grants (co-applicant only): four records already in `data/grants.yaml` (CIHR 2025–26 $306,000; NWHRI 2024–26 $150,000; CPHO Catalyst 2023–25 $125,000; CIHR 2021–23 $182,836).
- Publications: 10 journal articles in `data/publications.yaml`, from public ORCID `0009-0003-6736-6496` (record last modified 2026-11-24 02:34 Europe/Copenhagen).

From ORCID employments (cross-check only): Aarhus, UHN/Toronto Rehab, and McGill/MUHC agree in substance with the CV; education list is empty; no fundings.

### Decisions (owner, 2026-11-25 23:40 Europe/Copenhagen)

1. Vertical, original timeline approved (not the reference's horizontal rail).
2. **No awards** in this version. Do not add the CV awards table to data or the timeline.
3. Defaults approved: full page shows all 10 ORCID publications + the 4 awarded grants as milestones; homepage preview shows education + positions only.
4. Aarhus uses the CV wording: "Postdoctoral Researcher, Nov 2026 – Present" (no ORCID "VIP, Postdoc" title or 2028 end date).

Still excluded: phone, referees, unsuccessful grants, grants under review.

The v1 site still uses a placeholder portrait only; that does not block the timeline. Data for education, positions, publications, and awarded grants is **not** placeholder.

## Where it lives

- Full page: `https://yushengzhou.github.io/timeline/` and `https://yushengzhou.github.io/zh/timeline/`.
- Homepage section: after the about prose, before awarded grants.
- Nav (all pages): About, **Timeline**, Publications, Projects.

## Visual / a11y / mobile

Fit the current design (v1 preview screenshots): narrow `42rem` column, system font, stacked blocks, 1px `--line` separators, 44px controls, Light/Dark/System already in the header. The timeline is a **vertical** list with a simple left rule (or no rule—just the existing `.item` borders). Dates stack **above** the body on small screens (do not keep a squeezed side column at 375px). Use existing dark tokens; no flash (theme script stays in `head`). Contrast and focus rings follow current `--focus` rules. Keyboard: filters, details, and links are reachable in order.

## Acceptance criteria

- **AC1.** Given a production build of `feat/site-v1` plus this addendum, when a reviewer opens `/timeline/` and `/zh/timeline/`, then both pages show the composed real items in reverse-chronological order, in the current typography and CSS variables, in both light and dark, with the language toggle staying on the sibling page.
- **AC2.** Given a 375px-wide viewport, when the homepage and timeline page are viewed, then the timeline is single-column, controls are ≥44px, and name/email remain above the fold on the homepage (same rule as v1).
- **AC3.** Given JS disabled, when the full timeline is loaded, then every in-scope item is visible and readable; given JS enabled, when a type chip is pressed, then only that type remains visible and `aria-pressed` updates.
- **AC4.** Given the rendered HTML, when inspected, then the timeline is an `<ol>`, dates use `<time datetime>`, a keyboard-only pass works, and `prefers-reduced-motion: reduce` introduces no required motion.
- **AC5.** Given the built site and data files, when searched, then they contain no phone number, no referee names or emails, no unsuccessful-grant titles, and no under-review grant titles; every visible timeline item is traceable to the CV or ORCID as specified; no placeholder facts are invented.
- **AC6.** Given a case-insensitive search for known academic-theme names and the reference site's names on the implementation (excluding `docs/`, which is this record), when it runs, then it is empty; layouts/CSS/JS for the timeline were written in this repo, not copied from the reference.
- **AC7.** Given the existing CI commands, when they run on the PR, then they stay green after the new routes and i18n keys are included.

## Commands

```bash
hugo version    # v0.170.1
hugo server     # /timeline/ and /zh/timeline/; homepage preview
hugo --gc --minify && test -f public/timeline/index.html && test -f public/zh/timeline/index.html
hugo --printI18nWarnings 2>&1 | grep -F 'i18n|MISSING_TRANSLATION' && exit 1 || true
python3 scripts/check_site.py
```

Extend `scripts/check_site.py` for the new routes, nav link, i18n keys, hreflang, no-JS completeness, exclusion strings (phone, referees, unsuccessful / under-review grant titles), and the originality search.

## Risks

- Visual or interaction copying of lizheng.ai (horizontal node rail; a folded “later / original records” list). See `docs/references.md`. The career-rail motif is distinctive enough to flag as a real copying risk if imitated.
- Data drift if publication fields are copied into `timeline.yaml` instead of referenced.
- Leaking under-review / unsuccessful grants or the phone and referees.
- Remaining CV vs ORCID date/title disagreements (documented in PR #1); resolve only with the owner, do not silently “fix.”
- Filters implemented as JS-only content (fails AC3).
