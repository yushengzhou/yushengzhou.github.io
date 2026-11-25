# ADR-0007: Deploy with GitHub Actions

- Date: 2026-11-25
- Status: accepted

## Context

The site is a GitHub Pages project. Pages can build from a branch or from an Actions artifact.

## Decision

GitHub Actions builds and deploys on push to `main`. The GitHub Pages source is GitHub Actions.

## Rationale

`.github/workflows/hugo.yaml` deploys on push to `main` and on manual `workflow_dispatch`. Pull requests run the build, the `i18n|MISSING_TRANSLATION` check, and `scripts/check_site.py`, and they do not deploy. One-time repository setup is Settings > Pages > Source = GitHub Actions.

## Consequences

The workflow installs Hugo 0.170.1, checks the release checksum, and uploads `public/` only from the non-pull-request jobs. `pages: write` and `id-token: write` are granted on the build and deploy jobs, not on the pull-request check.
