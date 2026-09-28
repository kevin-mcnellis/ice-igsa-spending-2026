> Release copy: references to other repository documents are shown as paths, not links. Those documents and the two private-worktree references are not bundled here. The original governed rulebook remains in the canonical repository.

# ICE Detention Facility Analysis Semantic Rulebook

## Scope

- Project or lane: DDP-based ICE detention roster expansion and geography,
  with Post, contract, USAspending, and dated FOIA evidence as secondary lanes.
- Intended recurring questions: how the number and geographic distribution of
  observed facilities changed after the January 6, 2025 baseline; which
  facilities first appeared, disappeared, or reappeared; and how reported ADP,
  guaranteed minimum, detailed type, composition, and ALOS changed within
  source and comparability limits.
- Out of scope for the governed core: unsupported opening/closure claims,
  conditions ratings, legal conclusions, and contractor-wide allocation.
- Controlling roster artifacts: `data/manifest.csv`,
  `metadata/detention_roster_snapshot_inventory.csv`, exact DDP-preserved raw
  rows, and reviewed longitudinal identity/support decisions. Post, FOIA,
  contract, and USAspending sources control only their separately labeled
  supporting lanes.
- Current-status routing updated: 2026-09-13. Individual definition and evidence
  dates below remain as recorded; this is not a new full semantic audit.
- Readiness: **Longitudinal identity and Task 4 metric semantics are governed;
  the Nassau correction and corrected Task 4 outputs are built, verified, and
  reapproved. Reviewed geography and the three-date map pipeline are implemented,
  with their source-specific provisional qualifications retained.**
  Workbook schemas, source-row extraction, exact-identity grouping, curated
  review decisions, source dates, candidate tiers, ADP derivation, panel
  grains, bounded contract transactions, candidate award archives, recipient
  relationships, and direct facility links are governed. File C field-level
  time semantics are governed here and are now implemented: the generated
  table carries per-field `toa_additivity` and `gross_outlay_additivity`
  columns in place of the superseded row-level `additivity_status`.
  Historical operator attribution, award terms, financial coverage, and
  publication claims retain their stated review limits. Clark County (ID)'s
  reviewed provisional location keeps its source-specific qualification below.
  Kevin reapproved the corrected
  eligible-entity and event totals on August 27, 2026.

The article is published at
`https://www.kevinmcnellis.com/posts/ice_facilities/`; the website repository's
`posts/ice_facilities/index.qmd` controls public wording. The local
`z_for_publication/index.qmd` is an earlier staging version. Publication and
delivery verification do not reapprove the article's claims or change the
semantic rules below. The active File C lane has a separately approved
recipient-only release using the two 2025/2029 accounts. Facility assignment is
deferred, and its 213 financial-review units are not a prerequisite to recipient
rankings. Use the current lane contract (unbundled private worktree)
and recipient report (unbundled private worktree)
for that unintegrated layer; do not infer facility or IGSA payments from the
recipient totals or from a facility-type label.

## July 9 graphic: expanded c3 presentation definition

Kevin approved this scoped amendment on September 9, 2026 in task
`01a07489-03f7-78e3-a2b3-13a85505bb4f`; see the
approved decision and verification plan (`docs/expansion_category_update_20260909.md`).
`c3 — Trump expansion facilities` is a reviewed presentation classification,
not an operator, legal ownership class, causal estimate, or funding-law measure.
It now combines identified new/converted sites, DHS purchases for ICE use,
reactivations, and agreements adding ICE detention capacity since January 20,
2025. Routine renewals, higher ADP, and first roster appearance alone do not qualify.

The controlling roster panel supplies the allowed IDs. The reviewed rows in
`config/map_graphic_expansion_sites.csv` specify `applies_on`, `event_type`,
`event_by`, `event_date_basis`, source URLs, and notes. `event_by` is a supported
latest possible event date; a month-end bound is not an assertion that the event
occurred on that day. The bound must be on or after January 20, 2025 and no later
than the applicable map date. Unknown IDs, duplicate IDs, unobserved target dates,
missing evidence, unsupported event types, and invalid/future dates fail validation.
Legacy c3 rows retain their separately approved earlier applicability.

New assignments currently apply to July 9, 2026 only. The earlier two panels are
preserved, so changes in c3 between those panels and July cannot be interpreted
as event or population growth on a consistent category definition. This coverage
limit must be visible with the revised panel and remain in build warnings.

Each observed roster entity is counted once. Its full reported ADP enters its
presentation category, regardless of the size of a contract's added capacity or
the date of the qualifying event within the fiscal-year ADP period. Operator
name/class, owner annotation, raw facility type, source values, and underlying
IDs remain unchanged. Keep Dilley's two reporting entities separate and describe
the female component's site-level reactivation inference. Do not code Dilley,
Northeast Ohio, Cimarron, or Nevada Southern as purchased on service evidence.
Midwest's qualifying July event is March 12 intake, not the August sale. Prairie
is outside the current roster and remains excluded.

## Three-date graphic: federal contracting group

Kevin approved moving Migrant Ops Center Main A from Other to Federal on
September 10, 2026 in task `01a07489-03f7-78e3-a2b3-13a85505bb4f`, followed by
implementation and regeneration of the graphics and dated calculation copy.
This is a presentation grouping for the contracting-type bar. It does not
change ICE's raw type, the operator, ownership, or the population category.

The generated `contracting_type_group` field is governed for this graphic:
`federal` contains CDF, USMS CDF, STAGING, BOP, SPC, DOD, and MOC;
`state_local` contains STATE, IGSA, DIGSA, and USMS IGA; all remaining reported
types map to `other`. One row represents one observed roster entity on one
of the three approved dates. Each entry counts once, including entries with
missing ADP. The bar's denominator is the full observed facility count.

