# ADR-0008: Institution names stay in English on Chinese pages

- Date: 2026-11-25
- Status: accepted

## Context

Chinese pages translate prose, role titles, degrees, and place names. Institution names are proper names that also appear in the English CV.

## Decision

Write institution names in English on Chinese pages. Translate city and country names.

## Rationale

Owner's content rule. Experience and education `org.zh` values repeat the English institution name. Grant `funder` values have no Chinese string, so `layouts/partials/loc.html` keeps the English name. `place.zh` holds the translated city and country.

## Consequences

A Chinese page shows names such as Hannover Medical School, University of Queensland, and Zhejiang Chinese Medicine University in English. The About text uses the English university name as well. Adding a `zh` organization string that is a translation would show that translation, so new rows keep the English name.
