# Yusheng Zhou

Academic site with English pages at `/` and Chinese pages at `/zh/`, built with Hugo.

## Install

Hugo 0.170.1. Since 0.170.0 there is one official build, and the separate extended edition is gone. An archive named `hugo_extended_*` that shares the checksum of the standard archive is an alias of that file, not a second edition.

The Linux x86_64 archive is the one CI installs. It contains one `hugo` executable, plus `README.md` and `LICENSE`.

```bash
file="hugo_0.170.1_linux-amd64.tar.gz"
base="https://github.com/gohugoio/hugo/releases/download/v0.170.1"
curl -sfL --output-dir /tmp -O "${base}/${file}"
curl -sfL --output-dir /tmp -O "${base}/hugo_0.170.1_checksums.txt"
grep -F "${file}" /tmp/hugo_0.170.1_checksums.txt
(cd /tmp && sha256sum --check --ignore-missing hugo_0.170.1_checksums.txt)
mkdir -p "${HOME}/.local/hugo"
tar -C "${HOME}/.local/hugo" -xf "/tmp/${file}"
export PATH="${HOME}/.local/hugo:${PATH}"
hugo version
```

`hugo version` reports `v0.170.1`. For another OS, use the matching `hugo_0.170.1_*` archive from the [v0.170.1 release](https://github.com/gohugoio/hugo/releases/tag/v0.170.1).

## Usage

```bash
hugo server
```

Hugo prints a local URL. English is `/`, Chinese is `/zh/`. Timeline is `/timeline/` and `/zh/timeline/`. Publications are `/publications/`. Projects are `/projects/`.

```bash
hugo --gc --minify
```

This writes `public/`. `baseURL` in `hugo.toml` is `https://yushengzhou.github.io/`. The build also writes `public/en/index.html`, a `noindex` refresh to the English home page (`layouts/alias.html`). `public/` is gitignored.

`defaultContentLanguage` is `en` and `defaultContentLanguageInSubdir` is `false`, so Chinese stays under `/zh/`. `markup.goldmark.renderer.unsafe` is `false`, so HTML typed into Markdown is not rendered. v1 has no CV download by design. `[params] cv`, `[languages.en.params] cv`, and `[languages.zh.params] cv` are empty.

### Editing content

The address on the home page is the `email` field in `data/profile.yaml`. The ORCID iD is the `orcid` field in that same file. `credentials` (`MPH, PhD`) follows the name in the home-page heading and the home-page `<title>`, in both languages. `taglines` (three items, each `en` and `zh`) are typed in turn under the name; without JavaScript or with reduced motion the first one shows still (ADR-0018). Do not invent a second address in the Markdown.

`content/_index.en.md` and `content/_index.zh.md` are the About text and the research-interest list. `title` and `description` in the front matter are the page title metadata and the meta description.

`layouts/partials/loc.html` prints the `en` string, then replaces it with `zh` when that string is present. A missing or empty `zh` stays English. Institution names stay English on Chinese pages: set `org.zh` to the same English name, or omit `zh`. Grant `funder` values have no `zh` key. City and country in `place` are translated. Positions and education follow the CV. Publications follow the ORCID record named in `data/profile.yaml`. Where the CV and that record disagree, the record wins.

`data/publications.yaml` is the publication list. The intro lines are `content/publications.en.md` and `content/publications.zh.md`. To add a work, copy an entry, set `placeholder: false`, and keep this field order: `id`, `placeholder`, `type`, `year`, `month`, `selected`, then `authors`, `title`, `venue`, and `doi`. Optional `pdf`, `preprint`, and `code` render as links when set. Omit `title.zh` and `venue.zh` unless that Chinese string is the title of record. Newest `year`, then `month`, is listed first. `selected: true` also lists the work on the home page. The exact author string `Yusheng Zhou` is shown in bold. The site check expects 10 entries and at most 3 with `selected: true`.

`data/experience.yaml` fields: `id`, `placeholder`, `role`, `org`, `place`, `when`, optional `summary`. `data/education.yaml` fields: `id`, `placeholder`, `degree`, `org`, `place`, `when`. `data/grants.yaml` is awarded grants only. Fields: `id`, `placeholder`, `when`, `role`, `title`, `funder`. Grant amounts are not published, so there is no `amount` field (ADR-0015). There is no awards list in this version.

`data/timeline.yaml` only points at those records. It does not copy titles, authors, or organizations. Each row has:

- `id` — the id in the source file
- `type` — `education`, `position`, `publication`, or `milestone`
- `from` — `education`, `experience`, `publications`, or `grants`
- `start` — `YYYY` or `YYYY-MM`
- `end` — the same form, or `null` when the role is still open
- `source` — `cv` for positions, education, and grants; `orcid` for publications

Use `type` and `from` as a pair: `education` with `education`, `position` with `experience`, `publication` with `publications`, `milestone` with `grants`. The visible wording comes from the source record. `start` and `end` are the sort dates, and `start` is the `datetime` value. The list is newest `start` first. An empty `end` sorts ahead of a closed `end` with the same `start`. A remaining tie follows `id` in descending order. The Aarhus row keeps the CV role and dates already stored on that experience record, with `end: null`.

To add a timeline entry, add the record to the source file if it is not there, then add one row here. The site check expects at least 21 rows.

The full timeline starts with a flag strip: a horizontal year axis with one flag per place (ADR-0017). `data/stays.yaml` lists the stays. Each row has `id`, `flag` (a file name in `static/img/flags/`), `ratio` (flag width / height), `region` (`en` and `zh`, used in the flag's alt text), and `ids` (timeline ids). Dates come from those timeline rows and the city from the first record's `place`. To add a place, add its records and timeline rows, copy the flag SVG to `static/img/flags/`, and add a row here. Flags are public-domain SVGs from the `region-flags` npm package 1.1.0.

The home page, after the About prose, shows selected publications, then links to all publications and to the full timeline. It has no timeline preview and no grants block (ADR-0014). The full page is `/timeline/` and `/zh/timeline/` and lists every row, including all 10 publications and the 4 awarded grants as milestones. Filter chips (All, Education, Position, Publication, Milestone) are on the full page only. They are buttons, and the page's script hides other types and sets `aria-pressed`. With JavaScript off, every item is in the page and none are hidden. Position summaries, publication authors, and grant role sit in closed `details`.

`content/projects/_index.en.md` and `content/projects/_index.zh.md` are the projects section. With no project pages, the page shows `No projects are listed yet.` and `尚未列出项目。`. Add `content/projects/<slug>.en.md` and `content/projects/<slug>.zh.md`. `archetypes/default.md` sets `draft: true`. A draft is omitted from `hugo server` and from `hugo --gc --minify`. Set `draft: false` to publish. If a page has no translation, the language toggle points at that language's home page.

A `placeholder: true` flag on a data row or a page shows the badge `PLACEHOLDER` / `占位`. No placeholders are left. The portrait is `static/img/portrait.jpg`, a 190 × 190 pixel-art avatar set by `portrait` in `data/profile.yaml`, rendered with `image-rendering: pixelated`. To change it, replace that file or point `portrait` at another file under `static/`, and update `portrait_alt` in `i18n/en.yaml` and `i18n/zh.yaml`.

## Development

Python 3 is required. `scripts/check_site.py` uses the standard library only.

On a pull request, `.github/workflows/hugo.yaml` installs Hugo 0.170.1, checks the release checksum, then runs:

```bash
hugo build --gc --minify --baseURL "https://yushengzhou.github.io/"

out=$(hugo --printI18nWarnings --gc --minify --baseURL "https://yushengzhou.github.io/" 2>&1)
printf '%s\n' "$out"
if printf '%s\n' "$out" | grep -F 'i18n|MISSING_TRANSLATION'; then
  echo "i18n warnings present"
  exit 1
fi

python3 scripts/check_site.py
```

`grep -F` looks for Hugo's warning id `i18n|MISSING_TRANSLATION`. A match fails the job. `python3 scripts/check_site.py` prints `ok` when the built pages, theme, `hreflang`, language toggle, publication order, placeholders, timeline, and `/en/` redirect match the source. There is no separate lint command.

On a push to `main`, and on `workflow_dispatch`, job `build` installs Hugo the same way, runs `hugo build --gc --minify --printI18nWarnings` with `--baseURL` from `actions/configure-pages`, applies the same warning gate, runs `python3 scripts/check_site.py`, and uploads `public/`. Job `deploy` publishes that upload. Pull requests do not deploy.

Recorded decisions are indexed in `docs/decisions.md`.

## Deploy

A push to `main` builds the site and deploys `public/` to GitHub Pages. A manual run of `.github/workflows/hugo.yaml` does the same.

In the repository on GitHub, open Settings, then Pages, then Build and deployment. Set Source to GitHub Actions.

## License

This repository has no `LICENSE` file. No license decision is on record.
