# ADR-0002: Translations by file name

- Date: 2026-11-25
- Status: accepted

## Context

The site is bilingual. Each page needs an English URL and a Chinese URL, and the language control has to land on a page that exists.

## Decision

Translate by file name (`.en.md` / `.zh.md`). Serve English at `/` and Chinese at `/zh/`. The language toggle always has a real target.

## Rationale

`defaultContentLanguage` is `en` and `defaultContentLanguageInSubdir` is `false`, so English stays at the root and Chinese is under `/zh/`. `layouts/partials/href.html` links to the translated page when it exists, and otherwise to that language's home page.

## Consequences

Content files are pairs such as `content/_index.en.md` and `content/_index.zh.md`. Shared UI strings are `i18n/en.yaml` and `i18n/zh.yaml`. A page that exists in only one language still offers a working toggle, pointed at the other language's home page.