The raw type comes from the registered workbook row. The allowed IDs come from
the controlling roster panel. Python exports the group to both JSON and CSV,
and the renderer consumes that same field. Unknown or missing group values in
render input fail validation. June now contains 35 federal entries: seven BOP,
one DOD, one MOC, and 26 CDF/USMS CDF/SPC/STAGING entries. Its other groups are
163 state/local and one JUVENILE entry. January and July counts are unchanged.
See the implementation record (`docs/graphics_copyedit_20260910.md`) for checks and
the exact dated outputs. This grouping is not a legal ownership finding.

## Readiness buckets

### Current governed

- **Task 4 ADP rule:** use the Level A-D total whenever all four source values
  are numeric. Preserve criminality and threat totals as separate
  decompositions and reconciliation checks. Small source-decomposition
  differences do not erase a usable Level A-D total; retain exact differences
  and reconciliation tiers.
  `docs/reported_adp_level_sum_evidence.md` records the controlling workbook
  cells, ICE definitions, full-series reconciliation, and required public
  wording. Call the result a derived reported ADP total; do not imply that ICE
  supplied a separate total field.
- **Task 4 reconciliation-tier rule:** call a nonzero maximum component
  difference of 3 or less `small_component_difference_le_3`; call a larger
  difference `material_component_difference`. The boundary is inclusive and
  descriptive. It does not assert that rounding caused the difference.
- **Task 4 ADP reporting-period rule:** every panel and summary row carries the
  source fiscal year, the `fiscal_year_to_iids_date_average` reporting basis,
  the applicable October 1 fiscal-year start, and the facility-sheet IIDS date
  as the reporting-period end.
- **Task 4 ALOS rule:** preserve the FY-specific facility value and publish
  snapshot-level facility coverage, median, inclusive 25th/75th percentiles,
  minimum, maximum, and flagged extremes. Do not publish a systemwide weighted
  or unweighted ALOS without a later compatible methodology source.
- **Task 4 guaranteed-minimum rule:** sum numeric reported values only and
  publish numeric, explicit `N/A`, and blank counts/shares. Never zero-fill,
  label the total capacity, or use it as a utilization denominator.
- The longitudinal lane uses only DDP-preserved ICE workbooks under
  `data/raw/ice_detention_management_ddp/`. One explicitly selected workbook
  controls each internal IIDS date; superseded same-date files remain in the
  correction audit.
- The public analysis begins with 2025-01-06 as the pre-inauguration baseline;
  2025-01-21 is the first available post-inauguration IIDS date; 2024-12-23 is
  a stability check. Administration-period labels are chronological, not
  causal.
- `observed_facility_count` counts distinct supported final facility IDs in one
  controlling snapshot. It is the primary expansion metric. A source-row count
  is never a substitute.
- `first_observed_after_baseline`, `not_observed`, and `reappeared` describe
  roster history. They do not mean opened, closed, or reopened.
- A `first_observed_after_baseline` event remains an in-window roster
  classification even when the same reviewed facility identity has a FY2024
  identity-only anchor. The panel, event table, and summaries disclose that
  prior anchor separately so the event cannot be mistaken for the facility's
  first appearance anywhere in the DDP source history.
- A user-confirmed duplicate-source collision removes the duplicate row and
  restores the normal exact cross-date identity rule for other included rows
  with the same normalized name, address, city, and state. The approved
  survivor controls the final facility ID; unresolved collisions remain split
  and routed to review.

- Raw source bytes are immutable and identified by SHA-256.
- Source rows retain workbook/file, sheet, row, and raw labels.
- ICE's raw `type_detailed_as_reported` values remain unchanged. Their governed
  explanatory meanings and evidence statuses are maintained in
  `docs/ice_facility_type_glossary.md`; provisional or unresolved labels cannot
  be promoted into ownership, operator, contract, or operating-status claims.
- `not_observed_in_snapshot` is not a closure, abandonment, or non-opening.
- Post `Capacity` is preserved as `post_planned_capacity` and is not
  automatically treated as an incremental bed count.
- A Post soft-sided component row is not automatically identical to the named
  permanent parent facility. Parent-site relationship, operation of a
  soft-sided structure, and completion at the Post-reported capacity require
  separate evidence and statuses. See `docs/soft_sided_facility_research.md`.
- Facility and award linkage tiers remain explicit in every downstream table.
- ICE facility observations use the exact workbook-snapshot, sheet, and source
  row key defined in `docs/facility_identity_contract.md`.
- Facility entities use opaque IDs allocated from a permanent source anchor.
  A source observation may anchor a singleton entity, and exact normalized
  name/address/city/state rows may share that entity only when no same-snapshot
  collision exists. A tracked human decision may merge a non-exact component
  into one declared surviving anchor. In the longitudinal detention-roster
  lane, an approved facility identity may retain multiple same-date source rows
  when ICE reported separate rows for that facility. Roster presence counts the
  final facility entity once per date; every source row remains preserved, and
  numerical values are not combined without a separately approved aggregation
  rule. Names and addresses never generate entity IDs directly.
- Current Dilley/Guantanamo identity rule (approved 2026-08-26): Dilley
  Immigration Processing Center, Dilley Processing Single Adult Female, JTF
  Camp Six, and Migrant Ops Center Main A remain four separate entities. This
  supersedes the earlier pair merges and leaves zero included facility/date
  multiplicities. Their reported numerical values remain unchanged and are not
  aggregated or recalculated across the pairs.
- The governed address comparison expands only `HWY` to `HIGHWAY`; it preserves
  street numbers and all other tokens. Raw addresses remain as reported. An
  address is a comparison field, not a universal facility identifier; reviewed
  source typos remain case-specific rather than becoming global aliases.
- Four reviewed Post rows now link to three facility entities: North Lake,
  Alexandria Staging, and Corrections Center of Northwest Ohio. The Alexandria
  Family and Female rows remain separate source rows, and their capacities are
  not treated as additive.
- A reviewed `separate_facilities_same_complex` relationship never merges
  facility entities. Folkston Annex at 3424 and Folkston Main at 3026 are the
  current approved example.
- The facility sheets have no general capacity field. `Guaranteed Minimum` is
  a contractual field and is not a capacity denominator.
