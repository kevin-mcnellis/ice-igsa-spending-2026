# Published File C article claim audit

Published text JSON SHA-256: `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`. Overall **WARN**.
Published URL: https://www.kevinmcnellis.com/posts/ICE_IGSA/. Saved HTML SHA-256: `33c91a77197ec405a2a3fad8e99eafd72af1a5bf1c0c583123db08f58ac1d786`.

Counts: `{"ACCEPTED_BY_AUTHOR": 11, "PASS": 191, "WARN": 123}`.

Internal audit command (requires the Part A audit worktree and registered local sources; it cannot run from this public bundle): `python3 -B File_C_blog_post/audit/final_audit.py --manuscript File_C_blog_post/data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json --expected-hash cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815 --published-receipt File_C_blog_post/data/raw/final_audit/published_page/2026-09-28T13-23-41Z.receipt.json --source-root File_C_blog_post --reviews File_C_blog_post/audit/published_inputs/reviews.json --author-decisions File_C_blog_post/audit/published_inputs/author_decisions.json --fragments File_C_blog_post/audit/published_inputs/fragments.json --output-dir File_C_blog_post/outputs/claim_audit`
Public snapshot checks: saved HTML SHA-256 `33c91a77197ec405a2a3fad8e99eafd72af1a5bf1c0c583123db08f58ac1d786`; extracted text SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`. The public bundle provides the claim record and hashed text snapshot, but not every source file or the audit runtime.

A WARN marks a documented limitation, interpretive overreach, or incomplete source check; the claim-specific reason states which applies. Author acceptance records a wording decision, not technical verification.

## Failures

None.

## Warnings

- **TITLE.S1** (TITLE): What USAspending.gov Doesn’t Show About ICE’s Detention Spending
  - Interpretive title. The reviewed files show specific gaps between account totals, named recipients, and facility attribution; they do not measure every detention payment or prove all IGSA payments absent.
  - Proposed fix: Read the title with the Methodology's object-class, recipient, and facility-match limits.
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
- **SUBTITLE.S1** (SUBTITLE): ICE’s award records name almost none of the state and local governments that hold most of its detainees.
  - The page's selected award records name few state and local government recipients, but this audit cannot measure every payment reaching governments that operate facilities.
  - Proposed fix: Qualify 'almost none' as a finding about the selected File C award records and state the government-recipient denominator.
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: subtitle
- **P1.S1** (P1): Most people held by Immigration and Customs Enforcement (ICE) are in state and local facilities that ICE uses through intergovernmental service agreements (IGSAs).
  - The roster type groups include USMS IGA and do not by themselves establish state/local operation or payment route.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 168 facilities in three ICE IGSA-type labels
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/figure_b_data.csv`; SHA-256 `885e101b3d8f9e5b8ecbe6973ffe243a42b6be811730c6f9619b5ebefe900c54`; locator: facilities
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/verification.json`; SHA-256 `3624168efc005114b88082953bd17dfbc124dd6cd0cfea9dec2ed7ef99db6ad2`; locator: figure_b.limits
- **P1.S2** (P1): In July 2026, these facilities held 57% of ICE's detainees.
  - The number rounds to 57%, but “held 57% of detainees” reads like a July headcount; source is reported ADP.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 35,790.871887 / 62,516.733098 = 57.25% fiscal-year-to-date ADP
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/figure_b_data.csv`; SHA-256 `885e101b3d8f9e5b8ecbe6973ffe243a42b6be811730c6f9619b5ebefe900c54`; locator: reported_adp
- **P2.S3.C1** (P2): from 2015 to 2018, ICE penalized facilities for failing detention standards on “only two occasions”
  - OIG-19-18 reports two penalties among 106 facilities it reviewed in 2015–2018; the published clause lacks the reviewed-population limit.
  - Proposed fix: Say 'at the 106 facilities the OIG reviewed' before the two-penalty count.
  - Recomputed or checked: Two occasions in the OIG's 106-facility review
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 2
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 11
- **P2.S3.C2** (P2): thousands of documented violations of the agency’s own detention standards.
  - OIG-19-18 identifies thousands of deficiencies in the inspected facilities, but the clause omits the review population and inspection period.
  - Proposed fix: Tie the documented violations to the OIG's inspected facilities and period.
  - Recomputed or checked: OIG-19-18, 2015–2018 review of 106 facilities
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 2
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 11
- **P3.S1** (P3): Yet the public record of federal spending shows almost none of this.
  - “Almost none” is not defined by a denominator or payment universe; the comparison does not quantify all IGSA spending visibility.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.solely_iga_award_piids
- **P3.S3.C2** (P3): its award records account for $3.14 billion of that.
  - The fresh File C object-class 25.4 sum is $3,136,530,747.79, which rounds to $3.14 billion. The words 'of that' inherit the preceding unsupported detention-facility scope; object class 25.4 is a service category, not a facility-only measure.
  - Proposed fix: State the $3.14 billion as File C object-class 25.4 obligations without tying it to a detention-facility-only account total.
  - Recomputed or checked: $3,136,530,747.79
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.bar_totals
  - Source: `data/raw/final_audit/omb_a11_2025.pdf`; SHA-256 `7b0e6a3b018f6beea1c4b55ff377821fbd16def96354df5b319b2642ecd604c1`; locator: 262
  - Source: `audit/independent_recomputation.json`; SHA-256 `2f33fbf81a316aecf5713753efbc7261fbb99b03771d8c6e3f12831af2d23a6d`; locator: fresh independent check
- **P4.S2.C1** (P4): They total $17.5 million
  - They total $17.5 million: Amount matches, but replacement/expiration chronology is not fully settled for both agreements.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.solely_iga_25_4_amount
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 2
  - Source: `data/raw/final_audit/EROIGSA-17-0003-P00029.pdf`; SHA-256 `9c509e304d20c7eee84c2a7c38fdfa8a297c45f36a4d3237d6bdda2798b8408d`; locator: 2
  - Source: `audit/facility_screen_recheck.json`; SHA-256 `1ea3fd6e44c60fbb2973c154480512864c264d4cf478cba8bc3ffec4fc7b0a17`; locator: fresh read-only rerun
- **P4.S2.C2** (P4): both fall under a non-competitive contract that replaced two New Mexico counties’ IGSAs in April 2026.
  - both fall under a non-competitive contract that replaced two New Mexico counties’ IGSAs in April 2026.: Amount matches, but replacement/expiration chronology is not fully settled for both agreements.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.solely_iga_25_4_amount
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 2
  - Source: `data/raw/final_audit/EROIGSA-17-0003-P00029.pdf`; SHA-256 `9c509e304d20c7eee84c2a7c38fdfa8a297c45f36a4d3237d6bdda2798b8408d`; locator: 2
  - Source: `audit/facility_screen_recheck.json`; SHA-256 `1ea3fd6e44c60fbb2973c154480512864c264d4cf478cba8bc3ffec4fc7b0a17`; locator: fresh read-only rerun
- **P4.S3** (P4): No award record identifies the spending under the counties’ IGSAs.
  - The bounded zero scan does not establish that no public award record identifies any payment under the county IGSAs.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 0 selected identifier hits in 1,815,637 frozen 070-account rows
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
  - Source: `audit/torrance_recheck.json`; SHA-256 `1cf64f1f96d3b506bae540ef399307f2b4af44763359eb56b7049de3e272d3b1`; locator: fresh read-only rerun
- **P5.S1** (P5): This post shows where ICE's IGSA payments most likely sit in the public data.
  - “Most likely sit” is a proposed explanation, not a traced payment allocation.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P5.S2** (P5): The same gap appears in ICE's construction spending: in a report for Co-Equal, I found that public award records identified the recipients of only 7% of its $5.4 billion from its construction account.
  - The cited Co-Equal report and its exact $5.4 billion denominator were not retrieved; the current gap chart is only a related check.
  - Proposed fix: Supply an accessible Co-Equal report PDF/page for the 7% claim or remove that example.
  - Recomputed or checked: 7.69% from a later frozen 070-0545/25.2 comparison; cited Co-Equal report unavailable
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/chart_data.csv`; SHA-256 `8c811c691f450b0ebaa4ac6e1c700f88d614785805d32eb2c9781cbf950cb17c`; locator: construction_25_2
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: coequal
- **P5.S3** (P5): This analysis shows how tracing its detention spending from its operations account will require additional sources beyond USAspending.gov.
  - The stated need for additional sources follows from identified public-data limits but no complete alternative-source plan or payment universe is tested.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P6.S1** (P6): IGSAs do not clearly fit the kinds of spending for which federal law requires a public record of who was paid.
  - IGSA treatment under federal award reporting rules is a legal inference; OIG recorded ICE’s position but did not adjudicate the reporting statute.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/legal_sources/PLAW-109publ282.pdf`; SHA-256 `fac8d346dc31abfd839ef2cfc3230a115ebcf9020b82c10a99282e2f51e87cd1`; locator: 2
  - Source: `data/raw/legal_sources/PLAW-109publ282.pdf`; SHA-256 `fac8d346dc31abfd839ef2cfc3230a115ebcf9020b82c10a99282e2f51e87cd1`; locator: 3
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 7
- **P7.S3** (P7): The law does not say what kind of agreement that is or which federal contracting rules apply.
  - The legal inference needs careful distinction between the payment clause and adjacent cooperative-agreement authority.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: §373(a)(9)(A) uses generic agreement; §373(a)(9)(B) separately authorizes cooperative agreements
  - Source: `data/raw/final_audit/PLAW-104publ208.pdf`; SHA-256 `dec27f0049c9632010de245fd5cdd5c7d8dd030526826e586ec272ed56864447`; locator: 648
- **P8.S2** (P8): In its July 2026 facility list, 168 of the 208 facilities holding ICE detainees (81%) operated under agreements with state or local governments.
  - Roster counts match, but ICE type labels alone do not prove each facility operated under a state/local agreement on that date.
  - Proposed fix: Say “ICE listed 168 of 208 observed facilities under IGSA, DIGSA or USMS IGA labels.”
  - Recomputed or checked: 168/208 = 80.77%, displayed 81%
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/figure_b_data.csv`; SHA-256 `885e101b3d8f9e5b8ecbe6973ffe243a42b6be811730c6f9619b5ebefe900c54`; locator: facilities
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/verification.json`; SHA-256 `3624168efc005114b88082953bd17dfbc124dd6cd0cfea9dec2ed7ef99db6ad2`; locator: figure_b.limits
  - Source: `audit/independent_recomputation.json`; SHA-256 `2f33fbf81a316aecf5713753efbc7261fbb99b03771d8c6e3f12831af2d23a6d`; locator: fresh independent check
- **P9.S1** (P9): Despite ICE’s reliance on IGSA facilities, little is known about how ICE discloses the spending tied to these agreements.
  - The breadth of available IGSA spending disclosure has not been comprehensively inventoried across payment systems.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
