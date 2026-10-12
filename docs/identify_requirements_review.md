# Identify requirement candidate review

This is a review queue, not confirmed specification knowledge. The extraction
contains 2,077 mechanically collected source passages and 20 source-read curated
candidates. These original queue records remain non-executable and unapproved. A separate stage-5 candidate package maps the focused subset to executable rules; see [coverage](nvme_requirement_coverage.md). Counts are extraction output, not a
count of independent NVMe requirements. No product expected values are supplied.

## Inputs and scope

| Document ID | Revision | Physical PDF pages |
| --- | --- | ---: |
| BASE_2_0E | NVMe Base 2.0e, 2024-07-29 | 467 |
| BASE_2_1 | NVMe Base 2.1, 2024-08-05 | 707 |
| NVM_1_0E | NVM Command Set 1.0e, 2024-07-29 | 107 |
| NVM_1_1 | NVM Command Set 1.1, 2024-08-05 | 156 |

Sources are the four user-provided PDFs. Before any fixed-page scan, the
extractor verifies all four SHA256 hashes against `candidates/nvme/catalog.json`.
The output's `document_hashes` mapping binds its evidence to those exact registry
entries; the compiler can reject a candidate/registry mismatch even when PDFs
are absent. This proves source-byte identity, not interpretation correctness.
The extractor refuses outputs in `generated/`, non-JSON files, source PDFs and
the registry itself. Bundle comparisons are Base 2.0e + NVM 1.0e and Base 2.1 + NVM 1.1;
revision numbers never imply an automatically selected counterpart.

Scope is CNS 00h, 01h, 05h, 06h and 08h, including embedded LBA format and
power-state structures. A CNS is not an exclusive document owner: NVM1.0e
section 4.1.5.2 Figure 99 and NVM1.1 section 4.1.5.2 Figure 117 define fields
within the Base Identify Controller structure. Base separately defines CNS08.
Boundary pages also contain adjacent out-of-scope structures; these remain
explicitly unresolved until individual passages are assigned or excluded.

Core physical PDF page ranges captured in full:

| Document | CNS01 | CNS00 | CNS05 | CNS06 | CNS08 |
| --- | --- | --- | --- | --- | --- |
| BASE_2_0E | 262–288 | NVM document | 291 | 291 | 291–294 |
| BASE_2_1 | 321–353 | NVM document | 355–356 | 356 | 356–360 |
| NVM_1_0E | 65–66 | 56–65 | 66–68 | 68–70 | Base document |
| NVM_1_1 | 90–92 | 79–90 | 92–98 | 98–103 | Base document |

Physical PDF pages and printed page numbers are different in Base2.1. For
example physical page 357 is printed page 335. Evidence stores both where the
printed number is extractable. Evidence section UNKNOWN means no verified
section anchor; it is not filled using a guessed nearest heading.

## Reproduce and understand the queue

Run with Python containing `pypdfium2`:

```powershell
python tools/extract_identify_requirements.py --pdf-dir ..
```

The default output is `candidates/nvme/requirements.json`. It is isolated from
production knowledge and generated snapshots. The extractor does not invoke a
model, resolve rules, promote status, or execute SSD commands. It records all
1,437 physical pages in a coverage ledger and scans beyond the structure tables
for Identify mentions, known field acronyms and headings targeted by explicit
section references. This deliberately broad search includes false positives.

`EXCERPT` IDs identify deterministic source passages grouped by page. They
preserve wording, including SHALL, MAY and SHOULD. A passage can contain several
requirements, unrelated table columns, preceding conditions, or incomplete
continuations. Lexical classification is triage only: mixed modalities become
`unresolved`; a `mandatory` label alone never permits execution. Field acronyms
and structure links also need review. `condition: null` on these records means
not parsed, not unconditional. Search hits outside verified core ranges have an
empty structure list and UNKNOWN section until assigned by a reviewer.

`CURATED` IDs contain small source-read interpretations with explicit predicate
text. They have exactly the same candidate and unresolved evaluation status.
They overlap the original excerpts rather than replacing or promoting them.
Matching suffixes across versions suggest review pairs, never automatic rule
equivalence. New PDF bytes or an extraction algorithm change require renewed
review; page/excerpt IDs are not immutable normative requirement IDs.