- Level A-D are the governed components for an as-reported facility ADP
  derivation. All 501 Phase 3 rows reconcile to both criminality and threat-
  level decompositions within `0.00001`.
- The primary Phase 4 universe is contract award types A-D awarded by the ICE
  subtier with action dates from 2023-10-01 through 2026-07-18. A separately
  labeled supplemental lane is allowed only for verified non-ICE award
  descriptions or contract lineage that directly names a governed facility.
- USAspending transactions, awards, recipients, facilities, and relationship
  rows retain separate keys and grains. A relationship table never changes the
  grain of an amount.
- Automatic award-facility links require an exact governed facility name or
  address phrase in a transaction/base-award description, or a verified
  direct-description contract lineage. The longest exact alias suppresses
  truncated prefix duplicates within the same field.
- `federal_action_obligation` is governed at transaction grain. Award total
  obligation, total outlay, current value, and potential value remain distinct.
  No amount is allocated to a facility.
- Award-to-transaction reconciliation is attempted only against a frozen
  award-detail API record. Repeated award rollup fields in the bulk transaction
  download are not a verified award-grain total.
- File C uses field-specific time semantics. `TransactionObligatedAmount`
  reports transactions during the current reporting period and may be summed
  across nonoverlapping periods within a fiscal year. FY2026 P02 is exceptional:
  its TOA includes P01, so P01 must not be counted again. Cumulative current-
  period-end measures, including `ObligationsIncurredTotalByAward_CPE` and
  `GrossOutlayAmountByAward_CPE`, must not be summed across submission periods;
  use the latest comparable checkpoint or difference consecutive checkpoints.
- The current normalized File C table retains `transaction_obligated_amount`
  and `gross_outlay_amount_FYB_to_period_end`; it does not retain
  `ObligationsIncurredTotalByAward_CPE`. Each retained amount field carries
  its own governed metadata column: `toa_additivity`
  (`additive_across_nonoverlapping_periods_within_fy_fy2026_p02_includes_p01`)
  and `gross_outlay_additivity`
  (`cumulative_checkpoint_use_latest_or_difference_never_sum`).
- Recipient and parent-recipient fields establish award relationships only.
  They do not establish operator, owner, or facility manager identity.
- The FOIA disclosure universe uses the timestamp displayed on each ICE FOIA
  Library entry. Underlying document, inspection, contract, and operational
  dates remain separate fields.
- `foia_entry_id` identifies one unique listing entry even when live pagination
  exposes it on more than one frozen page. `document_id` identifies one
  canonical direct disclosure URL; redirects and byte hashes remain separate.
- Raw FOIA listing pages and direct files are immutable, local, Git-ignored
  inputs controlled by `data/foia_manifest.csv` and exact SHA-256 values.

### Candidate / needs review

- Task 4A produced `metadata/detention_roster_metric_inventory.csv` and
  `docs/detention_roster_metric_semantics_review.md`. Kevin approved the ADP,
  ALOS, and guaranteed-minimum rules on 2026-08-26. Tasks 4B-D implemented and
  verified the panel and summary schemas. The Nassau-corrected totals were
  reapproved on August 27, 2026.
- The dense facility-snapshot panel, roster-event table, and snapshot-summary
  schemas are built and structurally verified. They remain review outputs, not
  publication-ready findings; corrected Task 4 approval does not approve later
  geography or narrative findings.
- A systemwide ALOS statistic is not governed. The approved Task 4 output is
  the facility-level distribution and coverage only.
- Map coordinates require a reviewed facility-location ledger and approved
  geocoding source/provider. Facilities lacking coordinates remain in counts
  and are disclosed as unplottable.
- Saved DDP candidate approvals bind the final facility ID, candidate ID, DDP
  code, and frozen source hash. Spreadsheet display formatting never replaces
  those generated bindings.
- A reviewed display-name amendment may change a candidate from human-review
  to full-exact automatic status without changing facility identity. Preserve
  the superseded human decision in the review backup and omit the redundant
  active location decision.

- Supported, probable, ambiguous, and unmatched cross-year alias decisions.
- Clark County Jail (ID)'s reviewed provisional location is source-bound and
  implemented, but the entity remains `identity_review_required` and cannot
  enter supported Task 4 findings without corroborating ICE evidence.
- `planned_soft_sided_component_at_parent_site` is a candidate relationship
  concept, not an implemented or approved review-schema value. It must not be
  silently represented as ordinary facility identity.
- Supported operator/location award links that lack a direct facility phrase.
- Operator, owner, parent-company, and contractor-role entity resolution.
- FOIA facility mentions, FY2026 dispositions, historical-identity
  dispositions, additional-facility candidates, and Post match tiers remain a
  review queue until extraction completes and source pointers are audited.
- `known_fy2026_identity` in the automated FOIA table means a unique exact
  governed-name relationship with compatible title location under the FOIA
  rule. It does not create or approve an entity merge, prove current operation,
  or authorize a curated decision.

### Not yet governed

- Ownership, operator identity, parent-company history, award terms not exposed
  in USAspending, inspections, conditions, litigation, local permits, and
  construction milestones.

## Source inventory and precedence