- **P9.S5.C1** (P9): The second dataset contains records for individual spending awards
  - The second download is an account breakdown by award, but it includes Unlinked rows without a named award recipient. The claim is accurate for linked award rows and overbroad for every record in the file.
  - Proposed fix: Say the download contains award-level records plus Unlinked account-breakdown rows.
  - Recomputed or checked: Five numeric object-class 25.4 Unlinked rows lack a recipient
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/comparison_source_rows.csv`; SHA-256 `b38b2010fe8b57f10d8896303a81b824e7c80e290398a85cdfc0dfd570fa3a59`; locator: FY2025 Unlinked rows 502,1669; FY2026 Unlinked rows 5570,5582,5589
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P32
- **P9.S5.C2** (P9): name the funding’s recipient.
  - Five numeric 25.4 Unlinked rows carry PIIDs, but their award_unique_key, public award link, recipient UEI, and recipient name are blank; the categorical recipient claim needs the adjacent Methodology exception.
  - Proposed fix: Limit recipient naming to linked award records and point to the no-recipient rows.
  - Recomputed or checked: Five rows; signed total $9,498,809
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/comparison_source_rows.csv`; SHA-256 `b38b2010fe8b57f10d8896303a81b824e7c80e290398a85cdfc0dfd570fa3a59`; locator: FY2025 Unlinked rows 502,1669; FY2026 Unlinked rows 5570,5582,5589
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P32
- **P9.S6** (P9): Any obligation ICE does not tie to a spending award appears only in the account totals.
  - The five numeric Unlinked 25.4 rows appear in File C as well as the account-level reporting universe. They contain PIIDs but lack the award unique key, link, and recipient, so whether they are tied to a public spending award depends on the meaning of tied. The word only is too broad.
  - Proposed fix: Say obligations without a public award link may appear as File C Unlinked rows and in account totals.
  - Recomputed or checked: Five Unlinked rows with PIIDs and blank award_unique_key; signed total $9,498,809
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/comparison_source_rows.csv`; SHA-256 `b38b2010fe8b57f10d8896303a81b824e7c80e290398a85cdfc0dfd570fa3a59`; locator: FY2025 Unlinked rows 502,1669; FY2026 Unlinked rows 5570,5582,5589
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P32
- **P10.S1** (P10): If ICE reported its IGSA payments to spending awards, then the counties, cities, and states that are counterparties on the IGSAs would appear among the recipients.
  - The conditional assumes county/state counterparties would be named; payments could be through USMS or private-award channels, and no complete payment ledger is reconciled.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: State and local governments
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
- **P10.S2** (P10): They almost never do.
  - “Almost never” is a qualitative interpretation of the selected recipient table, not a census of all IGSA counterparties.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 3 government UEIs representing 2 local governments in selected 25.4 File C
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: State and local governments
- **P10.S3** (P10): From February 2025 through July 2026, ICE tied $3.14 billion in obligations for “operating and maintaining facilities” to spending awards with 74 named recipients.
  - The wording may imply all $3.14 billion has a named recipient; $9,498,809 is Unlinked without one.
  - Proposed fix: Say “ICE tied $3.14 billion to File C records; 74 named UEIs account for $3.127 billion of it.”
  - Recomputed or checked: $3,136,530,747.79 total; 74 named UEIs cover $3,127,031,938.79
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/verification.json`; SHA-256 `1d84091fed7fa8b9ceab643885f1e252f80da1d111db61791387011b45e00965`; locator: analysis.named_recipients
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `audit/independent_recomputation.json`; SHA-256 `2f33fbf81a316aecf5713753efbc7261fbb99b03771d8c6e3f12831af2d23a6d`; locator: fresh independent check
- **P11.S1** (P11): Why are the counties and cities missing?
  - Rhetorical question; the premise that all county/city payments are missing has not been established.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
- **P11.S2** (P11): One possible explanation is that the award records name the private companies that run many of the IGSA facilities, not the governments that signed the IGSAs.
  - Plausible pathway but not traced from IGSA invoices to private recipient award records.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P11.S3** (P11): If so, those payments would be hard to find because the same companies also run facilities under contracts directly with ICE.
  - Shared private operators do not establish that any given File C award paid under an IGSA.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: geo_corecivic_share_percent
- **P11.S4** (P11): In July 2026, facilities run by the two largest contractors – GEO Group and CoreCivic – held 58% of ICE detainees.
  - Rounded figure matches, but several operator attributions remain inferred or provisional.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 36,116.587191 / 62,516.733098 = 57.7711%
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: geo_corecivic_share_percent
- **P11.S5.C1** (P11): About half of those detainees were in facilities ICE uses under agreements with state and local governments
  - About half of those detainees were in facilities ICE uses under agreements with state and local governments: Approximate shares match saved attribution, subject to provisional operator decisions and type-label limits.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: igsa_share_within_geo_corecivic_percent
- **P11.S5.C2** (P11): most of the rest were in facilities ICE contracts for directly.
  - most of the rest were in facilities ICE contracts for directly.: Approximate shares match saved attribution, subject to provisional operator decisions and type-label limits.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: igsa_share_within_geo_corecivic_percent
- **P11.S6.C1** (P11): A payment to GEO or CoreCivic could therefore pay for either kind of facility
  - A payment to GEO or CoreCivic could therefore pay for either kind of facility: This is a possibility; award recipient identity alone does not identify the facility or agreement.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: geo_corecivic_share_percent
- **P11.S6.C2** (P11): the award record may not say which.
  - the award record may not say which.: This is a possibility; award recipient identity alone does not identify the facility or agreement.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: geo_corecivic_share_percent
- **P12.S2.C1** (P12): These descriptions are open-ended and are not required to list a facility
  - USAspending's About the Data says award-description quality varies; it does not state a binding rule that descriptions are never required to identify a facility.
  - Proposed fix: Say the descriptions may omit facility names, or cite the rule governing the description field.
  - Recomputed or checked: About the Data, page 12: quality/description caveat
  - Source: `data/raw/final_audit/usaspending_about_data.pdf`; SHA-256 `b3d4f5c6513daae90e496a522b0c44382be1fb25257e4d679528ba766252d321`; locator: 12
- **P12.S2.C2** (P12): some do.
  - USAspending's About the Data explains limits in descriptions, but it does not itself show a facility-naming description. The facility-name screen identifies name matches, yet this audit has not traced a cited example to its original description field.
  - Proposed fix: Cite one original File C award-description row naming a facility, with its source row ID.
  - Recomputed or checked: Facility-name screen reports 21 federal-contract matches and five IGA matches; original description example not separately checked
  - Source: `data/raw/final_audit/usaspending_about_data.pdf`; SHA-256 `b3d4f5c6513daae90e496a522b0c44382be1fb25257e4d679528ba766252d321`; locator: 12
- **P13.S9** (P13): But it finds almost no trace of the state and local facilities that hold most of ICE's detainees.
  - The screen measures description name mentions, not the full spending trail for state/local sites.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 5/224 IGSA-type facilities have description matches
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.iga_matched_facilities
- **P14.S1** (P14): The two awards behind that $17.5 million are the clearest evidence that ICE's payments under IGSAs are missing from the award records.
  - The fresh scan found zero literal county-IGSA identifier hits in 1,815,637 returned DHS File C rows, while two ICE direct task orders for the facilities carried $17,465,361.06 in selected 25.4 obligations. Calling these the clearest evidence is an author interpretation; the scan does not identify or prove missing county-IGSA payments across all award records.
  - Proposed fix: Attribute the inference to the author and say the sampled award rows did not identify the county agreements or counterparties.
  - Recomputed or checked: Zero searched identifier hits; two direct orders; $17,465,361.06 selected 25.4 obligations
  - Source: `audit/torrance_recheck.json`; SHA-256 `1cf64f1f96d3b506bae540ef399307f2b4af44763359eb56b7049de3e272d3b1`; locator: scanned_rows, identifier_hit_rows, direct_order_totals
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P14
- **P14.S2.C1** (P14): ICE held detainees at both facilities for years under agreements with the counties
  - ICE held detainees at both facilities for years under agreements with the counties: Dates match scanned documents; county-to-CoreCivic payment arrangement needs direct agreement/subcontract evidence for this whole sentence.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/EROIGSA-17-0003-P00029.pdf`; SHA-256 `9c509e304d20c7eee84c2a7c38fdfa8a297c45f36a4d3237d6bdda2798b8408d`; locator: 1
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 1
- **P14.S2.C2** (P14): which paid CoreCivic to run them
  - which paid CoreCivic to run them: Dates match scanned documents; county-to-CoreCivic payment arrangement needs direct agreement/subcontract evidence for this whole sentence.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/EROIGSA-17-0003-P00029.pdf`; SHA-256 `9c509e304d20c7eee84c2a7c38fdfa8a297c45f36a4d3237d6bdda2798b8408d`; locator: 1
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 1
- **P14.S2.C3** (P14): Cibola County's IGSA dates to October 2016
  - Cibola County's IGSA dates to October 2016: Dates match scanned documents; county-to-CoreCivic payment arrangement needs direct agreement/subcontract evidence for this whole sentence.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/EROIGSA-17-0003-P00029.pdf`; SHA-256 `9c509e304d20c7eee84c2a7c38fdfa8a297c45f36a4d3237d6bdda2798b8408d`; locator: 1
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 1
- **P14.S2.C4** (P14): Torrance County's to May 2019.
  - Torrance County's to May 2019.: Dates match scanned documents; county-to-CoreCivic payment arrangement needs direct agreement/subcontract evidence for this whole sentence.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/EROIGSA-17-0003-P00029.pdf`; SHA-256 `9c509e304d20c7eee84c2a7c38fdfa8a297c45f36a4d3237d6bdda2798b8408d`; locator: 1
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 1
- **P14.S3** (P14): These agreements show that ICE approved payment increases, including higher payment rates approved in 2025 and 2026, retroactive to earlier months.
  - Agreement modifications support rate changes, but the whole plural 2025/2026 chronology requires complete source mapping.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Cibola P00025 retroactive rates Jan.–Apr. 2025; Torrance P00045 later rates
  - Source: `data/raw/ice_foia_cibola/EROIGSA-17-0003-P00025-P00026-CibolaCountyCorrectionalCenterIGSA-MilanNM.pdf`; SHA-256 `913fcd144af50dfd3c36a316b1b7b6c2e7e4e975dcb1d764d8e3fedb50c42213`; locator: 2
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 2
- **P14.S4** (P14): Yet in the award data from October 2024 until the agreements ended, no award record identifies either agreement or either county as a recipient.
  - Negative result is bounded to the 1,815,637 returned rows and named identifiers; not the whole award universe.
  - Proposed fix: Limit the negative finding to the two frozen 070-account downloads and the selected identifiers.
  - Recomputed or checked: 0 selected identifier hits in two frozen 070-account downloads
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
  - Source: `audit/torrance_recheck.json`; SHA-256 `1cf64f1f96d3b506bae540ef399307f2b4af44763359eb56b7049de3e272d3b1`; locator: fresh read-only rerun
- **P15.S1.C1** (P15): In February 2026, New Mexico enacted the Immigrant Safety Act
  - The enrolled H.B. 9 PDF establishes the Immigrant Safety Act, but this audit has not checked the official chapter/enactment record for the precise February 2026 date.
  - Proposed fix: Add the official enactment or governor-signature record for the February date.
  - Recomputed or checked: H.B. 9 title and section 1 verified; enactment date not independently established
  - Source: `data/raw/final_audit/HB0009.pdf`; SHA-256 `2979b7c4afdbe16ebc16ce2efc2a6343a143d500e392cd8da28ea6e0c3df32a7`; locator: 2
- **P15.S1.C2** (P15): bars local governments from entering into or extending agreements to hold people for civil immigration violations, including IGSAs
  - H.B. 9 section 3 addresses new and renewed agreements for civil immigration detention. The phrase 'including IGSAs' is a category application; the statute does not name the federal IGSA label in this clause.
  - Proposed fix: Quote section 3(A)'s covered-agreement language and separately explain why the local IGSAs fall within it.
  - Recomputed or checked: H.B. 9 section 3(A)
  - Source: `data/raw/final_audit/HB0009.pdf`; SHA-256 `2979b7c4afdbe16ebc16ce2efc2a6343a143d500e392cd8da28ea6e0c3df32a7`; locator: 2
- **P15.S2** (P15): In March, ICE announced it would issue a non-competitive contract with CoreCivic for both facilities.
  - The cited SAM page could not be read beyond its JavaScript shell in this audit; third-party mirror is only a lead.
  - Proposed fix: Register an official SAM notice receipt or narrow to the saved IDV solicitation reference.
  - Recomputed or checked: SAM notice NOI-70CDCR26R00000014 posted 2026-03-10
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: sam_notice
  - [https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view](https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view)