Coverage status `unresolved` means passages were captured but semantic/layout
review is incomplete. `excluded` is a front-matter or negative lexical-screen
decision, not proof the page contains no relevant requirement. No page is marked
fully extracted or reviewed. Reference closure, visual table verification and
exhaustive normative coverage are outstanding.

## Curated review pairs and material distinctions

| CURATED suffix | NVM1.0e source | NVM1.1 source | Review concern |
| --- | --- | --- | --- |
| CAPACITY_ORDER | §2.1.1 p10 | §2.1.1 p12 | NSZE >= NCAP >= NUSE; relational, not a fixed product number |
| THINP_ZERO_NCAP | §2.1.1 p10 | §2.1.1 p12 | THINP=0 requires NCAP=NSZE |
| THINP_ZERO_NUSE_PERMISSION | §2.1.1 p10 | §2.1.1 p12 | NUSE=NCAP is permitted, not required |
| THINP_TRACKING | §2.1.1 p10 | §2.1.1 p12 | Allocation tracking is behavior; a single response is insufficient |
| ANA_ZERO_REPORTING | §2.1.1 p11 | §2.1.1 p13 | Needs Base CMIC support and controller/namespace ANA state |
| METADATA_ABSENT | §4.1.5.1 Fig98 p65 | §4.1.5.1 Fig116 p90 | MS=0 under no-metadata condition; not a Reserved rule |
| LBADS_NONZERO_MINIMUM | §4.1.5.1 Fig98 p65 | §4.1.5.1 Fig116 p90 | Preserve exponent encoding and zero unavailable sentinel |
| ALL_NS_UNSUPPORTED | §4.1.5.1 p56 | §4.1.5.1 p80 | Without Namespace Management, NSID=FFFFFFFFh: SHALL abort becomes MAY abort |
| AWUPF_BOUND | §2.1.4 Fig4 p12 | §2.1.4.1 Fig4 p14 | Parameter-supported footnote; newer table is Single Atomicity Mode |
| NAWUN_BASELINE | §2.1.4 Fig4 p12 | §2.1.4.1 Fig4 p14 | Controller/namespace relationship and newer mode applicability |

Other priority source passages include NVM1.0e Figure97 p58 (NLBAF depends on
Base Host Behavior Support LBAFEE), NVM1.1 Figure114 p80 (Reported column for
the all-namespaces capability response), and NVM1.1 §2.1.4 pp14–16 (Single and
Multiple Atomicity Mode). A product-only context cannot resolve those cases:
query CNS/CSI/NSID, feature state, namespace format and runtime state may matter.

## Review and promotion procedure

### Priority review ledger for the rule execution pilot

On 2026-10-11, AI source comparison rechecked the following passages in the pinned
local PDFs. All four PDF hashes match the registry. Atomicity Figure 4 was also
rendered and visually compared in both revisions. This is not human approval,
confirmed promotion, exhaustive cross-reference closure or production execution.

| Interpretation | Bundle and source (physical PDF page) | Conditions / remaining dependencies | Runtime treatment |
| --- | --- | --- | --- |
| NSZE >= NCAP >= NUSE | Base 2.0e + NVM 1.0e §2.1.1 p10; Base 2.1 + NVM 1.1 §2.1.1 p12 | Same namespace/query instance; namespace and ANA-state reporting exceptions still require closure | Relational candidate; analogous synthetic field comparisons tested |
| THINP=0 requires NCAP=NSZE | Same sources as capacity ordering | THINP from NSFEAT, same namespace, query applicability | Actual-bit conditional equality candidate; synthetic analog tested |
| THINP=0 permits NUSE=NCAP | Same sources as capacity ordering | MAY is permission, not required equality; allocation tracking is behavior | REVIEW, no mandatory equality generated |
| LBADS=0 is unavailable; nonzero below 9 is unsupported | NVM 1.0e §4.1.5.1 Fig98 p65; NVM 1.1 Fig116 p90 | LBA format index; exponent is raw encoded value; availability refers to NLBAF in 1.0e and §5.5 in 1.1 | Candidate; indexed fixture tests cover nonzero gate/range and zero exclusion |
| AWUPF <= AWUN | NVM 1.0e §2.1.4 Fig4 p12; NVM 1.1 §2.1.4.1 Fig4 p14 | Table footnote applies when parameter supported; 1.1 table is explicitly Single Atomicity Mode; support/mode dependency resolution remains outstanding | Conditional relational candidate; missing support facts yield UNKNOWN in fixture analog |