| Claim or metric type | First source | Fallback | Why |
|---|---|---|---|
| Post roadmap row and `Capacity` | Supplied Post CSV | Preserved Post graphics/article context | The CSV is the direct table supplied for this project; graphics explain but do not replace row values. |
| ICE-reported longitudinal observation or measure | Exact row in the controlling DDP-preserved ICE workbook | Superseded same-date DDP version only for correction comparison | The preserved ICE row controls what ICE reported; the configured version controls the dated roster. |
| ICE detailed facility type | Exact `type_detailed_as_reported` value plus `docs/ice_facility_type_glossary.md` | Facility-specific official agreement, audit, or contract | Preserve the raw value; the glossary explains supported meanings and keeps provisional or unresolved definitions visible. |
| Facility identity across sources | Reviewed crosswalk with source-row evidence | Conservative candidate queue | Names alone are unstable and cannot silently control identity. |
| Provisional correction to an internally conflicting facility location | Reviewed official/local evidence stored separately from the raw observation | Candidate location research | Raw DDP fields prove what ICE reported; reviewed geography may aid analysis only with explicit provisional status and cannot silently replace source values. |
| Facility proximity or same-complex relationship | Reviewed contextual evidence plus distinct official source rows | Verified map/location context | Proximity supports a relationship only; it cannot establish official hierarchy, ownership, or one merged identity. |
| Opening, expansion, closure, or abandonment | Dated direct official/contractual evidence | Multiple corroborating dated sources | Snapshot presence or absence is insufficient. |
| Award amount and timing | Exact USAspending award or transaction record | Official contract document | Each amount has a distinct grain and definition. |
| Award-to-facility relationship | Direct facility reference | Supported operator/location match | Contractor context alone is not facility spending. |
| Recipient identity | USAspending recipient and parent-recipient fields | Signed award or contract document | Recipient does not prove operator, owner, or facility manager. |
| File C award financial evidence | Exact source record from the frozen File C submission, interpreted under the named amount field's time basis | Later official submission snapshot | TOA is current-period activity; cumulative CPE measures are checkpoints, and FY2026 P02 TOA already includes P01. |
| Geographic coordinates | Verified source address plus reviewed geocode in the curated location ledger | Unplottable status; a centroid requires separate approval and must be labeled approximate | A geocode supports map placement, not operational status. Missing coordinates do not remove a facility from counts. |
| FOIA disclosure-window membership | Exact ICE FOIA Library entry timestamp | Frozen raw listing page | The listing timestamp establishes disclosure timing, not the underlying document or facility-operation date. |
| FOIA disclosed document | Exact bytes from the entry's direct link plus SHA-256 | Explicit access-failure record | A downloaded file proves what ICE disclosed at retrieval; it does not prove current operation or entity identity. |
| FOIA facility mention | Exact title or page/sheet/text locator with detention-use context | Conservative candidate queue | Generic geography and detention wording cannot establish a facility identity. |
| FOIA-to-FY2026 relationship | Existing governed aliases plus compatible name/location evidence | Unresolved candidate review | Automated output never edits the governed entity layer. |
| FOIA-to-Post relationship | Direct identifiers, address, contract reference, or compatible reviewed evidence | Descriptive candidate only | Soft-sided, warehouse, tent, family, or mega-facility language alone cannot confirm the Post project. |

## Canonical entities and grains

| Entity or table | Grain | Primary key | Required provenance |
|---|---|---|---|
| Post roadmap source | One supplied CSV row | `post:{source_row:04d}` | Raw row number, source hash |
| ICE facility observation | One workbook facility row in one snapshot | `iceobs:{snapshot_slug}:{sheet_slug}:{source_row:06d}` | File hash, sheet, row, raw fields |
| Facility entity | One source-anchor identity, exact cross-snapshot group, or reviewed merge component | Opaque `fac_{uuid5_hex}` from a permanent ICE observation anchor | Source-anchor rule, exact or reviewed crosswalk evidence rows, anchor label, and separate governed display label |
| Facility alias | One source label linked to one facility entity | `source_system + source_row_id` | Match rule, evidence tier, reviewer status |
| Facility relationship decision | One reviewed observation pair and relationship scope | `review_decision_id` | Source-row IDs and hashes, evidence source, review date/status, optional display name, and generated application check |
| Post-facility review decision | One Post source row linked to one reviewed facility entity | `review_decision_id` and unique `post_row_id` | Post row, reference ICE observation, approved entity, evidence, date, and capacity-additivity status propagated to the Post disposition |
| Facility-snapshot panel | One analytically eligible final facility entity by one controlling IIDS date, including explicit not-observed rows | `{facility_entity_id}::{snapshot_slug}` | Applied assignment, source observation when present, metric parse status, support/exclusion rule, and snapshot inventory |
| USAspending award | One USAspending award record | `generated_unique_award_id` or documented equivalent | Retrieval snapshot and raw record pointer |
| USAspending transaction | One transaction/action record | `generated_unique_transaction_id` or documented equivalent | Award id, action date, raw record pointer |
| Award-recipient relationship | One award and its reported direct/parent recipient | `award_id + recipient_uei` or named-recipient fallback | Award source, recipient role, operator-status caveat |
| Transaction-facility relationship | One transaction and one directly named facility | `transaction_id + facility_entity_id + matched_field + normalized_alias` | Exact phrase, field, source alias row, amount name, no-allocation status |
| Award-facility relationship | One award-facility candidate link | `award_id + facility_entity_id` | Linkage tier, evidence, review status |
| File C award evidence | One retained source record for an award/account/submission period; multiple records may share abbreviated account dimensions | Stable source-row pointer plus source ID, period, award, complete account dimensions, and financial element | File hash, submission period, complete account keys, physical source row, and field-level time semantics |
| FOIA Library entry | One unique listing entry | `foia_entry_id` | Frozen page URL(s), displayed timestamp, title, category, direct URL |
| FOIA document | One canonical direct disclosure URL | `document_id` | Entry IDs, retrieval status/time, final URL, media type, bytes, SHA-256, extraction status |
| FOIA facility mention | One explicit facility candidate in one document at one locator | `mention_id` | Document ID, entry ID, raw name/location, title or text locator, extraction rule, review status |
| FOIA facility inventory | One approved existing entity or one unresolved normalized-name/location candidate | `entity:{facility_entity_id}` or `foiafacility_{hash}` | Contributing mentions/documents, disclosure range, disposition set, candidate IDs, no-approval status |

## Canonical metrics

