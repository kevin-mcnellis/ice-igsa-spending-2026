# What USAspending.gov Doesn’t Show About ICE’s Detention Spending

Data, code, and checks behind [Kevin McNellis’s article](https://www.kevinmcnellis.com/posts/ICE_IGSA/), published September 27, 2026.

The post examines what USAspending.gov data and ICE's detention center data can show about ICE detention spending and intergovernmental service agreements (IGSAs). The main USAspending.gov File B–File C comparison uses five original archives: three account-level File B downloads and two award-breakdown File C downloads. 

## What the analysis found

- In ICE accounts `070-0540` and `070-0545`, the object class `25.4` comparison shows $5.91 billion in File B net obligations and $3.14 billion in File C net transaction obligations from February 2025 to July 2026. This difference is a reported accounting comparison. It does not identify IGSA payments or reconcile individual File B dollars to awards.
- Ten private detention contractors received $3.08 billion in class `25.4` File C obligations. Three government unique entity identfiers (UEIs) belonging to two local governments have a signed total of −$28,520. These are recipient-level reported obligations, not payments to detention facilities or a count of independent parent companies.
- On ICE’s July 9, 2026 roster, 168 of 208 observed facilities carried an `IGSA`, `DIGSA`, or `USMS IGA` label. They accounted for 57% of summed reported fiscal-year-to-date average daily population, which is not a July 9 head count.
- A reviewed award-description name screen matched 21 of 49 facilities in its federal/contract group and five of 224 in its IGSA group. The associated distinct-award class `25.4` amounts are about $2.23 billion and $96 million. A name match does not allocate an award amount to a facility or establish an agreement payment.
- Two direct CoreCivic orders name Torrance and Cibola, the facilities in that screen whose observed labels were solely in the IGSA group. Their selected class `25.4` obligations total $17.47 million. The direct orders and the counties’ agreements are different records.
- The article also discusses a roughly $4.8 billion File B-minus-File C difference across four object classes in ICE’s Operations and Support account. That subtraction is not a list of unreported awards or an estimate of IGSA spending.

## What this repository does not show

- Total payments under IGSAs, or a payment amount for any facility.
- Which individual account-level obligations, if any, are IGSA payments.
- A complete independent-parent-company count from direct-recipient UEIs.
- Facility ownership, operation, or exclusive award allocation from a roster type or description match.

## Reproduce the results

Requirements: Python 3.12.12 and [uv](https://docs.astral.sh/uv/). The included `pyproject.toml` and `uv.lock` pin the project’s Python packages.

```bash
uv run --frozen python3 run_all.py
```

The command verifies the source files recorded in `data/manifest.csv`, fetches missing frozen USAspending archives by their registered URLs (or, if USAspending no longer serves them, from this repository's `usaspending-archives-2026-09` release) and checks their SHA-256 fingerprints, rebuilds Chart 1, Chart 2, the facility name screen, and Figure B, and checks their outputs. It verifies the selected Figure A and gap-chart assets against reviewed hashes; it does not redraw them. USAspending data can be revised after a download; a newly requested file with the same filters is not automatically the saved vintage.

### Live article images

On September 28, a fresh HTTP check found that the live article linked the bundled Figure A, Figure B, and gap-chart PNGs byte for byte. The [dated image verification](audit/live_asset_verification.json) records the three live URLs and SHA-256 hashes. Earlier [Figure A](audit/figure_a_igsa168_review.json) and [gap-chart](audit/gap_chart_final_copy.json) review receipts describe a prior publication stage; they do not describe the live page at this check. The published article can change after this dated observation.

## Where each number comes from

`audit/claim_audit.json` records the published text target, each reviewed claim, its evidence, and its PASS, WARN, FAIL, or `ACCEPTED_BY_AUTHOR` status. The separate [author-decision record](audit/author_decisions.json) identifies wording choices that Kevin accepted with reasons and evidence; acceptance is not a factual PASS finding. `audit/claim_audit.md` is the readable rendering.

The following key-figures table is generated from the audit JSON, including its cited output row or source page. No value in the table is hand copied into this template.

| Figure | Value in article | Output or source | Row/page | Claim | Status |
| --- | --- | --- | --- | --- | --- |
| File B class 25.4 obligations | $5.91 billion | outputs/chart_1/verification.json, [claim audit](audit/claim_audit.md) | analysis.bar_totals, fresh independent check | P30.S2.C1 | PASS |
| File C class 25.4 obligations | $3.14 billion | outputs/chart_1/verification.json, [claim audit](audit/claim_audit.md) | analysis.bar_totals, fresh independent check | P30.S2.C2 | PASS |
| File B minus File C comparison | $2.77 billion | outputs/chart_1/verification.json, [claim audit](audit/claim_audit.md) | analysis.checks.aggregate_difference, fresh independent check | P30.S3 | PASS |
| Ten selected direct-recipient UEIs | $3,080,063,270 | outputs/chart_2/recipient_type_totals.csv, [claim audit](audit/claim_audit.md), outputs/chart_2/recipient_totals.csv | Selected private detention contractors, fresh independent check, ten substantive UEIs; two $250 minimum orders excluded | P33.S1.C2 | PASS |
| Federal/contract group name-screen awards | $2,229,581,023 | audit/source_snapshot/facility_name_screen_statistics_check.json, [claim audit](audit/claim_audit.md) | actual.federal_contract_25_4_amount, fresh read-only rerun | P47.S1.C2 | PASS |
| IGSA group name-screen awards | $96,196,138.33 | audit/source_snapshot/facility_name_screen_statistics_check.json, [claim audit](audit/claim_audit.md) | actual.iga_25_4_amount, fresh read-only rerun | P48.S1.C2 | PASS |
| Solely-IGSA named direct orders | $17,465,361.06 | audit/source_snapshot/facility_name_screen_statistics_check.json, [claim audit](audit/claim_audit.md) | actual.solely_iga_25_4_amount, fresh read-only rerun | P49.S1.C3 | PASS |

Overall claim audit status: **WARN** (191 PASS, 123 WARN, 0 FAIL, 11 author acceptances). Author acceptance is a wording decision, not factual verification. See [the complete claim audit](audit/claim_audit.md) and [author decisions](audit/author_decisions.json) for more information.

## Data sources

| Source | Role | Provenance |
| --- | --- | --- |
| USAspending.gov Custom Account Data | Frozen File B account totals and File C award-breakdown records for the stated accounts and reporting periods | Exact archives, retrieval dates, sizes, and hashes in `data/manifest.csv` |
| ICE detention statistics | Observed roster types and reported average daily population | Official workbook URL and original SHA-256 in `METHODOLOGY.md`; public-safe derived panel and lineage in `data/small/` |
| ICE FOIA Library | Torrance and Cibola agreement documents | Official PDF links and saved-source hashes in `METHODOLOGY.md`; original scans and page-review receipts are not bundled |
| USAspending.gov award pages and SAM.gov notice | Separate contract, task-order, and notice evidence | Four reviewed award-detail API snapshots are in `data/small/facility_name_screen/source_api/`; other cited pages and the SAM notice are linked in `METHODOLOGY.md`, but their acquisition receipts are not bundled |
| U.S. Census Bureau Gazetteer | Reference geography used by the original chart pipeline | Two frozen public ZIPs in `data/reference/` with official URLs and hashes in `data/manifest.csv` |
| Laws and oversight reports | Legal text and agency findings cited in the article | Official links and page-specific citations in `METHODOLOGY.md` and `audit/`; original documents are not bundled |
| News reports | Reported local context | External links in the methodology and audit; article text is not copied |

## Repository layout

```text
run_all.py        fetch or verify inputs, rebuild released outputs, and run checks
run_*.py          original chart and facility-screen producer entrypoints
scripts/          original calculation, figure, and screen modules
src/              release orchestration and package checks
tests/            behavior and source-integrity tests
data/manifest.csv source URLs, retrieval dates, sizes, hashes, and roles
data/fetch/       download and verify the large frozen archives
data/small/       public-safe source and review inputs, with derivation receipts
outputs/          rebuilt tables and figures plus hash-verified live images
audit/            claim audit, source receipts, and verification results
METHODOLOGY.md    methods, populations, formulas, and limits
```

`METHODOLOGY.md` explains the File B calculation, File C selection, roster groups, name-screen rules, and unresolved reporting limits. An award-to-facility relationship does not make an award amount additive across facilities.

## How this was made

Kevin McNellis directed the research, reviewed the results, and made the final decisions on methods and wording. Anthropic’s Claude and OpenAI’s Codex assisted with source review, code, checks, and editorial suggestions. Kevin is responsible for the analysis and any errors.

## Corrections and contact

The analysis has stated source and interpretation limits. Please send corrections through [kevinmcnellis.com](https://www.kevinmcnellis.com/contact.html) or open an issue in this repository.

## License

- **Original code** in `run_all.py`, `run.py`, `run_*.py`, `scripts/`, `src/`, `tests/`, and `data/fetch/` is licensed under the [MIT License](LICENSE), copyright © 2026 Kevin McNellis.
- **Original data, outputs, and documentation** in `outputs/`, `audit/`, `data/manifest.csv`, `METHODOLOGY.md`, and this README are licensed under [CC BY 4.0](LICENSE-DATA). Attribute Kevin McNellis, link to the license and source, and identify changes.
- **Third-party content** in `data/small/` and `data/reference/`, including public-safe derivatives, receives neither license grant from Kevin. Original publishers and source URLs, when available, are recorded in `data/manifest.csv` or `METHODOLOGY.md`; check their applicable rights before reuse.

## Citation

McNellis, Kevin. 2026. “What USAspending.gov Doesn’t Show About ICE’s Detention Spending.” September 27. [Article](https://www.kevinmcnellis.com/posts/ICE_IGSA/). Data and code: https://github.com/kevin-mcnellis/ice-igsa-spending-2026.