- **P15.S3.C2** (P15): ICE awarded CoreCivic.
  - ICE awarded CoreCivic.: Author separately accepted the expiration phrase; this full sentence still needs the conflicting county-manager date distinguished.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 2
  - Source: `provenance/torrance_award_api/idv.json`; SHA-256 `64fe190ea0587b21657262261fca984ab87edb98e8700cd88826dbd6523a94c8`; locator: date_signed
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: santa_fe
- **P15.S4** (P15): The new contract’s spending immediately appeared in the award records: two task orders with $17.5 million obligated to operate the facilities through July.
  - Amount and order dates are supported; “immediately” is a chronology inference and the sentence omits the selected object-class scope.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: $17,465,361.06 selected File C 25.4 on two ICE direct orders
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.solely_iga_25_4_amount
  - Source: `provenance/torrance_award_api/idv.json`; SHA-256 `64fe190ea0587b21657262261fca984ab87edb98e8700cd88826dbd6523a94c8`; locator: date_signed
- **P16.S1** (P16): If ICE is paying other IGSA facilities the same way, much of its spending at the state and local jails that hold most of its detainees may be missing from those records as well.
  - Counterfactual extrapolation from two New Mexico facilities to other sites is not tested; no payment-universe estimate exists.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.solely_iga_award_piids