| Metric | Definition | Grain | Date rule | Status |
|---|---|---|---|---|
| `post_planned_capacity` | Exact numeric `Capacity` supplied in the Post CSV | Post row | Roadmap/article context; do not assign an ICE snapshot date | Current governed |
| `ice_reported_capacity` | A general rated/operational capacity value from an explicitly named ICE field | ICE observation | Carry workbook snapshot and field definition | Unavailable in the three facility sheets; do not substitute `Guaranteed Minimum` |
| `ice_average_daily_population` | Sum of `Level A` through `Level D` for one facility source row when all four values are numeric | ICE observation | Carry `source_fiscal_year`, `adp_reporting_basis`, `adp_period_start`, and the facility-sheet IIDS date as `adp_period_end` | Governed; exact component differences and neutral reconciliation tiers remain visible |
| `ice_guaranteed_minimum` | Exact `Guaranteed Minimum` value as reported by ICE | ICE observation | Carry facility-sheet IIDS date | Governed as reported; not capacity or utilization denominator |
| `observed_facility_count` | Count of distinct supported final facility IDs with an included row in one controlling snapshot | Controlling IIDS date | Internal facility-sheet date; January 6 is baseline | Governed and implemented; approved Task 4E rules and later corrections apply |
| `states_and_territories_count` | Count of distinct nonblank reported state/territory values among observed supported facilities | Controlling IIDS date | Same as roster count | Implemented; not a substitute for reviewed point geography |
| `first_observed_after_baseline_count` | Count of supported facility identities whose first in-window observation occurs after 2025-01-06 | Controlling IIDS date | First available controlling occurrence; disclose any FY2024 identity-only anchor separately | Governed and implemented; does not prove opening |
| `reported_adp_total` | Sum of every numeric facility-row Level A-D total among supported observed facilities | Controlling IIDS date | Carry fiscal-year-to-IIDS reporting period and coverage | Governed and implemented with reconciliation tiers; approved Task 4E rules and coverage qualifications apply |
| `guaranteed_minimum_reported_total` | Sum of numeric as-reported guaranteed-minimum values, accompanied by reported and missing facility counts | Controlling IIDS date | Never zero-fill blanks | Governed and implemented; never label capacity |
| `case_composition` | Separate source-reported criminality and threat-level component totals/shares | Facility observation or controlling date | Preserve component family and coverage | Governed and implemented; no composite severity score |
| `average_length_of_stay` | Exact FY25/FY26 ALOS source value or approved facility-level distribution | Facility observation or controlling-date distribution | Preserve FY-specific header and fiscal-year-to-IIDS period semantics | Governed and implemented at facility-distribution level; no systemwide statistic |
| `utilization_rate` | Reviewed population numerator divided by a compatible rated/operational capacity denominator | Facility snapshot | Numerator and denominator must refer to compatible dates/definitions | Not computable from the current facility sheets alone |
| `federal_action_obligation` | Obligated amount reported for one contract action; may be positive, zero, or negative | USAspending transaction | Carry action date and 2026-07-18 retrieval snapshot | Governed |
| `award_total_obligation` | Award-detail API total obligation for a frozen direct candidate; bulk repeated rollups remain labeled unverified | USAspending award | Carry award-detail retrieval date | Governed with source-status field |
| `award_total_outlay` | Named award-detail outlay total, kept separate from obligations | USAspending award | Carry award-detail retrieval date | Governed when reported |
| `award_current_value` | Base plus exercised-options value from the award-detail record | USAspending award | Carry award-detail retrieval date | Governed when reported |
| `award_potential_value` | Base plus all-options potential value from the award-detail record | USAspending award | Carry award-detail retrieval date | Governed when reported |
| `file_c_transaction_obligated_amount` | File C obligation/deobligation transactions reported for the current submission period | File C evidence record | Add only across nonoverlapping reporting periods within one fiscal year; FY2026 P02 already includes P01 | Governed; implemented as `toa_additivity` |
| `file_c_gross_outlay_amount_FYB_to_period_end` | File C gross outlays accumulated from fiscal-year beginning through the reporting-period end | File C evidence record | Cumulative within the fiscal year; use the latest comparable checkpoint or difference consecutive checkpoints, never sum checkpoints | Governed; implemented as `gross_outlay_additivity` |
| `file_c_obligations_incurred_total_by_award_CPE` | File C obligations incurred from fiscal-year beginning through the reporting-period end | File C source record | Cumulative within the fiscal year; never sum checkpoints | Governed source definition; not retained in the current normalized table |

## Canonical evidence dimensions

### Facility match tier

- `exact_source_identity`: direct identifier or exact name/location evidence
  with no conflict. Under the current rule, normalized name, address, city, and
  state all agree and the exact key has no same-snapshot collision. This rule
  may group observations automatically after the uniqueness check passes. The
  governed address comparison currently adds only `HWY` to `HIGHWAY`.
- `supported_match`: multiple compatible fields or dated sources support the
  same identity despite a name variation; exact address plus compatible
  city/state/ZIP is the current minimum pattern.
- `probable_match`: strong candidate that still requires human review.
- `ambiguous`: competing candidates or material conflicts.
- `unmatched`: no defensible candidate under current evidence.
- `invalid_observation`: a note-like or malformed row lacks the minimum usable
  name/location signature.

Candidate-row `reviewer_status` describes the evidence for that exact
observation pair, not merely the final entity component. Use
`user_approved_same_facility` only for a directly reviewed pair and
`auto_accepted_exact_unique` only for a pair whose own exact evidence passed.
`entity_resolved_by_reviewed_component` means the observations are connected
through other reviewed component evidence; it is not a row-level approval.

### Dated facility outcome tier

- `confirmed_dated_evidence`: a dated source directly supports the claimed
  opening, expansion, operation, closure, or other outcome.
- `probable_dated_evidence`: multiple compatible dated clues support the
  outcome but do not directly establish it.
- `ambiguous`: evidence conflicts or does not distinguish possible outcomes.
- `not_observed_in_snapshot`: no defensible observation in the named snapshot;
  no broader negative conclusion is allowed.

### Award linkage tier

- `direct_facility_reference`: award or contract material names the facility,
  address, or unique facility identifier. This is the only automatic Phase 4
  facility-link tier.
- `supported_operator_location_match`: operator/recipient, place, timing, and
  other evidence jointly support a facility relationship.
