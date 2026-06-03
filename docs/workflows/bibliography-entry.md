# Bibliography Entry Workflow

Bibliography is owned by `lra-common`. Do not add canonical bibliography
entries in `Learning-Real-Analysis` or in `lra-volume-*` repositories.

## Canonical Files

The bibliography is split by target volume:

- `bibliography/volume-i-foundations.bib`
- `bibliography/volume-ii-number-systems.bib`
- `bibliography/volume-iii-analysis.bib`
- `bibliography/volume-iv-algebra.bib`
- `bibliography/volume-v-topology-geometry.bib`
- `bibliography/volume-vi-computational.bib`
- `bibliography/volume-vii-numerical-approximation.bib`
- `bibliography/volume-viii-logic-foundations.bib`
- `bibliography/general-reference.bib`

`bibliography/analysis.bib` is retained only as a legacy pointer and should not
receive new entries.

## Mobile Capture Workflow

When a source arrives from a phone photo, screenshot, title page, or OCR pass:

1. Extract candidate metadata: author, title, edition, publisher, year, ISBN,
   DOI, URL, and access date when relevant.
2. Search for existing entries:

   ```powershell
   python scripts/check_bibliography.py --find "author or title words"
   ```

3. Choose exactly one canonical home `.bib` file by curriculum volume.
4. Add the entry near its topic neighbors inside that file.
5. Use a stable CamelCase key such as `AuthorShortTitleYear`.
6. Run the duplicate check:

   ```powershell
   python scripts/check_bibliography.py
   ```

7. Build at least one affected volume, or the smallest document that cites the
   new key.
8. Commit and push `lra-common`; allow the common sync workflow to propagate
   `bibliography/` outward.

## Dedupe Rules

- Duplicate BibTeX keys are forbidden.
- Near-duplicate works should be merged before promotion to a canonical file.
- Different editions may remain as separate entries when the edition matters.
- Extractor-generated `.bib` output is candidate material only. Review it before
  adding it to a canonical file.

## Build Rule

Root files should use the split bibliography list rather than
`bibliography/analysis` alone:

```tex
\bibliography{%
  bibliography/volume-i-foundations,%
  bibliography/volume-ii-number-systems,%
  bibliography/volume-iii-analysis,%
  bibliography/volume-iv-algebra,%
  bibliography/volume-v-topology-geometry,%
  bibliography/volume-vi-computational,%
  bibliography/volume-vii-numerical-approximation,%
  bibliography/volume-viii-logic-foundations,%
  bibliography/general-reference%
}
```