The actual candidate records remain unchanged and non-executable. Fixture registry
offsets, CNS values, capability requirements and reviewer identity are clearly synthetic;
their confirmed label authorizes fixture tests only. Actual NVMe/OCP/MFND requirements
require independent document evidence and human review. OCP/MFND source versions have
not been supplied for this pilot, so no real requirements are inferred.

The next extraction priority is requirements → applicability/exception → Capability →
NVMe field/bit, not another complete structure extraction. Reviewers should approve
atomic interpretations and mappings, using the structure catalog as supporting evidence.
See [the implemented fixture pilot and follow-up sequence](rule_execution_pilot.md).

1. Open the pinned PDF at each physical page; compare table columns, notes,
   continuations and the preceding/following text. Preserve document revision,
   printed page, section, figure and exact source span.
2. Split passages into atomic statements and distinguish mandatory constraints,
   recommendations, permissions, descriptive encodings and command behavior.
   Determine the actor: host advice does not become a controller requirement.
3. Assign exact structure and field paths, including CNS/CSI and repeated entry
   instance semantics. Record applicable query, controller type, namespace
   state, optional-feature gates and exceptions. Do not assume missing conditions
   are false. Do not derive expected zero merely from Reserved or unsupported.
4. Follow each explicit and implicit dependency into the paired document.
   Record resolved anchors or an explicit UNKNOWN blocker. Detect conflicting
   clauses instead of overwriting one. Multiple sources extending the same field
   do not automatically establish precedence or override authority.
5. Review version pairs separately. A constant, offset, modality or applicability
   change needs its own evidence. An unchanged suffix is not approval to inherit.
6. Record reviewer identity, decision and source evidence through the project's
   review/promotion workflow before writing confirmed human-managed knowledge.
   Unsupported expressions and dynamic dependencies remain non-executable even
   if the source interpretation is approved. Build snapshots only from eligible
   confirmed sources according to the approved workflow.

Acceptance checks should cover mandatory versus MAY/SHOULD, Reserved versus
conditional zero, cross-field constraints, zero-based/exponent encodings,
missing runtime dependencies, query-dependent response semantics, mixed-document
field definitions, exact source pins, duplicate IDs, and the known SHALL/MAY
and Single Atomicity Mode version differences. Full extraction completeness
must be established by the review ledger, not record count or keyword matches.

## Stage 5 source-read closure

The separate executable package follows the same pinned four PDFs and does not promote the curated queue.
CNS01 AWUPF ≤ AWUN is mandatory in NVM1.0e p66 Fig99 and NVM1.1 p91 Fig117 field definitions.
This closes the earlier Controller-context ambiguity; the Namespace Figure4 subset still preserves
NSABP, zero inheritance and the newer Single Atomicity/MAM scope. THINP NUSE equality remains MAY.
Source anchors, executable conditions, exceptions, dependencies and deferred behavior checks are listed
in [the stage-5 ledger](nvme_requirement_coverage.md). No reviewer or confirmed status was invented.
OCP2_6.pdf is available for a subsequent stage; OCP/MFND rules were not added in stage 5.

## 프로젝트 완성 계획 6단계: 추가 규격 연결 (2026-10-12)

[추가 규격 계약과 적용 범위](supplemental_requirements.md)에 따라 OCP DSSD2.6 원문 hash와
요구 ID를 보존하여 두 Bundle의 요구사항 → Capability → NVMe Field/Bit 및 직접 제약을
candidate로 등록한다. 제품 Profile에 명시적으로 연결한 정책과 적용 Context만 실행하며
실제 제품값·적용 대상·FW를 추정하지 않는다. MFND는 사용자 지시로 제외한다.
기존 엔진의 충돌·단일 명시적 override와 원래/대체 규칙·검토 근거를 trace로 연결한다.
실제 제품 바인딩과 정책 자료, 기타 OCP 요구·동작 검사는 등록 대기/미구현으로 구분한다.