- `contractor_context_only`: the recipient is relevant, but the award cannot be
  assigned to a specific facility.
- `unlinked`: no defensible facility or operator relationship.

### FOIA FY2026 disposition

- `known_fy2026_identity`: unique automated relationship to an existing FY2026
  entity under the narrow FOIA name/location rule; still `not_approved` and not
  proof of current operation.
- `possible_fy2026_identity`: one or more compatible FY2026 candidates require
  review.
- `known_historical_identity_not_observed_fy2026`: the mention maps to a
  governed historical entity with no FY2026 observation; this is not a closure
  or non-operation claim.
- `possible_historical_identity_not_observed_fy2026`: a historical relationship
  remains unresolved.
- `additional_facility_candidate`: no governed FY2026 or historical entity met
  the automated rules; it is not an approved new facility.

### FOIA-to-Post tier

- `candidate`: compatible description, name, or location that requires review.
- `supported_match`: exact governed name plus city/state or stronger compatible
  evidence, but no direct Post-project identifier.
- `confirmed_match`: reserved for reviewed direct identifiers, addresses,
  contract references, or equivalent document language. The automated pipeline
  does not emit this value.

## Join rules

| Left source | Right source | Allowed join | Cardinality check | Wrong join to avoid |
|---|---|---|---|---|
| Post rows | Facility entities | Reviewed crosswalk row | Each Post row has exactly one disposition; multiple rows may link to one entity without being collapsed | Normalized facility name alone or summing capacities merely because rows share an entity |
| ICE observations | Facility entities | Source-anchor assignment, exact unique crosswalk row, or tracked reviewed merge | Each source row maps to exactly one final entity and a reviewed merge retains one declared survivor; longitudinally reviewed multi-row reporting grains may share one entity/date but remain separate source observations | City/state alone, unrestricted fuzzy match, address-only automatic merge, or treating same-entity rows as numerically additive |
| Facility entities | Facility relationships | Reviewed pair decision with a named relationship scope | Each decision preserves both entity IDs; a separate-facility relationship requires different IDs | Merging neighboring buildings because they share a complex, ZIP, operator, or map context |
| Facility entities | Snapshots | Applied reviewed assignment crossed with controlling snapshot inventory | Exactly one panel row per eligible `facility_entity_id + snapshot_id`; the current applied data must have zero included source-row multiplicities | Treating missing observations as zero, counting source rows, or combining separately governed Dilley/Guantanamo records |
| Awards | Facilities | Relationship table with linkage tier | Many-to-many remains explicit; no row multiplication in facility totals | Recipient name directly joined to facility name |
| Transactions | Awards | Exact USAspending award ID | Every transaction maps to one award; award and transaction rows remain separate | Treating repeated award fields on transaction rows as independent awards |
| Awards | Recipients | Exact award-detail or transaction recipient fields | One direct relationship row per award in the current layer | Treating recipient as operator or owner |
| Candidate awards | File C | Exact award ID/PIID plus preserved source-row, account, financial-element, and period keys | Keep every matching source record; aggregate only by the named field's time rule | Summing cumulative CPE checkpoints, treating TOA as cumulative, or double-counting FY2026 P01 through P02 |
| FOIA entries | FOIA documents | Canonical direct URL/document ID | Every in-window entry maps to one document; one document may retain multiple entry IDs | Dropping failed/unsupported documents or treating redirects as new disclosures |
| FOIA mentions | Facility entities | Governed FOIA name/location candidate rule | Many mentions may route to one entity; every automated row remains not approved | Updating curated identities or using name-only similarity as approval |
| FOIA mentions | Post rows | Exact or candidate relationship with explicit tier | One mention may have multiple Post candidates; ambiguity remains visible | Confirming a Post project from a soft-sided, warehouse, tent, family, or capacity resemblance alone |

## Date and freshness rules

- Store separate `source_retrieved_at`, `source_as_of`, `reporting_start`, and
  `reporting_end` fields when available.
- Never use fiscal-year labels as if every workbook were an end-of-year total.
- Keep file/release dates separate from facility-sheet IIDS dates. The current
  facility dates are 2024-10-07, 2025-09-15, and 2026-04-02.
- Preserve the changing facility inclusion notes: FY2024-FY2025 exclude HOTEL,
  while FY2026 names JUVENILE instead. Absence can reflect the published
  universe as well as operational change.
- A later FY2026 file is a new snapshot, not an in-place replacement of the
  frozen April 9 snapshot.
- Refresh ICE and USAspending source inventories before claiming a result is current.
- Preserve exact filenames and hashes for every published analysis snapshot.
- The longitudinal detention-roster lane uses only manifest rows under
  `data/raw/ice_detention_management_ddp/` with Deportation Data Project
  GitHub download URLs. ICE remains the original issuer. Direct-ICE files under
  `data/raw/ice/` belong only to the legacy three-snapshot lane and must not be
  mixed into longitudinal roster extraction.
- The primary transaction universe and all 64 direct candidate API archives are
  frozen as of 2026-07-18. Refresh them before making a current spending claim.
- For FY2026 File C, P02 is the first public monthly submission and its TOA
  includes P01. Do not describe P02 as November-only or add a separate P01 TOA.
- The frozen FOIA window is 2025-01-20 through 2026-08-20, inclusive, using
  ICE's displayed Eastern-time listing timestamps. A later library refresh is a
  new source snapshot and must not overwrite the frozen manifest silently.

## Wrong-answer modes

- Calling 58,336 Post-table capacity `new beds`.
- Treating ICE `Guaranteed Minimum` as rated capacity or using it to calculate
  utilization.
- Treating `not observed` as `did not open`, `closed`, or zero.
- Treating operation of Port Isabel, Moshannon Valley, Prairieland, Nevada
  Southern, Dilley, T. Don Hutto, or another parent facility as proof that a
  proposed soft-sided component opened or achieved the Post-reported capacity.
