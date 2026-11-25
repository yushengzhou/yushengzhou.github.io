# ADR-0003: Publications in one YAML file

- Date: 2026-11-25
- Status: accepted

## Context

Publication metadata has to be editable with the rest of the site. BibTeX is a common source format for academic pages.

## Decision

Keep publications in `data/publications.yaml` rather than BibTeX.

## Rationale

Hugo has no BibTeX pipeline. One YAML file can be edited in the GitHub web UI.

## Consequences

The publications page and the timeline read `data/publications.yaml`. There is no generated bibliography step. Adding a work means copying an entry in that file.
