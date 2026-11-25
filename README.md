# Academic site

Personal academic site for Yusheng Zhou. Hugo builds static HTML from Markdown and YAML. English pages are at `/`. Chinese pages are at `/zh/`.

The pages are About (the home page), Publications, and Projects. Layouts are in `layouts/`. The repository has no theme. Day-to-day edits are Markdown and YAML, then a push to `main`.

## Prerequisites

- Hugo 0.170.1
- Python 3, for `scripts/check_site.py` (the script uses the standard library only)
- Git

## Install Hugo 0.170.1

Since Hugo 0.170.0 there is one official build. The separate extended edition is gone. Archives named `hugo_extended_*` are still listed on the release, and for this version they are the same file as the standard archive (same checksum). Install `hugo_0.170.1_linux-amd64.tar.gz`, or the matching archive for another OS from the [v0.170.1 release](https://github.com/gohugoio/hugo/releases/tag/v0.170.1). Leave the `hugo_withdeploy_*` archives unused.

The Linux x86_64 archive is the one CI installs. It contains one `hugo` executable, plus `README.md` and `LICENSE`.

```bash
file="hugo_0.170.1_linux-amd64.tar.gz"
base="https://github.com/gohugoio/hugo/releases/download/v0.170.1"
curl -sfL --output-dir /tmp -O "${base}/${file}"
curl -sfL --output-dir /tmp -O "${base}/hugo_0.170.1_checksums.txt"
grep -F "${file}" /tmp/hugo_0.170.1_checksums.txt
(cd /tmp && sha256sum --check --ignore-missing hugo_0.170.1_checksums.txt)
mkdir -p "$HOME/.local/hugo"
tar -C "$HOME/.local/hugo" -xf "/tmp/${file}"
export PATH="$HOME/.local/hugo:$PATH"
hugo version
```

`hugo version` should report `v0.170.1`.

## Preview

From the repository root:

```bash
hugo server
```

The development site is at http://localhost:1313/. English is `/`. Chinese is `/zh/`. Publications are `/publications/` and `/zh/publications/`. Projects are `/projects/` and `/zh/projects/`.

## Production build

```bash
hugo --gc --minify
```

This writes `public/`. `baseURL` comes from `hugo.toml` (`https://yushengzhou.github.io/`). `public/` is gitignored.

The build also writes `public/en/index.html`. That file is a `noindex` meta-refresh to the English home page. The template is `layouts/alias.html`. The site check requires this file.

## Checks

On a pull request, `.github/workflows/hugo.yaml` job `check` installs Hugo 0.170.1, verifies the release checksum, builds the site, and runs the i18n gate and `scripts/check_site.py`. After the install above, those checks are:

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

`grep -F` looks for Hugo's warning id `i18n|MISSING_TRANSLATION` in the build log. A match fails the job. `python3 scripts/check_site.py` reads `public/` and prints `ok`. It checks the six routes above, the theme script, `hreflang`, the language toggle, publication order, placeholder badges, the `/en/` redirect, link hit areas of at least 44px, and that the built site contains no PDF. It also requires exactly 10 publications and at most 3 with `selected: true`.

On a push to `main`, and on `workflow_dispatch`, job `build` installs Hugo the same way, runs `hugo build --gc --minify --printI18nWarnings` with `--baseURL` from `actions/configure-pages`, applies the same `i18n|MISSING_TRANSLATION` gate, runs `python3 scripts/check_site.py`, and uploads `public/`. Job `deploy` publishes that upload to GitHub Pages. Pull requests do not deploy.

## Configuration

`hugo.toml`:

| Key | Value |
| --- | --- |
| `baseURL` | `https://yushengzhou.github.io/` |
| `title` | `Yusheng Zhou` |
| `defaultContentLanguage` | `en` |
| `defaultContentLanguageInSubdir` | `false` (English stays at `/`; Chinese is at `/zh/`) |
| `enableRobotsTXT` | `true` |
| `disableKinds` | `taxonomy`, `term`, `RSS` |
| `markup.goldmark.renderer.unsafe` | `false` (HTML typed into Markdown is not rendered) |
| `[params] cv` | `''` |
| `[languages.en]` | label `English`, locale `en-US`, weight `1`, `[languages.en.params] cv = ''` |
| `[languages.zh]` | label `中文`, locale `zh-Hans-CN`, weight `2`, `hasCJKLanguage = true`, `[languages.zh.params] cv = ''` |

v1 has no CV download by design.

Translations are separate files in one `content/` directory: `name.en.md` and `name.zh.md`. Shared UI strings are `i18n/en.yaml` and `i18n/zh.yaml`.

`layouts/partials/loc.html` resolves bilingual data fields. It starts from the `en` string. On a Chinese page it uses `zh` when that string is present and non-empty. A missing or empty `zh` stays English.

## Editing content

### About and research interests

`content/_index.en.md` and `content/_index.zh.md` are the home page prose: the About section and the research-interest list. Front matter `title` and `description` set the document title metadata and the meta description.

The name, role, affiliation, email, ORCID, portrait, and university profile link come from `data/profile.yaml`. Experience, education, grants, and selected publications come from the data files below.

### Publications

`data/publications.yaml` is the publication list. The source of truth is the public ORCID record <https://orcid.org/0009-0003-6736-6496>. Where a CV draft and ORCID disagree, the YAML follows ORCID.

The intro sentences are `content/publications.en.md` and `content/publications.zh.md` (`data: "publications"` in the front matter). The list itself is the YAML file. Titles stay in the language of the ORCID record. Omit `title.zh` and `venue.zh` so the English string is used. Do not add a translation that the record does not have.

To add a work, copy an existing entry and set `placeholder: false`. Keep this field order. The check reads `id`, `placeholder`, `type`, `year`, `month`, and `selected` in that order.

- `id` — stable id. Current entries use the DOI.
- `placeholder` — `true` shows the badge described under [Placeholders](#placeholders). ORCID records use `false`.
- `type` — every current entry is `journal`. The templates do not print this field.
- `year` and `month` — sort key. Newest year, then newest month, comes first. Entries that share a year and month stay in file order.
- `selected` — `true` also lists the work on the home page. The check allows at most three.
- `authors` — list of names. The exact string `Yusheng Zhou` is rendered in bold, and the check requires it on every entry.
- `title.en`, and `title.zh` when you have a Chinese title of record.
- `venue.en`, and `venue.zh` on the same terms.
- `doi` — linked as `https://doi.org/<doi>`.
- `pdf`, `preprint`, `code` — optional URLs. A link is rendered only when the field is set. No current entry sets them.

`scripts/check_site.py` expects exactly 10 entries. Adding or removing one fails that check until the expected count in the script is updated.

### Experience, education, and grants

Localized fields use `en` and `zh`, with the fallback in `loc.html`.

`data/experience.yaml` is shown in file order, current role first. Fields: `id`, `placeholder`, `role`, `org`, `place`, `when`, and optional `summary`. The Hannover role has no `summary`.

`data/education.yaml` fields: `id`, `placeholder`, `degree`, `org`, `place`, `when`.

`data/grants.yaml` is awarded grants only. Fields: `id`, `placeholder`, `when`, `role`, `title`, `funder`, `amount`. `amount` is one string for both languages (for example `$306,000`). `funder` has only an `en` string, so the English funder name is what Chinese pages show.

### Projects

`content/projects/_index.en.md` and `content/projects/_index.zh.md` are the section pages. Their Markdown is the intro line. With no project pages under the section, `layouts/list.html` adds the empty state from i18n: `No projects are listed yet.` and `尚未列出项目。`. The check requires those two sentences.

Add a project as a pair with the same slug:

- `content/projects/<slug>.en.md`
- `content/projects/<slug>.zh.md`

`archetypes/default.md` sets `draft: true` and `placeholder: false`. A draft is omitted from `hugo server` and from `hugo --gc --minify`. Set `draft: false` to publish the page. Set `placeholder: true` in the front matter to show the badge on that page.

The language toggle uses the paired translation. When a page has no translation, the toggle points at that language's home page (`/` or `/zh/`), which exists, so the toggle does not lead to a missing URL.

### Placeholders

The badge text is the i18n string `placeholder`: `PLACEHOLDER` in English and `占位` in Chinese.

- Data entries in the YAML files above show the badge when `placeholder: true`.
- A project (or other single page) shows it when front matter `placeholder: true`.
- The portrait uses a separate flag, `portrait_placeholder`, in `data/profile.yaml`.

Every publication, experience, education, and grant entry is `placeholder: false`. There are no project pages. The only remaining placeholder is the portrait.

The home page loads `static/img/portrait.svg`. `data/profile.yaml` sets `portrait: "/img/portrait.svg"`, and Hugo serves `static/` from the site root, so that SVG is the file behind the path. Replace `static/img/portrait.svg` with a photograph, or point `portrait` at another file under `static/` and put the photograph there. Set `portrait_placeholder: false` to clear the badge. While the flag is `true`, `layouts/home.html` prints the badge and an HTML comment; `false` removes both. The `alt` text stays the placeholder sentence until you edit `portrait_alt` in `i18n/en.yaml` and `i18n/zh.yaml`.

### Institution names

Keep institution names in English on Chinese pages. City and country names are translated.

`org.zh` in experience and education is the same English string as `org.en` (Aarhus University, University Health Network, the McGill institute, Hannover Medical School, University of Queensland, Zhejiang Chinese Medicine University). The Chinese About text uses `Aarhus University`. Grant funders have no `zh` key. `place.zh` is the translated city and country, for example `汉诺威, 德国`.

## Deploy

`.github/workflows/hugo.yaml` runs on a push to `main`, on every pull request, and on manual `workflow_dispatch`.

A push to `main` builds the site and deploys `public/` to GitHub Pages. A manual run does the same. A pull request runs the [checks](#checks) and does not deploy.

## One-time setup

In the repository on GitHub, open Settings, then Pages, then Build and deployment. Set Source to GitHub Actions.