- Combining FY2024 end-of-year and FY2025/FY2026 YTD measures without dates.
- Confirming a facility match from normalized name alone.
- Extending the North Lake exact-address decision into a universal facility-ID
  rule without first resolving same-snapshot address collisions, or converting
  a case-specific typo correction into a global normalization alias.
- Summing multiple Post capacity rows merely because they link to one facility
  entity; Alexandria Family and Female have unestablished additivity and must
  remain separate until verified.
- Merging distinct Annex and Main facility entities because they occupy the
  same complex or appear near one another on a map.
- Collapsing operator, owner, award recipient, and parent company.
- Treating award ceiling, current award value, obligations, outlays, and one
  transaction amount as interchangeable.
- Testing a transaction sum against a repeated bulk-row award rollup as if the
  latter were a frozen award-detail record.
- Summing cumulative File C CPE checkpoints across submission periods.
- Treating `TransactionObligatedAmount` as a cumulative checkpoint instead of
  current-period activity.
- Double-counting FY2026 P01 TOA after it has been combined into P02.
- Allocating contractor-level totals to a facility without supported evidence.
- Calling an award recipient the operator without a contract or operator-
  specific source.
- Using a map marker or geocode as proof of operation.
- Replacing a conflicting raw ICE address with a reviewed location without
  preserving both layers, evidence, and provisional status.
- Dropping ambiguous or unmatched records from denominators without disclosure.
- Treating a FOIA posting timestamp as the document's creation date, inspection
  date, contract date, or proof of operation during the posting window.
- Counting a shifted pagination duplicate as a second disclosure.
- Omitting unsupported, image-only, OCR-required, or failed documents from the
  document denominator.
- Calling `additional_facility_candidate` a confirmed new or operating facility.

## Detention-language discovery rules

The detention-language subsystem is a candidate-discovery layer, not an
extension of the governed Phase 4 facility-link layer. Its population is every
ICE-awarded contract action with `action_date >= 2025-01-20`, including later
actions on older awards and IDVs.

- `direct_detention` requires explicit detention, custody, detainee housing,
  bed-space, secure-housing, holding, or detainee-processing purpose.
- `facility_support` requires ancillary service or infrastructure language
  tied by deterministic proximity to detention or governed facility evidence.
- `contextual_lead` preserves weaker facility-type, acronym, movement, code,
  office, recipient, or location evidence for review.
- `excluded` retains the rule and evidence explaining why the description was
  rejected. Several weak signals may not add up to a stronger tier.

The primary analyst-facing CSV has one row per award and retains all discovered
awards. Binary fields distinguish direct detention, facility support,
contextual leads, and excluded actions. Procurement award obligation/outlay
totals remain the primary financial measures. File C obligation activity and
latest-checkpoint outlays are separately labeled coverage measures and never
replace the award totals.

The supporting audit CSV stacks transactions, rule evidence, award lineage,
File C relationships, File C financial rows, awaiting awards, and unresolved
facility candidates. Monetary fields are populated only on their native
`record_type`. An exact linked File C `award_unique_key` is the only currently
tested automatic File C relationship. The FY2025 P12 and FY2026 P10 `Unlinked`
members are now source-checked, but PIID/parent fallback relationships remain
`WARN`: the inspected target-account PIIDs did not recover current D1 awards,
recipients, parent vehicles, or exact FOIA instruments.
- Calling an automated `known_fy2026_identity` row a human-approved entity
  decision.
- Confirming a Post project from descriptive similarity alone.

### Unlinked File C PIIDs and IGSA residuals — September 13, 2026

An `unlinked_file_c_piid` is the exact PIID reported on a File C financial row
that USAspending did not connect to a public award key. It is a contract-
recovery candidate, not a verified procurement, recipient, IGSA, facility, or
purpose relationship. Preserve four dispositions: `verified_igsa`,
`verified_non_igsa`, `unclassified`, and `file_c_only_unlinked`. Moving a PIID
out of the last two categories requires an exact recipient-bearing agreement,
award record, or equivalent original instrument; an `F` order also requires its
parent PIID when applicable.

PIID position nine is a numbering clue, not an IGSA classifier. Although `P`
is the standard purchase-order code, P-coded `70CDCR20P00000046` is identified
by ICE's FOIA library as the Snake River Juvenile Detention Center IGSA and by
USAspending as an award to the County of Twin Falls. Do not classify the
`70CDCR25PSA...` or `70CDCR26PSA...` series as non-IGSA without the underlying
instrument.

`file_b_minus_all_file_c` is the compatible File B amount less every compatible
Contracts, Assistance, and Unlinked File C amount. Classifying an Unlinked PIID
does not change it. `igsa_compatible_unexplained_envelope` is a candidate
decomposition after verified non-IGSA File C and separately identified non-
award activity are removed. It is not an IGSA point estimate or state/local
payment total. Use it only within the same fiscal year, period, TAFS, PARK,
object class, direct/reimbursable status, DEFC, sign convention, source vintage,
and available PYA. Negative adjustments or missing PYA can prevent an upper-
bound interpretation.

The IGSA spending and residual brief (`docs/igsa_spending_residual_analysis.md`)
controls the dated empirical counts, source hashes, PIID search results, and
open recovery queue. Refresh that note and this rule when a PIID recovers an
instrument, a later submission changes the target population, or a documented
IGSA-to-File-C payment chain is established.

**Reference alignment — September 18, 2026:** the approved
identification strategy (`docs/file_b_file_c_identification_strategy.md`), scope
revision `8b4a282`, now controls the proposed accounting comparison: both
federal accounts `070-0540` and `070-0545`, all object classes, and the three
selected multiyear account scopes at their specified endpoints. It produces
gross-outlay differences, not an obligation residual. The earlier single-TAS
brief and 25.4-only methodology remain dated evidence, not limits on this
new scope. These pointers do not change the definitions above or establish
that the new comparison has been executed.

