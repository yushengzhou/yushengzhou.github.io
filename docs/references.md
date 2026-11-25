# Timeline references (borrowing record)

Studied 2026-11-25, read-only, from https://www.lizheng.ai/ (also `/en` and `/about`). No code, CSS, assets, or text from that site is to be reused in this repository.

## License / copyright

The public site states a copyright line only: **“© 2026 孙煜征 · Yuzheng Sun”** (English homepage: **“© 2026 Yuzheng Sun · 孙煜征”**), in the footer of the homepage, `/en`, and `/about`. No Creative Commons licence, no MIT/Apache grant, and no trademark statement was found on those pages. A separate GitHub repository, https://github.com/sunyuzheng/lizheng-open-context, exists and may carry its own licence; that does **not** license the look, CSS, JavaScript, or assets of www.lizheng.ai. Treat the website as ordinary copyrighted work. Borrow ideas and interaction patterns only.

## Risk flag

**Yes — two patterns on the reference are distinctive enough that imitating them would be a real copying risk, not a generic timeline.**

1. **Career path (`lz-career` / `lz-cpath`).** A compact horizontal (CSS grid) rail of employer/institution nodes joined by a connector line and dots, with a visually emphasized “now” node, optional Latin-name typography, and phrase-chip role stacks. On viewports ≤860px the connector is hidden and the items stack. There is no filter, no hover behaviour, and no expand/collapse on this block; it is a static path. Do not reproduce this rail, node treatment, typography pairing, motion, class names, or copy.
2. **“Public judgments” list (`#judgment`).** A vertical dated list of public predictions with a three-part editorial structure (claim, a later “what happened” coda, and an “original records” sidebar), featured/badge states, and a “show more” control that reveals folded entries (`lz-expand` / `calls-more`). This is a distinctive editorial device, and it is the wrong content type for an academic CV timeline. Do not reuse that structure, labels, or interaction.

The rest of the homepage (ask widget, guest lists, city/window effects, IntersectionObserver-driven sections, Geist typography, brand colour, Chinese slogans) is also off-limits.

The reference has **no dark mode** and no `color-scheme` / theme toggle. This site already does; the timeline must use the existing variables, not the reference palette.

Generic ideas that are safe to borrow are listed below. The implementation must remain a vertical, document-like list that fits the current 42rem, system-font, `--line`-bordered layout.

## Borrowing record

| Idea borrowed | Source | How ours differs |
| --- | --- | --- |
| A scannable career overview of successive roles and education, with the current step clearly marked | https://www.lizheng.ai/ career section (“履历” / EN “Path”) | Vertical reverse-chronological `<ol>` in the existing academic layout; “Present”/“至今” is plain text, not a glowing end-node on a horizontal rail; many more item types (publications, grants) than a six-step logo path; no phrase-chip typography, no Latin-name font split, no connector-and-dot graphic. |
| Letting a long chronological list be scanned, with some detail available on demand | https://www.lizheng.ai/ judgments list (dated entries; some start folded; a show-more control) | Native `<details>` on each item, all items in the DOM without JS; optional type **filters** (education / position / publication / milestone) rather than hiding a tail of the same editorial list; no “later / original records” coda, no featured-claim layout, no custom expand button pattern. |
| Chronology as a first-class way to read a person’s work | Same site, taken as a general UX idea | Academic data only (CV + ORCID); reverse chronological to match the existing CV and `data/experience.yaml`; EN/ZH and light/dark, which the reference career block does not provide. |

Ideas only: no snippets, tokens, measurements, or assets from the source are recorded here for reuse.

## Must-not-copy

Do not copy, translate, restyle, or re-implement from www.lizheng.ai (or its `/en`, `/about`, CSS, or JS bundles):

- Source, HTML structure, CSS, JavaScript, fonts (including Geist), icons, photographs, OG images, or any asset.
- Names and branding: 立正, 课代表立正, 孙煜征, Yuzheng Sun, 超线性学院, Superlinear Academy, Statsig, and the reference site’s slogans.
- The horizontal career rail (node, connector line, “now” node treatment, phrase chips, Latin-name style).
- The judgments format (date + claim + “后来” aftermath + original-records sidebar, featured/fold/show-more).
- Class or hook names (`lz-career`, `lz-cpath`, `lz-expand`, `calls-list`, `calls-more`, and other `lz-` prefixes).
- Colour palette, grid breakpoints, and motion (including any scroll- or observer-driven effects used elsewhere on that site).

Also still forbidden, from the parent spec: al-folio, academicpages / Minimal Mistakes, Hugo Blox / Wowchemy / Academic, Hugo Academia, and any other third-party academic theme.

Timeline CSS and any filter script must be original work in this repository.