- **P17.S1** (P17): From February 2025 through July 2026, ICE obligated $4.8 billion from its operations account for facilities, services, transportation and equipment without tying it to any award, as shown below.
  - The $4.8 billion is the signed File B minus File C residual for four object classes, with File C including Unlinked numeric rows before subtraction. The Methodology defines that accounting difference and says it is not an IGSA estimate; it does not establish that every residual dollar lacked any award.
  - Proposed fix: Call the amount an account-to-award-file reporting difference, not spending proved awardless.
  - Recomputed or checked: Four-class residual $4,799,482,587.89; plotted File C includes $58,987,437.93 Unlinked
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/verification.json`; SHA-256 `6e254b4c7c4ca6970cd67df506098d33e9f1667759b5ef98f4d254d424994404`; locator: title_gap, limitations
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P67
- **P17.S2** (P17): USAspending.gov shows how much ICE committed, but not who received it.
  - The residual cannot identify ultimate payees, but the wording should not imply no related award evidence exists.
  - Proposed fix: State the recipient-visibility limit of the File B–File C difference without implying all award links are absent.
  - Recomputed or checked: File B has no recipient; File C has linked and Unlinked rows
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/chart_data.csv`; SHA-256 `8c811c691f450b0ebaa4ac6e1c700f88d614785805d32eb2c9781cbf950cb17c`; locator: title_gap
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
- **P18.S1.C1** (P18): ICE's payments under IGSAs are most likely in one of two places: in these account-level totals
  - ICE's payments under IGSAs are most likely in one of two places: in these account-level totals: The two proposed locations are plausible hypotheses, not a verified accounting allocation of IGSA payments.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P18.S1.C2** (P18): in award records that do not identify the facility they pay for.
  - in award records that do not identify the facility they pay for.: The two proposed locations are plausible hypotheses, not a verified accounting allocation of IGSA payments.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P18.S2** (P18): The untied totals also include other spending, however, such as travel by ICE's own employees and payments to other federal agencies.
  - Those categories can include non-IGSA spending, but their exact composition in the File B–C residual is not identified.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: The four object classes include travel, equipment and other services
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/chart_data.csv`; SHA-256 `8c811c691f450b0ebaa4ac6e1c700f88d614785805d32eb2c9781cbf950cb17c`; locator: title_gap
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/verification.json`; SHA-256 `6e254b4c7c4ca6970cd67df506098d33e9f1667759b5ef98f4d254d424994404`; locator: limitations
- **P19.S1.C1** (P19): The DHS OIG and GAO have been highlighting the fiscal risks of ICE’s IGSAs for nearly two decades
  - The cited OIG and GAO reports document fiscal risks, but the supplied report set does not establish a continuous nearly-two-decade OIG-and-GAO record for ICE IGSAs.
  - Proposed fix: Date the cited reports directly or add an earlier primary report that supports the duration claim.
  - Recomputed or checked: OIG-18-53 (2018), OIG-19-18 (2019), GAO-21-149 (2021)
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 2
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 25
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 2
  - [https://www.gao.gov/assets/gao-21-149.pdf](https://www.gao.gov/assets/gao-21-149.pdf) (28)
- **P19.S1.C3** (P19): failures to penalize underperforming facilities
  - OIG-19-18 documents inspection and remedy weaknesses, but the broad plural 'failures to penalize underperforming facilities' needs a specific finding and time period tied to these IGSAs.
  - Proposed fix: Tie the claim to the OIG's specific penalty or remedy finding and identify the reviewed agreements.
  - Recomputed or checked: OIG-19-18, printed page 2; general inspection and remedy finding
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 2
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 25
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 2
  - [https://www.gao.gov/assets/gao-21-149.pdf](https://www.gao.gov/assets/gao-21-149.pdf) (28)
- **P19.S1.C4** (P19): spending “millions of dollars a month on unused detention beds.”
  - GAO-21-149 discusses unused guaranteed beds, but the quoted 'millions of dollars a month' wording and its scope have not been verified as a verbatim GAO passage in this final source check.
  - Proposed fix: Verify the exact quotation and period on the cited GAO page or paraphrase the documented unused-bed spending.
  - Recomputed or checked: GAO-21-149, page 28 cited; quotation not independently confirmed
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 2
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 25
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 2
  - [https://www.gao.gov/assets/gao-21-149.pdf](https://www.gao.gov/assets/gao-21-149.pdf) (28)
- **P20.S1.C1** (P20): These risks are magnified by the tens of billions that ICE has at its disposal from the One Big Beautiful Bill Act
  - These risks are magnified by the tens of billions that ICE has at its disposal from the One Big Beautiful Bill Act: The short title is independently verified and separately author-accepted; this whole sentence’s combined available-funding scale was not traced to both laws here.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/PLAW-119publ98.pdf`; SHA-256 `6c5bcb9dbb863f480ea6c833fee6c779ac735a8bc7e76d009e28e05a40076f09`; locator: 1
- **P20.S3.C1** (P20): In Muscatine County, Iowa, ICE raised the cap on its payments to the county jail by 75%
  - In Muscatine County, Iowa, ICE raised the cap on its payments to the county jail by 75%: The news supports a roughly 75% cap rise and an ICE amendment to a USMS agreement; it does not verify actual payments or the exact disclosure clause from the underlying document.
  - Proposed fix: Say the ICE amendment raised the Muscatine funding cap about 75%; do not call the cap paid money.
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: daily_iowan
  - [https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/](https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/)
- **P20.S3.C2** (P20): under an agreement that bars “public disclosures.”
  - under an agreement that bars “public disclosures.”: The news supports a roughly 75% cap rise and an ICE amendment to a USMS agreement; it does not verify actual payments or the exact disclosure clause from the underlying document.
  - Proposed fix: Say the ICE amendment raised the Muscatine funding cap about 75%; do not call the cap paid money.
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: daily_iowan
  - [https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/](https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/)
- **P20.S4** (P20): Payments to another Iowa county have more than doubled.
  - The cited Woodbury report supports a more-than-double comparison, but the sentence leaves the county unnamed and the county-fiscal-year comparison basis unstated.
  - Proposed fix: Name Woodbury County, Iowa, and distinguish county fiscal years and actual versus projected amounts.
  - Recomputed or checked: $918,021 for Woodbury county FY2025-26 versus $417,228 in FY2024-25; cited headline discusses projected revenue
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: woodbury
  - [https://www.corrections1.com/iowa-jail-projects-2-3m-increase-from-ice-detainees](https://www.corrections1.com/iowa-jail-projects-2-3m-increase-from-ice-detainees)
- **P20.S5.C1** (P20): In Oklahoma, ICE's monthly payments under the state corrections department's agreement for the Diamondback facility grew from $2.0 million in October 2025
  - Claim checked: Reported monthly payments under the Diamondback agreement were $2.0 million in October 2025.
  - The Frontier reports the October 2025 Diamondback monthly amount from state records; an original state payment record was not available in this audit.
  - Proposed fix: Attribute the amount to The Frontier's state-record review or link the underlying state payment record.
  - Recomputed or checked: Reported $2.0 million, October 2025
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: frontier
  - [https://www.readfrontier.org/31564-2/](https://www.readfrontier.org/31564-2/)
- **P20.S5.C2** (P20): when it held no detainees
  - Claim checked: Diamondback held no ICE detainees in October 2025.
  - The Frontier's displayed state table shows zero average daily ICE population for Diamondback in October 2025; an original occupancy record was not independently checked.
  - Proposed fix: Attribute the zero-detainee statement to the reported state table or link the original occupancy record.
  - Recomputed or checked: Reported October 2025 ICE ADP: zero
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: frontier
  - [https://www.readfrontier.org/31564-2/](https://www.readfrontier.org/31564-2/)
- **P20.S5.C3** (P20): to $8.3 million in March 2026.
  - Claim checked: Reported monthly payments under the Diamondback agreement reached $8.3 million in March 2026.
  - The Frontier reports $8.3 million for March 2026 from state records; an original state or ICE payment ledger was not independently checked.
  - Proposed fix: Attribute the March amount to The Frontier or link the original state payment record.
  - Recomputed or checked: Reported $8.3 million, March 2026
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: frontier
  - [https://www.readfrontier.org/31564-2/](https://www.readfrontier.org/31564-2/)
- **P21.S1** (P21): This analysis set out to use federal data to show how ICE is using IGSAs.
  - Author’s research intent; not independently verifiable from source data.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
- **P21.S2.C1** (P21): It shows where that spending most likely sits
  - It shows where that spending most likely sits: “Most likely sits” and potential scale are inferences, not traced IGSA amounts.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P21.S2.C2** (P21): its potential scale.
  - its potential scale.: “Most likely sits” and potential scale are inferences, not traced IGSA amounts.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.limits
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: interpretation_limit
- **P21.S4** (P21): Assembling a full picture will require additional public attention and scrutiny of ICE’s IGSAs.
  - Advocacy conclusion; source checks do not prove what amount of additional scrutiny is necessary.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
- **P22.S1.C1** (P22): This analysis is provisional
  - Provisional is an author's uncertainty label; the frozen source manifest documents vintages but does not establish the future stability of the analysis.
  - Proposed fix: Keep the provisional label and name the specific limits: data vintages, scope, and unresolved facility attribution.
  - Recomputed or checked: Source vintages fixed in comparison_source_manifest.csv
  - Source: `data/comparison_source_manifest.csv`; SHA-256 `a2b89dd0b8ae7e2bcc317941797f4dd9675f90072a2b4c4c8efd44650e1ecd91`; locator: five frozen downloads
- **P22.S1.C2** (P22): reflects data downloaded in September 2026.
  - The comparison manifest records September 2026 acquisitions, but this audit has not reconciled every source in the full analysis to one download date.
  - Proposed fix: Name the specific File B and File C download dates, or limit the claim to the datasets with dated manifest entries.
  - Recomputed or checked: Comparison manifest includes September 2026 source dates
  - Source: `data/comparison_source_manifest.csv`; SHA-256 `a2b89dd0b8ae7e2bcc317941797f4dd9675f90072a2b4c4c8efd44650e1ecd91`; locator: five frozen downloads
- **P23.S1** (P23): I did this analysis with two AI coding assistants, Anthropic's Claude and OpenAI's Codex.
  - First-person tool-use disclosure. The saved repository and task receipts demonstrate Codex work, but this audit did not reconstruct every Claude contribution or prove that these were the only two assistants.
  - Proposed fix: Retain as the author's disclosure; link the public code and method notes for what can be verified.
- **P23.S2** (P23): Codex wrote and ran most of the code that downloads, processes, and checks the data.
  - The repository shows code and runs, but Git commits and saved outputs do not quantify which assistant wrote most of the code; this is an author attribution.
  - Proposed fix: Retain as a first-person attribution, with the code repository linked.
- **P23.S3.C1** (P23): Claude searched for and checked source documents
  - Claude searched for and checked source documents: The author attributes source search, figure testing, and editing suggestions to Claude; source receipts show the work products but do not identify the agent for every action.
  - Proposed fix: Retain as an attributed process disclosure rather than an independently reconstructed activity log.
- **P23.S3.C2** (P23): tested the figures against those sources
  - tested the figures against those sources: The author attributes source search, figure testing, and editing suggestions to Claude; source receipts show the work products but do not identify the agent for every action.
  - Proposed fix: Retain as an attributed process disclosure rather than an independently reconstructed activity log.
- **P23.S3.C3** (P23): suggested edits to this post.
  - suggested edits to this post.: The author attributes source search, figure testing, and editing suggestions to Claude; source receipts show the work products but do not identify the agent for every action.
  - Proposed fix: Retain as an attributed process disclosure rather than an independently reconstructed activity log.
- **P23.S4.C1** (P23): I directed the work
  - I directed the work: The author states he directed and reviewed the analysis and made final method and wording decisions; several dated approvals are recorded, but the full editorial history is not independently reconstructible here.
  - Proposed fix: Retain as a first-person responsibility and decision disclosure.
- **P23.S4.C2** (P23): reviewed the results
  - reviewed the results: The author states he directed and reviewed the analysis and made final method and wording decisions; several dated approvals are recorded, but the full editorial history is not independently reconstructible here.
  - Proposed fix: Retain as a first-person responsibility and decision disclosure.
- **P23.S4.C3** (P23): made the final decisions on methods and wording.
  - made the final decisions on methods and wording.: The author states he directed and reviewed the analysis and made final method and wording decisions; several dated approvals are recorded, but the full editorial history is not independently reconstructible here.
  - Proposed fix: Retain as a first-person responsibility and decision disclosure.
- **P23.S5** (P23): I am responsible for the analysis and any errors in it.
  - The author's responsibility statement is a first-person declaration, not a numeric or source-document finding that this audit can prove independently.
  - Proposed fix: Keep as the author's own responsibility statement.
- **P23.S6** (P23): See my GitHub for additional details.
  - GitHub reference lacks a final approved repository URL in the locked manuscript.
  - Proposed fix: Add the approved repository URL when it exists; until then do not suggest the detailed package is already available.
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: sam_notice
- **P26.S2.C1** (P26): It reports obligations for individual awards, such as contracts and task orders
  - Linked File C rows report award obligations, including contracts and task orders, but the same download contains Unlinked account-breakdown rows with no identifiable award or recipient.
  - Proposed fix: Limit the sentence to linked File C award rows and separately mention Unlinked rows.
  - Recomputed or checked: Five numeric object-class 25.4 Unlinked rows have no recipient
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/comparison_source_rows.csv`; SHA-256 `b38b2010fe8b57f10d8896303a81b824e7c80e290398a85cdfc0dfd570fa3a59`; locator: FY2025 Unlinked rows 502,1669; FY2026 Unlinked rows 5570,5582,5589
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P32
- **P26.S2.C2** (P26): names each recipient.
  - Five numeric 25.4 Unlinked rows carry PIIDs but leave recipient fields blank; therefore names each recipient is overbroad even though linked award rows ordinarily do.
  - Proposed fix: Say linked award rows name recipients, while Unlinked rows may not.
  - Recomputed or checked: Five source rows; $9,498,809 signed total
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/comparison_source_rows.csv`; SHA-256 `b38b2010fe8b57f10d8896303a81b824e7c80e290398a85cdfc0dfd570fa3a59`; locator: FY2025 Unlinked rows 502,1669; FY2026 Unlinked rows 5570,5582,5589
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P32
- **P31.S3** (P31): USAspending.gov's recipient profiles, and SAM.gov, show each UEI's name and entity type.
  - Recipient/entity-type profiles are a separate USAspending/SAM surface; this audit did not verify every current profile or crosswalk.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/verification.json`; SHA-256 `1d84091fed7fa8b9ceab643885f1e252f80da1d111db61791387011b45e00965`; locator: analysis.named_recipients
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
- **P32.S2** (P32): I grouped the $3.14 billion by UEI.
  - The sentence can imply every dollar grouped by UEI; Unlinked records require a separate missing-recipient bucket.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: $3,136,530,747.79 grouped; $9,498,809 has no UEI
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.bar_totals
  - Source: `audit/independent_recomputation.json`; SHA-256 `2f33fbf81a316aecf5713753efbc7261fbb99b03771d8c6e3f12831af2d23a6d`; locator: fresh independent check
- **P32.S5** (P32): I classified each UEI by the entity information USAspending.gov reports for its awards, retrieved September 23, 2026, not by name alone.
  - The September 23 profile retrieval and all 74 classifications were not independently rechecked in this audit.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Shared classification crosswalk was source-linked in earlier package
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/verification.json`; SHA-256 `1d84091fed7fa8b9ceab643885f1e252f80da1d111db61791387011b45e00965`; locator: analysis.named_recipients
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
- **P34.S2.C1** (P34): Imperial County's two awards (70CMSD18P00000133 and 70CMSD23P00000069)
  - The classified source-row snapshot lists both Imperial County PIIDs, but the audit has not checked their original award records and relationship to Imperial County independently.
  - Proposed fix: Cite each original award record and verify the Imperial County recipient association.
  - Recomputed or checked: Two distinct listed PIIDs: 70CMSD18P00000133 and 70CMSD23P00000069
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/classified_source_rows.csv`; SHA-256 `2146d62dab76a71aeaa81e07400718797d40db7ea5b04ccfff8c6f9513fa918c`; locator: 70CMSD18P00000133
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/classified_source_rows.csv`; SHA-256 `2146d62dab76a71aeaa81e07400718797d40db7ea5b04ccfff8c6f9513fa918c`; locator: 70CMSD23P00000069
- **P34.S2.C2** (P34): were reduced by $18,000 and $14,580.
  - The classified snapshot carries signed negative rows for those two PIIDs, but the final audit has not recomputed each net reduction from original source rows.
  - Proposed fix: Recompute both PIID-level signed totals from the registered File C download and cite the source row IDs.
  - Recomputed or checked: Reported reductions: $18,000 and $14,580
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/classified_source_rows.csv`; SHA-256 `2146d62dab76a71aeaa81e07400718797d40db7ea5b04ccfff8c6f9513fa918c`; locator: 70CMSD18P00000133
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/classified_source_rows.csv`; SHA-256 `2146d62dab76a71aeaa81e07400718797d40db7ea5b04ccfff8c6f9513fa918c`; locator: 70CMSD23P00000069
- **P34.S5** (P34): The Denver Health and Hospital Authority, listed by USAspending.gov as both a local government and a hospital, is grouped with health providers.
  - The analytic grouping is visible; the dual local-government/hospital entity-type assertion needs profile evidence beyond the grouped CSV.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Denver Health −$2,000 grouped with other public/nonprofit
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_totals.csv`; SHA-256 `969ab13dfb93c4b518834cdeb93c1dc491325f9083ea7079c9644e4677ae86bb`; locator: DENVER HEALTH AND HOSPITAL AUTHORITY
- **P35.S3** (P35): The July 9, 2026 figures come from the “Facilities FY26” sheet of the workbook posted July 20, 2026 (FY26_detentionStats07202026.xlsx).
  - Workbook filename and sheet are verified, but the historical ICE live posting date was not independently captured in this audit.
  - Proposed fix: Cite the registered archived workbook and distinguish file date July 20 from internal facility observation date July 9.
  - Recomputed or checked: Facilities FY26 sheet present; July 9 IIDS date in manifest
  - Source: `data/raw/final_audit/FY26_detentionStats07202026.xlsx`; SHA-256 `f83255a56773a7f7a53e46a72ed3bf742397db03eaf14f6abe3f9b07744d28a6`
  - Source: `data/raw/final_audit/canonical_snapshots/data/manifest.csv`; SHA-256 `a09967dec12f22dcdf32d2e8e5e7590e261aaa06ad764f506933a39ce9aa233a`; locator: FY26_detentionStats07202026.xlsx
- **P38.S3** (P38): For the Marshals Service agreements, some payments may flow through the Marshals Service rather than ICE.
  - The third Torrance child award proves a USMS order exists, but does not quantify flows for the full USMS IGA facility group.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Possible USMS payment channel
  - Source: `data/raw/final_audit/torrance_parent_children.json`; SHA-256 `c24bad523e20525fe5c1ed9cc269b8d3464629f67f3a7c622babdad012a002ee`; locator: child_award_count
  - Source: `data/raw/final_audit/usms_torrance_order.json`; SHA-256 `8dfd1f4a0a0d8167b97b3203b42c97801631f2861129e95004638c3de2da51fa`; locator: generated_unique_award_id
- **P39.S2** (P39): The GEO Group and CoreCivic figures use the operator attributions from my September 11, 2026 analysis (GitHub repo).
  - The September 11 analysis/repository URL is a placeholder; verify final link and source version.
  - Proposed fix: Replace the GitHub placeholder with the final approved source repository URL.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: operator_source
- **P39.S3** (P39): On July 9, facilities those companies run held 57.8% of ICE's reported population.
  - Numeric share matches but several operator attributions are provisional.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 57.7711%
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: geo_corecivic_share_percent
- **P39.S4.C1** (P39): 50.5% was in the three IGSA types
  - 50.5% was in the three IGSA types: Numeric shares match the saved join, subject to provisional operator attributions and type limits.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: type_totals
- **P39.S4.C2** (P39): 42.9% was in contract detention facilities.
  - 42.9% was in contract detention facilities.: Numeric shares match the saved join, subject to provisional operator attributions and type limits.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/operator_share/verification.json`; SHA-256 `85b303c3630af54798a8a90558d9804f4c4b7370c74eff74641721f107387f64`; locator: type_totals
- **P40.S4** (P40): The facility list is on this analysis’ GitHub repo.
  - The locked manuscript has no approved GitHub release URL for the facility list.
  - Proposed fix: Replace the GitHub placeholder with the final approved source repository URL.
  - Source: `data/raw/final_audit/canonical_snapshots/output/tables/detention_roster_facility_snapshot_panel.csv`; SHA-256 `021d3f49c5e9893b11cfb2f9d84778634dcca2735de911ef4a1259872135ae6c`; locator: final_facility_entity_id
- **P55.S2** (P55): I searched all records in both File C downloads, across every Homeland Security account, for:
  - Both registered downloads were requested for DHS at agency scope and every returned Contracts, Assistance, and Unlinked row was scanned. Their 84 observed 070-* account symbols support every account represented by award rows in these files. The literal phrase cannot certify accounts with no returned rows or other DHS systems.
  - Proposed fix: For precision, say every account represented in the two downloaded files.
  - Recomputed or checked: 1,815,637 returned rows; 84 distinct 070-* symbols; three members
  - Source: `audit/published_scope_recheck.json`; SHA-256 `3de783e682a4286bc1402405f1a8f889ed53beb3bf34648ecbae156091f86394`; locator: years, combined_account_count, county_row_components, claim_limit
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P55
- **P60.S2** (P60): No record carried any of the identifiers.
  - The zero result is bounded to two frozen 070-account downloads and the chosen literal/normalized identifiers.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 0 specified identifier hits in 1,815,637 rows
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: identifier_hit_rows
  - Source: `audit/torrance_recheck.json`; SHA-256 `1cf64f1f96d3b506bae540ef399307f2b4af44763359eb56b7049de3e272d3b1`; locator: fresh read-only rerun
- **P60.S3** (P60): Apart from CoreCivic's two task orders, the records located in either county are unrelated, such as FEMA and flood-insurance payments.
  - The old zero-county-match objection is reversed: 33 rows carry the county geography. Twelve are on CoreCivic's two direct orders; the other 21 are Assistance rows under FEMA Federal Assistance or National Flood Insurance Fund accounts. The account labels alone do not establish that every other row is substantively unrelated to detention activity.
  - Proposed fix: Describe the 21 other rows as FEMA/NFIP account rows, or document a row-level review before calling all of them unrelated.
  - Recomputed or checked: 12 direct-order rows; 21 FEMA/NFIP assistance rows; zero earlier IGSA identifier hits
  - Source: `audit/published_scope_recheck.json`; SHA-256 `3de783e682a4286bc1402405f1a8f889ed53beb3bf34648ecbae156091f86394`; locator: county_row_components and other_county_account_names
- **P60.S4** (P60): USAspending.gov's award and transaction search, queried September 26–27, 2026, also returned no record of either IGSA task order.
  - API search is mutable and the saved query contract/coverage must be assessed separately from the frozen File C scan.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: 0 named IGSA task-order API hits in dated capture
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: api_capture
  - Source: `audit/torrance_recheck.json`; SHA-256 `1cf64f1f96d3b506bae540ef399307f2b4af44763359eb56b7049de3e272d3b1`; locator: fresh read-only rerun
- **P61.S4** (P61): They also carry $708,458.18 for transportation.
  - “They” again grammatically refers to three children; the third DOJ/USMS award is outside the ICE account comparison.
  - Proposed fix: Say “ICE’s two orders also carry $708,458.18 in selected File C transportation obligations.”
  - Recomputed or checked: $708,458.18 selected 21.0 on two ICE orders
  - Source: `provenance/torrance_cibola_file_c_verification.json`; SHA-256 `ae198ebcf64961d5e0a2ae6f1e82e1f0399bcb4a03b398994c03379705c4debb`; locator: direct_order_totals
  - Source: `data/raw/final_audit/usms_torrance_order.json`; SHA-256 `8dfd1f4a0a0d8167b97b3203b42c97801631f2861129e95004638c3de2da51fa`; locator: funding_agency
- **P61.S6** (P61): ICE's advance notice of the sole-source award is on SAM.gov as notice NOI-70CDCR26R00000014.
  - SAM page was not retrievable as text in this audit; third-party search result is insufficient for an official PASS.
  - Proposed fix: Register an official SAM notice receipt before a PASS.
  - Recomputed or checked: NOI-70CDCR26R00000014
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: sam_notice
  - [https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view](https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view)
- **P67.S2** (P67): Together, the four classes have $4.8 billion not tied to any award.
  - The four-class $4.8 billion value is File B minus all selected File C numeric obligations, including Unlinked entries; the Methodology then disclaims an IGSA estimate. The expression not tied to any award is reporting shorthand and does not prove every dollar lacks an award outside these files.
  - Proposed fix: Say not visible as selected File C obligations, while preserving the accounting-difference caveat.
  - Recomputed or checked: Four-class residual $4,799,482,587.89; $58,987,437.93 Unlinked already included in File C subtraction
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/verification.json`; SHA-256 `6e254b4c7c4ca6970cd67df506098d33e9f1667759b5ef98f4d254d424994404`; locator: title_gap, limitations
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P67
- **P67.S3** (P67): That amount may include payments under IGSAs.
  - No IGSA payment ledger reconciles this residual to agreement payments.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Possible but not measured
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/verification.json`; SHA-256 `6e254b4c7c4ca6970cd67df506098d33e9f1667759b5ef98f4d254d424994404`; locator: limitations
- **P67.S4** (P67): It also includes other spending, such as travel by ICE employees, agency-wide equipment and payments to other federal agencies.
  - The residual’s exact composition is not identified by class labels alone; examples are possible, not measured subamounts.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Travel/equipment/services categories can contain non-IGSA spending
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/chart_data.csv`; SHA-256 `8c811c691f450b0ebaa4ac6e1c700f88d614785805d32eb2c9781cbf950cb17c`; locator: title_gap
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/gap_chart_draft/verification.json`; SHA-256 `6e254b4c7c4ca6970cd67df506098d33e9f1667759b5ef98f4d254d424994404`; locator: limitations
- **FN2.S1** (FN2): U.S. Department of Homeland Security, Office of Inspector General, Immigration and Customs Enforcement Did Not Follow Federal Procurement Guidelines When Contracting for Detention Services, (February 2018) (https://www.oig.dhs.gov/sites/default/files/assets/2018-02/OIG-18-53-Feb18.pdf).
  - The published citation now gives the official OIG report title, but 'February 2018' omits the February 21 date and the OIG-18-53 identifier printed on the report.
  - Proposed fix: Cite Immigration and Customs Enforcement Did Not Follow Federal Procurement Guidelines When Contracting for Detention Services, OIG-18-53 (February 21, 2018).
  - Recomputed or checked: OIG-18-53, February 21, 2018
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 1
- **FN4.S1** (FN4): U.S. Department of Homeland Security, Office of Inspector General, Immigration and Customs Enforcement Did Not Follow Federal Procurement Guidelines When Contracting for Detention Services, (February 2018) (https://www.oig.dhs.gov/sites/default/files/assets/2018-02/OIG-18-53-Feb18.pdf).
  - The published citation now gives the official OIG report title, but 'February 2018' omits the February 21 date and OIG-18-53 identifier.
  - Proposed fix: Use the official title, OIG-18-53, and February 21, 2018.
  - Recomputed or checked: OIG-18-53, February 21, 2018
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 1
- **FN5.S2** (FN5): ICE developed new guidance for IGSAs in 2019, which the GAO cited in a 2021 report, but I could not find a public copy of that guidance.
  - The official GAO footnote supports the guidance citation; the author’s unsuccessful public-copy search cannot be independently established.
  - Proposed fix: Retain GAO’s guide citation but describe the public-copy search as the author’s search only.
  - Recomputed or checked: GAO cites Procurement Guide 18-02 Revision 1 dated March 22, 2019
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: gao
  - [https://www.gao.gov/assets/gao-21-149.pdf](https://www.gao.gov/assets/gao-21-149.pdf) (1)
- **FN6.S1.C1** (FN6): U.S. Immigration and Customs Enforcement, FY2026 detention statistics (July 20, 2026 release), "Facilities FY26" tab (https://www.ice.gov/doclib/detention/FY26_detentionStats07202026.xlsx).
  - U.S. Immigration and Customs Enforcement, FY2026 detention statistics (July 20, 2026 release), "Facilities FY26" tab (https://www.ice.gov/doclib/detention/FY26_detentionStats07202026.xlsx).: The published ICE workbook itself is ignored in this worktree; panel/figure receipts confirm derivative figures but not raw workbook title/date here.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/output/tables/detention_roster_facility_snapshot_panel.csv`; SHA-256 `021d3f49c5e9893b11cfb2f9d84778634dcca2735de911ef4a1259872135ae6c`; locator: 2026-07-09
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/figure_b_data.csv`; SHA-256 `885e101b3d8f9e5b8ecbe6973ffe243a42b6be811730c6f9619b5ebefe900c54`; locator: reported_adp
- **FN6.S1.C2** (FN6): Average daily population is the sum of each facility's fiscal-year-to-date average (Levels A–D).
  - Average daily population is the sum of each facility's fiscal-year-to-date average (Levels A–D).: The published ICE workbook itself is ignored in this worktree; panel/figure receipts confirm derivative figures but not raw workbook title/date here.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `data/raw/final_audit/canonical_snapshots/output/tables/detention_roster_facility_snapshot_panel.csv`; SHA-256 `021d3f49c5e9893b11cfb2f9d84778634dcca2735de911ef4a1259872135ae6c`; locator: 2026-07-09
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/figure_b/figure_b_data.csv`; SHA-256 `885e101b3d8f9e5b8ecbe6973ffe243a42b6be811730c6f9619b5ebefe900c54`; locator: reported_adp
- **FN7.S4** (FN7): File C reports obligations for individual awards.
  - The footnote omits Unlinked records, some with numeric obligations and no identified public award.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: File C includes Contracts, Assistance and Unlinked rows
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.checks
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
- **FN8.S2** (FN8): Each has at least one award that federal records tie to ICE detention, custody, or detainee transportation.
  - The detention/custody/transport tie for each award was not rechecked against every contract description in this audit.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Ten source-linked UEIs in selected contractor class
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_totals.csv`; SHA-256 `969ab13dfb93c4b518834cdeb93c1dc491325f9083ea7079c9644e4677ae86bb`; locator: selected private UEIs
- **FN8.S3** (FN8): The two Akima companies are counted separately because the award records do not show them sharing a parent.
  - Distinct UEIs do not establish independent parents; source records and parent crosswalk need direct confirmation.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Two Akima direct UEIs; common-parent claim unresolved
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/verification.json`; SHA-256 `1d84091fed7fa8b9ceab643885f1e252f80da1d111db61791387011b45e00965`; locator: analysis.named_recipients
- **FN9.S1** (FN9): The award records also list the Denver Health and Hospital Authority, which USAspending.gov categorizes as both a local government and a hospital.
  - The classification is saved, but current USAspending dual entity-type profile was not independently retrieved.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Denver Health grouped as other public/nonprofit at −$2,000
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_totals.csv`; SHA-256 `969ab13dfb93c4b518834cdeb93c1dc491325f9083ea7079c9644e4677ae86bb`; locator: DENVER HEALTH AND HOSPITAL AUTHORITY
- **FN9.S2** (FN9): I grouped it with public hospitals, universities, and nonprofits rather than with state and local governments, because it is a public health care provider rather than a general-purpose government.
  - The hospital grouping reflects a judgment about general-purpose government, not a property established by File C amounts alone.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Analyst classification choice
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_totals.csv`; SHA-256 `969ab13dfb93c4b518834cdeb93c1dc491325f9083ea7079c9644e4677ae86bb`; locator: DENVER HEALTH AND HOSPITAL AUTHORITY
- **FN10.S2** (FN10): USAspending.gov, About the Data, p. 12, https://www.usaspending.gov/data/about-the-data-download.pdf (accessed September 27, 2026).
  - Title/page match, but the historical September 27 access date was not independently logged by this task.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Recomputed or checked: Official About the Data PDF p. 12
  - Source: `data/raw/final_audit/usaspending_about_data.pdf`; SHA-256 `b3d4f5c6513daae90e496a522b0c44382be1fb25257e4d679528ba766252d321`; locator: 12
- **FN12.S1.C3** (FN12): across all accounts and award types.
  - The two DHS agency-scoped downloads contain Contracts, Assistance, and Unlinked members spanning 84 observed account symbols. Every returned row was scanned, which covers accounts with returned award rows for this search purpose; completeness of accounts with no returned rows is not independently established.
  - Proposed fix: Specify all account symbols and award-type members returned in the two downloads.
  - Recomputed or checked: 1,815,637 returned rows; 84 account symbols
  - Source: `audit/published_scope_recheck.json`; SHA-256 `3de783e682a4286bc1402405f1a8f889ed53beb3bf34648ecbae156091f86394`; locator: years and combined_account_symbols
- **FN14.S1** (FN14): U.S. Immigration and Customs Enforcement, “Notice of Intent to Sole Source – Torrance and Cibola,” SAM.gov, NOI-70CDCR26R00000014, March 10, 2026, https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view.
  - SAM official page did not yield notice text; source registration remains incomplete.
  - Proposed fix: Register an official SAM notice receipt or mark the exact posted-date/title claim as not yet verified.
  - Recomputed or checked: NOI-70CDCR26R00000014, reported posted 2026-03-10
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: sam_notice
  - [https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view](https://sam.gov/opp/ee796eb2d09b4216a30f6b15d9dd4a8d/view)
- **FN17.S1.C1** (FN17): DHS Office of Inspector General, Immigration and Custom Enforcement Detention Bedspace Management (April 2009)
  - DHS Office of Inspector General, Immigration and Custom Enforcement Detention Bedspace Management (April 2009): The footnote appears to append a trailing dash/punctuation to GAO title; verify final bibliography formatting.
  - Proposed fix: Correct GAO title punctuation; retain the OIG-09-52 title’s own “Custom Enforcement” wording.
  - Source: `data/raw/legal_sources/OIG-09-52.pdf`; SHA-256 `4da39febc61f0020dbaded586d80c04800f4652062d30cef848dc7ae43f894b1`; locator: 1
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: gao
- **FN17.S1.C2** (FN17): DHS Office of Inspector General, Immigration and Customs Enforcement Did Not Follow Federal Procurement Guidelines When Contracting for Detention Services, (February 21, 2018)
  - DHS Office of Inspector General, Immigration and Customs Enforcement Did Not Follow Federal Procurement Guidelines When Contracting for Detention Services, (February 21, 2018): The footnote appears to append a trailing dash/punctuation to GAO title; verify final bibliography formatting.
  - Proposed fix: Correct GAO title punctuation; retain the OIG-09-52 title’s own “Custom Enforcement” wording.
  - Source: `data/raw/legal_sources/OIG-09-52.pdf`; SHA-256 `4da39febc61f0020dbaded586d80c04800f4652062d30cef848dc7ae43f894b1`; locator: 1
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: gao
- **FN17.S1.C3** (FN17): DHS Office of Inspector General, ICE Does Not Fully Use Contracting Tools to Hold Detention Facility Contractors Accountable for Failing to Meet Performance Standards, OIG-19-18 (January 29, 2019)
  - DHS Office of Inspector General, ICE Does Not Fully Use Contracting Tools to Hold Detention Facility Contractors Accountable for Failing to Meet Performance Standards, OIG-19-18 (January 29, 2019): The footnote appears to append a trailing dash/punctuation to GAO title; verify final bibliography formatting.
  - Proposed fix: Correct GAO title punctuation; retain the OIG-09-52 title’s own “Custom Enforcement” wording.
  - Source: `data/raw/legal_sources/OIG-09-52.pdf`; SHA-256 `4da39febc61f0020dbaded586d80c04800f4652062d30cef848dc7ae43f894b1`; locator: 1
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: gao
- **FN17.S1.C4** (FN17): U.S. GAO, Immigration Detention: Actions Needed to Improve Planning, Documentation, and Oversight of Detention Facility Contracts (January 2021)
  - U.S. GAO, Immigration Detention: Actions Needed to Improve Planning, Documentation, and Oversight of Detention Facility Contracts (January 2021): The footnote appears to append a trailing dash/punctuation to GAO title; verify final bibliography formatting.
  - Proposed fix: Correct GAO title punctuation; retain the OIG-09-52 title’s own “Custom Enforcement” wording.
  - Source: `data/raw/legal_sources/OIG-09-52.pdf`; SHA-256 `4da39febc61f0020dbaded586d80c04800f4652062d30cef848dc7ae43f894b1`; locator: 1
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: gao
- **FN19.S1.C1** (FN19): Daily Iowan, Muscatine County Jail Releases ICE Contract, (March 4, 2026)
  - Daily Iowan, Muscatine County Jail Releases ICE Contract, (March 4, 2026): Daily Iowan was independently read; Iowa Capital Dispatch timed out in this web pass, though prior receipt exists.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: daily_iowan
  - [https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/](https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/)
  - Source: `provenance/claim_audit/source_receipts.json`; SHA-256 `c2114696ac4b7f8d1e9d620356d34b1ec622767e735c1268fe16142b02930554`; locator: iowa_capital_dispatch
- **FN19.S1.C2** (FN19): Iowa Capital Dispatch, ICE contract with Iowa jail increased funding for detentions by 75% (March 6, 2026)
  - Iowa Capital Dispatch, ICE contract with Iowa jail increased funding for detentions by 75% (March 6, 2026): Daily Iowan was independently read; Iowa Capital Dispatch timed out in this web pass, though prior receipt exists.
  - Proposed fix: Complete the source check identified in the reason, or narrow the wording to the evidence already linked.
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: daily_iowan
  - [https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/](https://dailyiowan.com/2026/03/04/muscatine-county-jail-releases-ice-contract/)
  - Source: `provenance/claim_audit/source_receipts.json`; SHA-256 `c2114696ac4b7f8d1e9d620356d34b1ec622767e735c1268fe16142b02930554`; locator: iowa_capital_dispatch
- **FN21.S1** (FN21): Analysis by Greg Constantine, published at https://www.readfrontier.org/31564-2/.
  - Citation is missing publication name and date; article page supports both.
  - Proposed fix: Add “The Frontier” and August 10, 2026 to the citation.
  - Recomputed or checked: The Frontier, Greg Constantine, Aug. 10, 2026
  - Source: `audit/web_receipts.json`; SHA-256 `1a75242e88ec27b51e29cebf424d9a520a8836e28751cea3a00153104c95ecd0`; locator: frontier
  - [https://www.readfrontier.org/31564-2/](https://www.readfrontier.org/31564-2/)

## Author-accepted wording

- **P15.A1** (P15): On April 30, the IGSAs expired
  - readability; author's assessment of the facts.
  - Accepted by: Kevin McNellis on 2026-09-27
  - Evidence and remaining limit: P00045 runs Torrance to April 30; Cibola was asked to end April 30; a reported county-manager account instead gives Torrance March 30. The locked Methodology discloses the difference. Author chose the short wording.
  - Source: `data/raw/ice_foia_torrance/70CDCR19DIG000009-P00045.pdf`; SHA-256 `4b8f3ec3b56729438d5264c9bb132bc35f88efc6943a53957dafd1cfe77d2774`; locator: 1
  - Source: `provenance/claim_audit/source_receipts.json`; SHA-256 `c2114696ac4b7f8d1e9d620356d34b1ec622767e735c1268fe16142b02930554`; locator: santa_fe_new_mexican
- **P20.A1** (P20): Secure America Act
  - readability; author's assessment of the facts.
  - Accepted by: Kevin McNellis on 2026-09-27
  - Evidence and remaining limit: The handoff recorded author acceptance before the enacted text was registered. Official P.L. 119-98 §1(a) now verifies this short title; acceptance remains a wording decision.
  - Source: `data/raw/final_audit/PLAW-119publ98.pdf`; SHA-256 `6c5bcb9dbb863f480ea6c833fee6c779ac735a8bc7e76d009e28e05a40076f09`; locator: 1
- **P20.A2** (P20): increased its IGSA payments
  - readability; author's assessment of the facts.
  - Accepted by: Kevin McNellis on 2026-09-27
  - Evidence and remaining limit: Muscatine agreement is a U.S. Marshals Service agreement with an ICE rider. The cited news reports an increased agreement cap, not verified paid amounts. Author retained wording.
  - Source: `provenance/claim_audit/source_receipts.json`; SHA-256 `c2114696ac4b7f8d1e9d620356d34b1ec622767e735c1268fe16142b02930554`; locator: daily_iowan/iowa_capital_dispatch
- **P61.A1** (P61): its three task orders. They carry $17,465,361.06
  - Claim checked: The author accepted the pronoun linking $17,465,361.06 to the preceding three-task-order sentence; the amount comes from two ICE orders, and the parent has a third DOJ order.
  - readability; author's assessment of the facts.
  - Accepted by: Kevin McNellis on 2026-09-27
  - Evidence and remaining limit: Parent USAspending API lists three children. The $17,465,361.06 selected File C object-class 25.4 amount is from ICE’s two direct orders; the USMS third order has $3,335,386 in separate DOJ-funded award obligations. Author retained wording.
  - Source: `data/raw/final_audit/torrance_parent_children.json`; SHA-256 `c24bad523e20525fe5c1ed9cc269b8d3464629f67f3a7c622babdad012a002ee`
  - Source: `data/raw/final_audit/usms_torrance_order.json`; SHA-256 `8dfd1f4a0a0d8167b97b3203b42c97801631f2861129e95004638c3de2da51fa`
  - Source: `outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`
- **FN1.A1** (FN1): Federal Funding Accountability and Transparency Act of 2006, § 2(a)(4), 31 U.S.C. 6101 note, (https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title31-section6101&num=0&edition=prelim).
  - Cites the section numbering of the current codified text (31 U.S.C. 6101 note, as amended by the DATA Act); §2(a)(2) is the numbering as enacted in 2006.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: The official 2024 U.S. Code note prints the Federal award definition at §2(a)(4), while P.L. 109-282 as enacted printed it at §2(a)(2).
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: If citing the 2006 enacted text, use §2(a)(2); retain §2(a)(4) only with the current-codified-text source layer.
  - Source: `data/raw/final_audit/USCODE-2024-title31-subtitleV-chap61-sec6101.pdf`; SHA-256 `1761d970ede891f1dcfb2b02d2c6b7068d02cd58ed4bdbc4d7e3446b083d2679`; locator: 5
  - Source: `data/raw/legal_sources/PLAW-109publ282.pdf`; SHA-256 `fac8d346dc31abfd839ef2cfc3230a115ebcf9020b82c10a99282e2f51e87cd1`; locator: 2
- **P7.A1** (P7): The inspector general concluded that ICE had “no assurance” it executed detention agreements in “the best interest of the Federal Government, taxpayers, or detainees."
  - Paraphrase; the OIG's wording ('detention center contracts') is in the linked report.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: OIG-18-53 printed pages 1 and 5 use detention center contracts; the published sentence says detention agreements.
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: For a verbatim account of the OIG conclusion, use detention center contracts.
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 8
- **P15.A2** (P15): required local governments to terminate their IGSAs.
  - Summary of HB 9 §3; the earliest-permissible-date condition is in the linked law.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: H.B. 9 §3(B) requires termination at the earliest permissible date under the agreement terms.
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: Add the earliest-permissible-date condition for statutory precision.
  - Source: `data/raw/final_audit/HB0009.pdf`; SHA-256 `2979b7c4afdbe16ebc16ce2efc2a6343a143d500e392cd8da28ea6e0c3df32a7`; locator: 2
- **P19.A1** (P19): including overpayments
  - Summary of OIG and GAO risk findings; the reports' 'may have overpaid' wording is in the linked sources.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: OIG-18-53 says ICE may have overpaid; the published phrase omits that uncertainty.
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: Say risk of overpayment or may have overpaid.
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 2
  - Source: `data/raw/legal_sources/OIG-18-53.pdf`; SHA-256 `14d9e0f3169dac9aaee3fef8f71bbf57960d072690368fc31f7bf1af28fda4b0`; locator: 25
  - Source: `data/raw/legal_sources/OIG-19-18.pdf`; SHA-256 `612201b03b540ccada067166fc9f2eb1c56bb342be0cdb11b2f9f0418c8144cf`; locator: 2
  - [https://www.gao.gov/assets/gao-21-149.pdf](https://www.gao.gov/assets/gao-21-149.pdf) (28)
- **P3.A1** (P3): From February 2025 through July 2026, ICE obligated $5.91 billion to operate and maintain detention facilities
  - The Methodology states that object class 25.4 is broader than detention.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: The $5.91 billion class 25.4 amount is verified; published Methodology P28 explicitly says the class covers more than detention.
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: Label the amount object class 25.4 rather than detention-only operating costs.
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P28
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_1/verification.json`; SHA-256 `9c0bacc3c12fc6e31bc36ec3ddc0e9bed60c2c20c98e60512e103f18d91ba0cb`; locator: analysis.bar_totals
  - Source: `data/raw/final_audit/omb_a11_2025.pdf`; SHA-256 `7b0e6a3b018f6beea1c4b55ff377821fbd16def96354df5b319b2642ecd604c1`; locator: 262
  - Source: `audit/independent_recomputation.json`; SHA-256 `2f33fbf81a316aecf5713753efbc7261fbb99b03771d8c6e3f12831af2d23a6d`; locator: fresh independent check
- **P31.A1** (P31): Each File C record carries the recipient's Unique Entity Identifier (UEI).
  - Methodology wording; the no-recipient rows are disclosed in the same section.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: Published Methodology P32 quantifies $9,498,809 in no-recipient rows, so each is not literally true across all File C rows.
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: Say linked File C records carry recipient UEIs; identify the no-recipient exception.
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P32
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/chart_2/recipient_type_totals.csv`; SHA-256 `5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c`; locator: No recipient reported
- **P48.A1** (P48): Of that, $78,730,777 went to the three facilities ICE also listed under a federal or contract type.
  - Methodology wording; the section's Limits paragraph says a name match is not a facility allocation.
  - Accepted by: Kevin McNellis on 2026-09-28
  - Evidence and remaining limit: Published Methodology P46 sums each matched award once and P50 says a name match does not identify the agreement; the $78,730,777 is not allocated to facilities.
  - Decision source: Kevin instruction relayed by coordinator task 01a0d96a-2d4d-7da3-bb3a-547d61e6b45a on 2026-09-28
  - Proposed fix: Say $78,730,777 in matched awards named three facilities rather than went to those facilities.
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P46
  - Source: `data/raw/final_audit/published_page/2026-09-28T13-23-41Z.text.json`; SHA-256 `cee9b354cf225abaad7cb481bb172dacaf15b7bb8dd87d422e7f1be869e9c815`; locator: P50
  - Source: `data/raw/final_audit/canonical_snapshots/File_C_blog_post/outputs/facility_name_screen/statistics_check.json`; SHA-256 `efc5accc11a86a8cc0d557623f247a893199f3692937f353f193d3c828e5b7b9`; locator: actual.iga_not_solely_25_4_amount
  - Source: `audit/facility_screen_recheck.json`; SHA-256 `1ea3fd6e44c60fbb2973c154480512864c264d4cf478cba8bc3ffec4fc7b0a17`; locator: fresh read-only rerun

## Full inventory

| ID | Status | Written values | Source count |
|---|---|---|---:|
| TITLE.S1 | WARN |  | 1 |
| SUBTITLE.S1 | WARN |  | 1 |
| P1.S1 | WARN |  | 2 |
| P1.S2 | WARN | 2026, 57%, July 2026 | 1 |
| P2.S1 | PASS | 2009 | 1 |
| P2.S2.C1 | PASS |  | 2 |
| P2.S2.C2 | PASS |  | 2 |
| P2.S3.C1 | WARN | 2015, 2018, only two occasions | 2 |
| P2.S3.C2 | WARN |  | 2 |
| P2.S4 | PASS | millions of dollars a month on unused detention beds. | 2 |
| P2.S5.C1 | PASS |  | 2 |
| P2.S5.C2 | PASS |  | 2 |
| P2.S5.C3 | PASS |  | 2 |
| P3.S1 | WARN |  | 2 |
| P3.S2 | PASS |  | 2 |
| P3.S3.C2 | WARN | $3.14 billion | 3 |
| P3.S4 | PASS | 98% | 4 |
| P3.S5 | PASS | $28,520 | 2 |
| P4.S1 | PASS |  | 2 |
| P4.S2.C1 | WARN | $17.5 million | 4 |
| P4.S2.C2 | WARN | 2026, April 2026 | 4 |
| P4.S3 | WARN |  | 2 |
| P5.S1 | WARN |  | 2 |
| P5.S2 | WARN | 7%, $5.4 billion | 2 |
| P5.S3 | WARN |  | 2 |
| P6.S1 | WARN |  | 3 |
| P6.S2.C1 | PASS | federal award, | 2 |
| P6.S2.C2 | PASS | grants, subgrants, loans, awards, cooperative agreements, and other forms of financial assistance, | 2 |
| P6.S2.C3 | PASS | contracts, subcontracts, purchase orders, task orders, and delivery orders. | 2 |
| P6.S3.C1 | PASS | 2018, are not grants, | 1 |
| P6.S3.C2 | PASS | has not formally defined IGSAs as cooperative agreements or procurement contracts | 1 |
| P7.S1 | PASS | 1996 | 1 |
| P7.S2 | PASS | housing, care, and security of persons detained, under an agreement with a State or political subdivision of a State. | 1 |
| P7.S3 | WARN |  | 1 |
| P7.S4.C1 | PASS | exempt from the Competition in Contracting Act and FAR [Federal Acquisition Regulations], | 2 |
| P7.S4.C2 | PASS |  | 2 |
| P7.S4.C3 | PASS | a form of fixed-price, indefinite quantity, indefinite delivery type contract. | 2 |
| P8.S1 | PASS |  | 1 |
| P8.S2 | WARN | 2026, 168, 208, 81%, July 2026 | 3 |
| P8.S3.C1 | PASS | 104 | 3 |
| P8.S3.C2 | PASS | 38 | 3 |
| P8.S3.C3 | PASS | 26 | 3 |
| P8.S4 | PASS | 57% | 2 |
| P9.S1 | WARN |  | 1 |
| P9.S2 | PASS |  | 1 |
| P9.S3.C1 | PASS |  | 1 |
| P9.S3.C2 | PASS | object class, | 1 |
| P9.S4 | PASS |  | 2 |
| P9.S5.C1 | WARN |  | 3 |
| P9.S5.C2 | WARN |  | 3 |
| P9.S6 | WARN |  | 3 |
| P10.S1 | WARN |  | 2 |
| P10.S2 | WARN |  | 1 |
| P10.S3 | WARN | 2025, 2026, $3.14 billion, 74, February 2025, July 2026, operating and maintaining facilities | 3 |
| P10.S4 | PASS | 98% | 3 |
| P10.S5.C1 | PASS |  | 2 |
| P10.S5.C2 | PASS | $28,520 | 2 |
| P11.S1 | WARN |  | 1 |
| P11.S2 | WARN |  | 2 |
| P11.S3 | WARN |  | 1 |
| P11.S4 | WARN | 2026, 58%, July 2026 | 1 |
| P11.S5.C1 | WARN |  | 1 |
| P11.S5.C2 | WARN |  | 1 |
| P11.S6.C1 | WARN |  | 1 |
| P11.S6.C2 | WARN |  | 1 |
| P12.S1 | PASS | 2025, 2026, January 2025, July 2026 | 2 |
| P12.S2.C1 | WARN |  | 1 |
| P12.S2.C2 | WARN |  | 1 |
| P13.S1 | PASS |  | 2 |
| P13.S2 | PASS | 21, 49, service processing centers, contract | 2 |
| P13.S3 | PASS | $2.23 billion, 71%, $3.14 billion | 2 |
| P13.S4 | PASS | 224 | 2 |
| P13.S5 | PASS | $96 million, 3% | 2 |
| P13.S6 | PASS |  | 2 |
| P13.S7 | PASS | $17.5 million | 2 |
| P13.S8 | PASS |  | 1 |
| P13.S9 | WARN |  | 1 |
| P14.S1 | WARN | $17.5 million | 2 |
| P14.S2.C1 | WARN |  | 2 |
| P14.S2.C2 | WARN |  | 2 |
| P14.S2.C3 | WARN | 2016, October 2016 | 2 |
| P14.S2.C4 | WARN | 2019, May 2019 | 2 |
| P14.S3 | WARN | 2025, 2026 | 2 |
| P14.S4 | WARN | 2024, October 2024 | 2 |
| P15.S1.C1 | WARN | 2026, February 2026 | 1 |
| P15.S1.C2 | WARN |  | 1 |
| P15.S2 | WARN |  | 2 |
| P15.S3.C2 | WARN |  | 3 |
| P15.S4 | WARN | $17.5 million | 2 |
| P16.S1 | WARN |  | 2 |
| P17.S1 | WARN | 2025, 2026, $4.8 billion, February 2025, July 2026 | 2 |
| P17.S2 | WARN |  | 2 |
| P18.S1.C1 | WARN |  | 2 |
| P18.S1.C2 | WARN |  | 2 |
| P18.S2 | WARN |  | 2 |
| P19.S1.C1 | WARN |  | 4 |
| P19.S1.C3 | WARN |  | 4 |
| P19.S1.C4 | WARN | millions of dollars a month on unused detention beds. | 4 |
| P19.S2 | PASS |  | 2 |
| P19.S3.C1 | PASS | 2018, to acquire beds quickly and in remote locations, | 2 |
| P19.S3.C2 | PASS | noncompetitively, | 2 |
| P19.S3.C3 | PASS | free to take advantage of the broad flexibilities afforded by its IGSA authority to modify the terms of the original agreement. | 2 |
| P20.S1.C1 | WARN |  | 1 |
| P20.S3.C1 | WARN | 75% | 2 |
| P20.S3.C2 | WARN | public disclosures. | 2 |
| P20.S4 | WARN |  | 2 |
| P20.S5.C1 | WARN | $2.0 million, 2025, October 2025 | 2 |
| P20.S5.C2 | WARN |  | 2 |
| P20.S5.C3 | WARN | $8.3 million, 2026, March 2026 | 2 |
| P21.S1 | WARN |  | 0 |
| P21.S2.C1 | WARN |  | 2 |
| P21.S2.C2 | WARN |  | 2 |
| P21.S3 | PASS |  | 2 |
| P21.S4 | WARN |  | 0 |
| P22.S1.C1 | WARN |  | 1 |
| P22.S1.C2 | WARN | 2026, September 2026 | 1 |
| P23.S1 | WARN |  | 0 |
| P23.S2 | WARN |  | 0 |
| P23.S3.C1 | WARN |  | 0 |
| P23.S3.C2 | WARN |  | 0 |
| P23.S3.C3 | WARN |  | 0 |
| P23.S4.C1 | WARN |  | 0 |
| P23.S4.C2 | WARN |  | 0 |
| P23.S4.C3 | WARN |  | 0 |
| P23.S5 | WARN |  | 0 |
| P23.S6 | WARN |  | 1 |
| P24.S1 | PASS |  | 1 |
| P24.S2 | PASS |  | 1 |
| P25.S1 | PASS | Account Breakdown by Program Activity & Object Class | 1 |
| P25.S2 | PASS |  | 1 |
| P26.S1 | PASS | Account Breakdown by Award | 1 |
| P26.S2.C1 | WARN |  | 3 |
| P26.S2.C2 | WARN |  | 3 |
| P27.S1.C1 | PASS | 4, 12 | 1 |
| P27.S1.C2 | PASS | 10 | 1 |
| P27.S2 | PASS | 12, 10 | 1 |
| P27.S3 | PASS | 15, 16, 23, 2026, September 15 | 1 |
| P28.S2 | PASS | 070, 0540, 070, 0545 | 1 |
| P28.S3 | PASS | 25.4, operation and maintenance of facilities. | 1 |
| P28.S4 | PASS | when done by contract with the private sector or another Federal Government account. | 1 |
| P28.S5 | PASS |  | 1 |
| P29.S2 | PASS | 2025, 2026, February 2025, July 2026 | 1 |
| P29.S3 | PASS |  | 2 |
| P29.S4 | PASS | 2025, 2025, January 2025, September 2025 | 1 |
| P29.S5 | PASS |  | 1 |
| P29.S6 | PASS |  | 2 |
| P29.S7 | PASS | 2 | 1 |
| P29.S8 | PASS |  | 1 |
| P30.S2.C1 | PASS | 25.4, $5.91 billion | 2 |
| P30.S2.C2 | PASS | $3.14 billion | 2 |
| P30.S3 | PASS | $2.77 billion | 2 |
| P30.S4 | PASS |  | 1 |
| P31.S3 | WARN |  | 2 |
| P32.S2 | WARN | $3.14 billion | 3 |
| P32.S3.C1 | PASS | 74, $3,127,031,939 | 3 |
| P32.S3.C2 | PASS | $9,498,809 | 3 |
| P32.S4 | PASS |  | 2 |
| P32.S5 | WARN | 23, 2026, September 23, 2026 | 2 |
| P33.S1.C1 | PASS |  | 3 |
| P33.S1.C2 | PASS | $3,080,063,270 | 3 |
| P33.S1.C3 | PASS | 98% | 3 |
| P33.S2 | PASS |  | 1 |
| P33.S3.C1 | PASS | $250 | 2 |
| P33.S3.C2 | PASS |  | 2 |
| P34.S1 | PASS |  | 2 |
| P34.S2.C1 | WARN | 70, 70 | 2 |
| P34.S2.C2 | WARN | $18,000, $14,580 | 2 |
| P34.S3 | PASS | 70, $4,060 | 1 |
| P34.S4 | PASS | $28,520 | 2 |
| P34.S5 | WARN |  | 1 |
| P34.S6 | PASS | $2,000 | 1 |
| P35.S2 | PASS |  | 2 |
| P35.S3 | WARN | 9, 2026, 20, 2026, July 9, 2026, July 20, 2026, Facilities FY26 | 2 |
| P36.S2.C1 | PASS | 38, IGSA facilities | 2 |
| P36.S2.C2 | PASS | 26 | 2 |
| P36.S2.C3 | PASS | 104 | 2 |
| P36.S3 | PASS | 168, 208, 81% | 2 |
| P36.S4.C1 | PASS |  | 2 |
| P36.S4.C2 | PASS |  | 2 |
| P37.S1 | PASS |  | 2 |
| P37.S2 | PASS | 9, July 9 | 2 |
| P37.S3.C1 | PASS | 168 | 2 |
| P37.S3.C2 | PASS | 35,791, 62,517 | 2 |
| P37.S3.C3 | PASS | 57% | 2 |
| P38.S1 | PASS |  | 1 |
| P38.S2 | PASS |  | 3 |
| P38.S3 | WARN |  | 2 |
| P39.S2 | WARN | 11, 2026, September 11, 2026 | 1 |
| P39.S3 | WARN | 9, 57.8%, July 9 | 1 |
| P39.S4.C1 | WARN | 50.5% | 1 |
| P39.S4.C2 | WARN | 42.9% | 1 |
| P40.S2 | PASS |  | 3 |
| P40.S3 | PASS | 271, 21, 2025, 9, 2026, January 21, 2025, July 9, 2026 | 3 |
| P40.S4 | WARN |  | 1 |
| P41.S2 | PASS |  | 1 |
| P42.S1 | PASS | 49 | 2 |
| P43.S1 | PASS | 224 | 2 |
| P44.S1 | PASS |  | 2 |
| P44.S2 | PASS |  | 1 |
| P44.S3 | PASS |  | 1 |
| P45.S2.C1 | PASS |  | 1 |
| P45.S2.C2 | PASS |  | 1 |
| P45.S3 | PASS | 15, T Don Hutto. | 2 |
| P45.S4.C1 | PASS |  | 1 |
| P45.S4.C2 | PASS |  | 1 |
| P46.S2 | PASS | 25.4 | 3 |
| P47.S1.C1 | PASS | 21, 76 | 2 |
| P47.S1.C2 | PASS | $2,229,581,023 | 2 |
| P47.S1.C3 | PASS | 71%, $3.14 billion | 2 |
| P48.S1.C1 | PASS | 5, 12 | 2 |
| P48.S1.C2 | PASS | $96,196,138.33 | 2 |
| P48.S1.C3 | PASS | 3% | 2 |
| P49.S1.C1 | PASS |  | 2 |
| P49.S1.C2 | PASS |  | 2 |
| P49.S1.C3 | PASS | $17,465,361.06 | 2 |
| P50.S2 | PASS |  | 1 |
| P50.S3 | PASS |  | 1 |
| P50.S4 | PASS |  | 2 |
| P51.S2 | PASS |  | 3 |
| P52.S1 | PASS | 70, 15, 2019, May 15, 2019 | 1 |
| P53.S1 | PASS | 17, 0003, 28, 2016, October 28, 2016 | 2 |
| P54.S1 | PASS |  | 1 |
| P54.S2.C1 | PASS |  | 1 |
| P54.S2.C2 | PASS |  | 1 |
| P55.S2 | WARN |  | 2 |
| P56.S1 | PASS |  | 4 |
| P57.S1 | PASS | 70, 70 | 3 |
| P58.S1 | PASS |  | 3 |
| P59.S1 | PASS |  | 2 |
| P60.S1.C1 | PASS |  | 2 |
| P60.S1.C2 | PASS | 0 | 2 |
| P60.S2 | WARN |  | 2 |
| P60.S3 | WARN |  | 1 |
| P60.S4 | WARN | 26, 27, 2026, September 26 | 2 |
| P61.S2 | PASS | 70 | 2 |
| P61.S3.C2 | PASS | 25.4, 2026, July 2026 | 2 |
| P61.S3.C3 | PASS | $9,023,550.00 | 2 |
| P61.S3.C4 | PASS | $8,441,811.06 | 2 |
| P61.S4 | WARN | $708,458.18 | 2 |
| P61.S5.C1 | PASS | 27, 2026, $22,869,719.24, September 27, 2026 | 2 |
| P61.S5.C2 | PASS | $4,695,900, 2026, August 2026 | 2 |
| P61.S6 | WARN | 70 | 2 |
| P62.S1 | PASS | 0540 | 1 |
| P62.S2 | PASS | 2025, 2026, February 2025, July 2026 | 2 |
| P63.S1 | PASS | 25.4 | 1 |
| P64.S1 | PASS | 31.0 | 1 |
| P65.S1 | PASS | 21.0 | 1 |
| P66.S1 | PASS | 25.2 | 1 |
| P67.S1 | PASS |  | 1 |
| P67.S2 | WARN | $4.8 billion | 2 |
| P67.S3 | WARN |  | 1 |
| P67.S4 | WARN |  | 2 |
| P67.S5 | PASS |  | 1 |
| FN1.S1.C2 | PASS | $25,000 | 1 |
| FN2.S1 | WARN | 2018, February 2018 | 1 |
| FN3.S1 | PASS | 104, 208, 373, 30, 1996, September 30, 1996, Public Law 104-208, §373 | 1 |
| FN4.S1 | WARN | 2018, February 2018 | 1 |
| FN5.S1 | PASS |  | 1 |
| FN5.S2 | WARN | 2019, 2021 | 2 |
| FN5.S3 | PASS | 2021, January 2021 | 2 |
| FN6.S1.C1 | WARN | 20, 2026, July 20, 2026, Facilities FY26 | 2 |
| FN6.S1.C2 | WARN |  | 2 |
| FN7.S1 | PASS |  | 1 |
| FN7.S2 | PASS |  | 1 |
| FN7.S3.C1 | PASS |  | 2 |
| FN7.S3.C2 | PASS | 11, 83 | 2 |
| FN7.S4 | WARN |  | 2 |
| FN7.S5 | PASS |  | 2 |
| FN8.S1.C1 | PASS | 10, $1.01 billion | 2 |
| FN8.S1.C2 | PASS | $598 million | 2 |
| FN8.S1.C3 | PASS | $460 million | 2 |
| FN8.S1.C4 | PASS | $453 million | 2 |
| FN8.S1.C5 | PASS | $281 million | 2 |
| FN8.S1.C6 | PASS | $99 million | 2 |
| FN8.S1.C7 | PASS | $91 million | 2 |
| FN8.S1.C8 | PASS | $60 million | 2 |
| FN8.S1.C9 | PASS | $19 million | 2 |
| FN8.S1.C10 | PASS | $8 million | 2 |
| FN8.S2 | WARN |  | 1 |
| FN8.S3 | WARN |  | 1 |
| FN8.S4 | PASS | $250 | 3 |
| FN9.S1 | WARN |  | 1 |
| FN9.S2 | WARN |  | 1 |
| FN9.S3 | PASS | $2,000, 70 | 1 |
| FN9.S4 | PASS | $30,520 | 3 |
| FN10.S1.C1 | PASS | maintaining data quality for the award description field has been persistently challenging for federal agencies, | 1 |
| FN10.S1.C2 | PASS | lack meaningful information altogether. | 1 |
| FN10.S2 | WARN | 12, 27, 2026, September 27, 2026 | 1 |
| FN11.S1.C1 | PASS | 17, 0003, 28, 2016, October 28, 2016 | 2 |
| FN11.S1.C2 | PASS | 70, 15, 2019, May 15, 2019 | 2 |
| FN12.S1.C1 | PASS | 1, 12, 16, 2026, September 16, 2026 | 1 |
| FN12.S1.C2 | PASS | 1, 10, 15, 2026, September 15, 2026 | 1 |
| FN12.S1.C3 | WARN |  | 1 |
| FN12.S2.C1 | PASS | 70, 17, 0003 | 2 |
| FN12.S2.C2 | PASS | 70, 70 | 2 |
| FN12.S2.C3 | PASS |  | 2 |
| FN12.S2.C4 | PASS |  | 2 |
| FN12.S2.C5 | PASS |  | 2 |
| FN13.S1 | PASS | 9, 2026, 5, 3, H.B. 9, § 3 | 1 |
| FN14.S1 | WARN | 70, 10, 2026, March 10, 2026, Notice of Intent to Sole Source – Torrance and Cibola, | 2 |
| FN15.S1.C1 | PASS | 70 | 1 |
| FN15.S1.C2 | PASS | 30, 2026, April 30, 2026 | 1 |
| FN15.S1.C3 | PASS | detention and transportation support services at the Torrance and Cibola detention facilities, | 1 |
| FN16.S1 | PASS | 21.0 | 1 |
| FN16.S2 | PASS | 11, 83, 25.4, when done by contract with the private sector or another Federal Government account, | 1 |
| FN17.S1.C1 | WARN | 2009, April 2009 | 2 |
| FN17.S1.C2 | WARN | 21, 2018, February 21, 2018 | 2 |
| FN17.S1.C3 | WARN | 19, 18, 29, 2019, January 29, 2019 | 2 |
| FN17.S1.C4 | WARN | 2021, January 2021 | 2 |
| FN18.S1 | PASS | 21, 2018, February 21, 2018 | 1 |
| FN19.S1.C1 | WARN | 4, 2026, March 4, 2026 | 3 |
| FN19.S1.C2 | WARN | 75%, 6, 2026, March 6, 2026 | 3 |
| FN20.S1 | PASS | $2.3, 9, 2026, February 9, 2026 | 2 |
| FN21.S1 | WARN |  | 2 |
| P15.A1 | ACCEPTED_BY_AUTHOR | 30, April 30 | 2 |
| P20.A1 | ACCEPTED_BY_AUTHOR |  | 1 |
| P20.A2 | ACCEPTED_BY_AUTHOR |  | 1 |
| P61.A1 | ACCEPTED_BY_AUTHOR | $17,465,361.06 | 3 |
| FN1.A1 | ACCEPTED_BY_AUTHOR | 2006, 2, 4, 31, 6101, § 2(a)(4), 31 U.S.C. 6101 | 2 |
| P7.A1 | ACCEPTED_BY_AUTHOR | no assurance, the best interest of the Federal Government, taxpayers, or detainees. | 1 |
| P15.A2 | ACCEPTED_BY_AUTHOR |  | 1 |
| P19.A1 | ACCEPTED_BY_AUTHOR |  | 4 |
| P3.A1 | ACCEPTED_BY_AUTHOR | 2025, 2026, $5.91 billion, February 2025, July 2026 | 4 |
| P31.A1 | ACCEPTED_BY_AUTHOR |  | 2 |
| P48.A1 | ACCEPTED_BY_AUTHOR | $78,730,777 | 4 |