The corrected Relevant Research identifier review (`docs/research/relevantresearch_identifiers_20260918/README.md`)
supersedes five extraction values for new exact-identifier searches and adds
a source-supported order–parent pair. Preserve original strings and the
correction ledger; the untouched lane extraction is no longer sufficient by
itself for those searches. A documented pair is not yet a File C match, an
FPDS-reporting finding, or a FAR-applicability determination. The four
instrument dispositions above remain unchanged; USMS/interagency payment-channel
labels are a separate dimension. The
supporting-reference review (`docs/igsa_spending_residual_analysis.md`, section 16)
records source checks, historical limits and the exclusion of the externally
changing strategy working copy from formula verification.

## Query routing

1. Verify raw inputs against `data/manifest.csv`.
2. Identify the requested entity, metric, grain, and as-of date here.
3. Use a governed definition when available.
4. Route candidate definitions through the unresolved/review layer.
5. Use raw exploration only as labeled evidence discovery, never as a silent
   replacement for a governed definition.

## Eval questions

| Question | Expected source/rule | Required caveat | Status |
|---|---|---|---|
| How many Post roadmap rows are there? | Supplied Post CSV at Post-row grain | Distinguish rows from unique real-world facilities after matching | Verified: 125 source rows |
| Did a named facility open by year-end? | Dated outcome evidence plus reviewed facility identity | Workbook absence is not proof of failure | Needs source review |
| Did a Post soft-sided component open? | Dated component-specific evidence plus a governed parent-site relationship | Parent-facility operation, higher ADP, or a matching city does not establish the proposed structure or capacity | El Paso identity ambiguous; Dilley structures supported but 250-capacity Post outcome unverified; five others searched/not established |
| How many beds did the roadmap add? | Capacity definitions across Post/internal-document context | Post CSV `Capacity` is not automatically incremental | Not yet answerable |
| How much federal spending went to a facility? | Directly linked transaction/award records plus the relationship table | The current layer does not allocate award amounts to facilities, and one award may name multiple facilities | Evidence layer governed; a facility total is not produced |
| Which company operates a facility? | Contract or operator-specific source joined through a governed relationship | USAspending recipient alone is insufficient | Not established in Phase 4 |
| Does a P-coded Unlinked File C PIID prove a non-IGSA purchase? | Exact recipient-bearing instrument plus the IGSA spending and residual brief (`docs/igsa_spending_residual_analysis.md`) | Position nine is a numbering clue; P-coded `70CDCR20P00000046` is a verified IGSA counterexample | Governed answer: no; target PIIDs remain unresolved |
| Is File B minus File C an IGSA spending estimate? | Compatible File B/File C controls plus separately verified award and non-award classifications | Unlinked File C, payroll, benefits, other non-award activity, signs, and missing PYA remain separate | Not yet answerable; only an unexplained accounting envelope |
| Which facilities first appear in FY2026? | Governed ICE observation keys plus the reviewed facility-entity panel by facility-sheet IIDS date | `newly appearing` does not mean newly built/opened and the inclusion universe changed | Reviewed-entity panel built; remaining non-exact candidates await review |
| Are Folkston Annex and Main one facility? | Curated user-approved decision, exact ICE source rows, and contextual screenshot | They are separate facility entities in the same complex; the screenshot does not prove official hierarchy or ownership | Verified for the current frozen snapshots |
| Are the Alexandria Family and Female capacities one facility total? | Two preserved Post rows plus the reviewed shared facility entity | Identity is approved, but additivity, overlap, and component structure are not established | One entity; capacity relationship unresolved |
| How should File C amounts be combined across periods? | Named File C financial element plus fiscal year and submission period | TOA may be added across nonoverlapping periods; cumulative CPE measures may not; FY2026 P02 includes P01 | Definition verified and implemented in per-field output metadata |
| Which FOIA disclosures fall in the target window? | Frozen entry table at `foia_entry_id` grain | Use ICE listing timestamps; keep underlying document dates separate | Acquisition verified; extraction incomplete |
| Does a disclosed record identify a facility absent from FY2026? | Source-anchored FOIA mention plus governed FY2026/historical reconciliation | `additional_facility_candidate` requires review and does not prove operation | Needs full extraction and candidate audit |
| Does a FOIA facility confirm a Post-described project? | Exact FOIA locator plus reviewed Post relationship | Descriptive similarity alone cannot exceed candidate; automated output cannot confirm | Needs source review |

## Provenance footer

Use this pattern for substantive answers:

```text
Source: [governed source row/table]
Freshness: [source as-of and retrieval date]
Definition/grain: [metric and one-row meaning]
Validation: [hash/key/reconciliation/reviewer check]
Confidence: [High | Medium | Low]
Residual gap: [specific unresolved evidence]
```

## Maintenance triggers

Update this rulebook when a workbook schema or facility-type taxonomy changes,
a later source snapshot is added, an award amount or linkage definition is
approved, a recurring wrong answer reveals a missing rule, or a better direct
source supersedes a fallback.


## Current scoped outlay-coverage example — September 10, 2026

The blog’s outlay comparison is an application of the existing File B/File C
boundaries, not a new facility-spending definition. Its explicit scope is
TAS 070-2025/2029-0545-000, PARK 5ZD2ZMBJ8U0, FY2026 P10. Sum the nonblank
`gross_outlay_amount_FYB_to_period_end` values separately within each source;
retain object class, direct/reimbursable, DEFC and award dimensions in File C.
The two selected award rows contribute $15,247,086.83 against $4,845,337,255.50
in File B. The remainder is $4,830,090,168.67 and is not attributed to awards.

Award-level site totals can include other accounts. KVG’s award-wide
$24,422,330.55 includes $9,357,827.32 from 0540/PARK 5ZD2ZMB6YC1; that amount
is outside the numerator and denominator of this figure. Period differences
must be verified, not presumed, when reconciling an award page with an account
extract. The public extract’s PYA is unavailable; visible-dimension checks do
not establish hidden-field uniqueness.

The outlay guide (`docs/outlay_traceability_graphic.md`) supplies exact source rows,
variables and local reproduction pointers. This saved-snapshot comparison does
not establish missing required award reports, a legal disclosure exemption,
improper spending, or a detention/facility expenditure total.
