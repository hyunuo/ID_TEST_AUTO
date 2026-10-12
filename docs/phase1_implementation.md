# Phase 1 Implementation Contracts

The architecture source of truth remains `ssd_nvme_validation_system_design.md` and `AGENTS.md`.
This document records implementation choices for the requested Phase 1 subset; it does not replace the SDS.

## Scope

Implemented: Pydantic v2 contracts, source YAML loading and validation, explicit linear spec inheritance,
guarded schema/requirement deltas, effective snapshots, provenance, manifests, structural diffs,
`knowledge build` / `spec diff`, unit/integration/golden tests.

Original subset exclusions (historical): Product Profile selection, production DUT Rule Resolver, DERIVED/LOOKUP execution, SQLite,
Capability Mapping execution, collectors, actual SSD validation, Excel, Confluence, AI/RAG, production knowledge.
Those components are outside the user's explicit implementation scope, even where the SDS describes a broader Phase 1.

## Source format

Every YAML document has a `kind`: `catalog`, `base`, or `delta`.
Unknown document kinds and properties are errors; unsupported knowledge is never silently ignored.
Source YAML uses `data_kind: fixture` or `data_kind: production` explicitly.
No production data ships with this implementation.

`SpecFamily` supports NVME/OCP/MFND and TEST. TEST is exclusively for fixtures.
All fixture field and rule IDs start with `TEST.` or `FIXTURE.`.
Version labels are strings and safe path components. Their ordering comes only from `inherits`, never numeric or lexical inference.
Windows reserved file names, trailing dots and case-colliding versions are rejected on every platform.
Production documents, rules, overrides, change history and referenced Features cannot use fixture evidence.

A catalog registers source document identities `(source_type, source_document, source_version)` and Feature IDs.
Provenance requires source identity, section and Knowledge status. Unavailable reviewer/date remain null.
Confirmed evidence requires an explicitly supplied reviewer/date; code never promotes candidate evidence.
The catalog is reference metadata, not a copy of the actual source document or proof that a production rule is correct.

Base files for the same family/version may be split by command if their fields/rules are disjoint
and their `data_kind`/`schema_ref` agree. Duplicate IDs are errors, not overwrites.
OCP/MFND requirements use an explicit `schema_ref` to a NVME/TEST snapshot; they cannot define field schemas.

Canonical schema values are native integers, bitmask integers, strings or byte representations described by `value_type`.
Numeric checks currently require native YAML integers. Quoted hexadecimal formatting is not automatically converted.
This is a strict Phase 1 input contract, not a claim that all illustrative SDS YAML can be imported unchanged.

LOOKUP accepts a Source YAML mapping or a list of `{key, value}` entries.
Effective output always uses a deterministically sorted entry list, preserving integer and string key types.
For example, integer `1` and string `"1"` remain separate entries. Repeated keys of the same type are errors.
Delta LOOKUP arrays use this entry-list representation and replace the complete list.
Runtime LOOKUP execution remains outside this subset.

Domain collections are recursively immutable, including condition dictionaries and nested Delta objects/arrays.
Builder edits use separate mutable work buffers. `model_copy(update=...)` is a trusted internal operation;
it freezes supplied collections but, as in Pydantic, does not validate arbitrary update values.

## Delta semantics

Actions are case-insensitive at loading and canonicalized to uppercase.

| Action | Contract |
| --- | --- |
| ADD | Target must be absent; `previous` is absent; `current` supplies a complete new entity. |
| MODIFY | Nonempty `previous` guard; `current` recursively patches objects. Arrays replace in full. |
| REMOVE | Nonempty `previous` guard; `current` absent. Entity is removed, but its history remains in snapshot changes. |
| REDEFINE | Nonempty `previous` guard; `current` is a complete replacement with the same Target identity. |
| DEPRECATE | Schema: `current: {lifecycle: deprecated}`. Rule: `current: {provenance: {status: deprecated}}`. |
| REQUIREMENT_CHANGE | Rule-only patch containing the `requirement` property. |

Guards compare every specified property against the unmodified **parent** snapshot.
Nested nonempty objects act as partial guards; scalars, arrays, empty objects and explicit null match exactly.
Scalar types must match, so `true` does not match integer `1`.
This comparison also applies to scalars nested in array guards.
All guards are checked before any delta operation is applied.

Whole-field changes cannot coexist with bit changes on that field within one delta.
Repeated changes to the same field/bit or rule are rejected. Disjoint bit changes are sorted deterministically.
Target identity changes are errors. Rename must be an explicit remove/add workflow.
This includes a field's command and a rule's command/field/effective bit, including `check.bit` targets.
Explicit null sets an optional property to null; it is not an implicit property deletion operator.

OCP/MFND deltas may declare `schema_ref_change: {previous: ..., current: ..., provenance: ...}`.
`previous` is required (explicit null is allowed) and must equal the parent's complete schema reference.
`current` must resolve to a compatible data-kind NVME/TEST snapshot. Retained rules are revalidated against it.
The change is recorded as `@schema_ref`, appears in structural diffs and retains selection dependencies.
This is explicit reference validation, not a general cross-family compatibility inference engine.

Schema deprecation is separate from reserved/defined semantics.
Reserved state never synthesizes an expected-zero rule. Only an explicit validation behavior expresses that requirement.

## Provenance and determinism

Effective records retain `introduced_in`, `last_changed_in`, Source document/section/status,
relative Source YAML path, SHA-256 of original bytes and ordered change history.
These version markers describe builder-observed history, not an invented historical date from the external specification.
Remove events remain in `snapshot.changes`, and removed-item diffs include the removal evidence.
Bit diffs filter history to the bit and whole-field events instead of attributing unrelated bit changes to that bit.

Rule changes use the change's explicit evidence or the Delta document's evidence; parent approval is not inherited.
Inline `current.provenance`, when non-null, must be a complete independent provenance object.
Different explicit inline and change-level evidence is an error, not a precedence choice.
DEPRECATE's prescribed status-only payload is the sole exception: it uses Delta/change evidence with deprecated status.
The effective rule and its new history event use the same evidence. Parent evidence remains in earlier history.

The knowledge hash covers relative Source paths and original bytes, including comments.
Uncommitted Knowledge content is therefore distinguished even when Git HEAD is unchanged.
Canonical snapshots and `manifests/build.json` contain no wall-clock time.
`manifests/execution.json` contains `generated_at` and Python/platform/runtime dependency versions separately;
its hash and the artifact index can differ between runs.
Builder semantics changes must update the builder version. Reproduction also requires the same dependency/toolchain behavior.
Builder 0.2.0 contains the independent-review safety fixes. `requirements-dev.lock` pins the tested development/CI dependencies.

## Build validation and conflict limits

Checks include YAML/schema validity, duplicate IDs, missing/circular/nonlinear inheritance,
delta guard mismatches, unknown Field/Bit/Feature/Source/schema references,
bad condition keys, incompatible value types, invalid masks/ranges and literal confirmed-rule conflicts.
Active rules cannot target deprecated fields or bits.
Condition paths with surrounding whitespace are errors; normalization cannot collapse different input keys.

Literal conflict checks operate within one effective snapshot, partitioning scalar-equality condition scopes.
They intersect EXACT/MIN/MAX/RANGE/ENUM and whole/partial Bit constraints without dropping compatible requirements.
Different layers/specificity/file ordering never select a winner.
Explicit overrides remain in the artifact with their original and overriding rules; enabled overrides need confirmed evidence.
Chained overrides are explicitly unsupported in this subset.
Context partitioning fails with `CONFLICT_CHECK_LIMIT` above 4096 combinations rather than claiming all contexts were checked.

Explicit confirmed Schema `must_be_zero` behavior participates in static conflict checking using Schema evidence.
For a bit, authority comes from the latest matching bit or whole-field event; unrelated bit events do not change it.
Reserved without explicit validation contributes no zero constraint. Candidate Schema evidence is not promoted.
Whole-field static zero checks currently support integer/bitmask fields; confirmed byte/string behavior fails explicitly
with `SCHEMA_VALIDATION_UNSUPPORTED` pending a normalization contract. Requirement overrides cannot disable Schema checks.

Cross-family/product-context Rule Resolution and dynamic LOOKUP/DERIVED/CAPABILITY evaluation are not performed.
Declared function/capability references can be validated but that does not establish runtime correctness.
The original Builder emits no SSD PASS/FAIL. The later offline rule pilot emits explicitly labeled
TEST/FIXTURE verdicts only. Candidate and Unknown knowledge are not converted into authoritative results.

## Artifacts and commands

All source versions are built and validated in memory before output is changed.
Optional `--spec`/`--version` selection retains parent and schema dependencies, while still validating the complete Source input.
Output lives in `effective/<family>/<version>.json`, `manifests/` and `artifact_index.json` under the selected output root.
The artifact index identifies files owned by the builder and checks their content hashes.
Unmanaged files or manually changed generated content prevent replacement. `.gitkeep` files are preserved.
Source/output overlap and output symlinks are refused.
Output is staged, then swapped with rollback on a handled replacement failure. Failed validation leaves existing artifacts intact.
Concurrent writers and recovery from a hard process kill between directory renames are not implemented.

All Phase 1 builds rebuild from Source, including `--clean`; there is no incremental/cache build mode.
`spec diff` builds from Source rather than trusting generated files.

## Golden artifacts

Golden JSON is generated exclusively using `tests/regenerate_fixture_goldens.py --write` and the real builder/diff engine.
It lives under `tests/golden/fixture_build/`, uses TEST/FIXTURE Source and `TEST_FIXTURE_COMMIT`, and is never Source Knowledge.
Tests do not regenerate or overwrite baselines. Review generated diffs before changing accepted goldens.
Independent semantic assertions cover behavior beyond comparing the implementation with its own generated baseline.
`.gitattributes` fixes Source YAML and Golden JSON checkout bytes to LF, including on Windows.
CI runs the full suite on Linux and Windows with `SSD_REQUIRE_SYMLINK_TESTS=1`.
On a local Windows machine without symlink privilege, those two tests explicitly skip; the same condition fails CI.

## Decisions still needed for later phases

The subsequent Identify candidate workflow is documented in `identify_knowledge_workflow.md`
and SDS section 72. It adds an isolated, explicitly non-authoritative multi-document
compiler without reinterpreting legacy NVME sources. Candidate component inheritance,
guarded review deltas and staged artifact publication reuse existing builder primitives.
It does not implement Product Resolution or promote candidate evidence.

- Approved actual Spec/Policy data and provenance naming adapters for source documents.
- FW version schemes, Product Profile ambiguity and Context Spec override policy.
- Complete condition language, missing facts/applicability/authority semantics.
- Cross-family Schema compatibility declarations and Rule Resolution.
- Dynamic calculations, dependencies on Actual, and prevention of circular validation.
- General override authority/scope/chains and scalable static conflict checking.
- SQL query/cache requirements and concurrent artifact publication/recovery.

## Implemented: requirement rule execution pilot

The next priority is conditional requirements and field relationships, rather than complete
PDF structure reconstruction. nvme-cli/libnvme command and layout support will be reused;
integration must pin its release/commit and retain spec-version applicability separately.

The offline pilot now builds fixture Source through the existing Builder and exposes
`resolve(context, snapshots, mappings)` and `evaluate(expected_profile, actual_facts)`.
It preserves conditional constraints, supports numeric field comparisons and literal/bit checks,
and emits an Effective Expected Profile, per-rule fixture verdicts and provenance trace.
The existing Builder literal-intersection implementation is reused. General relational
satisfiability, LOOKUP/DERIVED execution and production Bundle adapters remain unsupported.

Context missing facts remain UNKNOWN; Actual-dependent conditions are deferred. Unconfirmed
and non-mandatory knowledge is REVIEW. Capability-required bits are checked independently
from device-reported feature gates. Explicit single-stage overrides retain both rules;
schema checks cannot be overridden. Reserved never synthesizes a zero requirement.

`pilot run --source tests/fixtures/rule_pilot/knowledge --input tests/fixtures/rule_pilot/input.json`
emits deterministic fixture JSON to stdout without publishing artifacts. Source selection,
normalization, authority, conflict limits and status aggregation are specified in
[the rule execution pilot contract](rule_execution_pilot.md).

This describes the original fixture pilot. Product Profile auto-selection, FW comparison,
real collection and Excel remain future work. Subsequent sections describe experimental DUT
rule execution and the SQLite source repository; the original pilot remains file-based.

## Implemented: version-separated offline Actual normalization

`actual normalize` reads saved raw/JSON with an explicit fixture/candidate target Bundle
layout and independently recorded tool/device/query metadata. Tool and advertised versions
never select the product spec. It preserves all raw bytes (mapped hex and unmapped ranges),
the complete JSON interpretation and input hashes. No implicit reserved-zero rules, masks,
numeric coercion, truncation, padding or raw-to-JSON fallback are applied.

`layout_from_profile` reuses Builder schemas/history. `evaluate_normalized` connects
eligible fixture observations to the existing Resolver and retains capture reports while
guarding cross-Bundle/device/namespace combinations. Candidate interpretations stay REVIEW;
missing facts remain UNKNOWN. See [normalization contracts](actual_normalization.md).
# 로컬 GUI 추가 구현

후속 구현: candidate/provisional 실행을 명시적 experimental 모드에서 허용했다.
저장 DUT 로그 → 선택 Bundle의 집중 필드 Source → 기존 Builder → resolve/evaluate 경로를
추가했으며 GUI와 actual review-log --experimental에서 실행한다. provenance 승인 상태를
변경하지 않고 검토 전 해석/정책 가정과 모든 입력 hash를 보존한다. 자세한 현재 계약은
[검토 전 규칙 실행](experimental_rules.md)을 따른다. 실제 SSD 명령은 최후순위다.

저장 id-ctrl 로그를 기존 Candidate Bundle 지식에 연결하는 GUI를 추가했다.
Builder·Resolver/evaluate·정규화·Bundle Diff는 기존 application 서비스를 호출한다.
초기 GUI는 TEST/FIXTURE 실행 패널을 제공했으나 현재 기본 화면에서 제거했다.
현재 저장 DUT 로그에는 실제 규격 후보와 명시적 개발 가정을 experimental로 적용한다.
원문·입력 hash·필드별 정의·연결 요구사항·근거를 JSON으로 조회/저장한다.
실행 규칙이 없는 필드는 REVIEW/UNKNOWN으로 유지한다. 규칙 실행 결과와 지식 승인 상태는 별개다.
실행과 제한은 [로컬 GUI](local_gui.md)에 기록했다.

## 저장 로그 단일 GUI 흐름 통합

텍스트 로그를 공통 ActualFact로 변환하고 기존 layout_from_profile/normalize_json과
Builder/Resolver/evaluate로 연결했다. 기본 화면의 TEST/FIXTURE 실행 패널을 제거했고
CLI와 application 서비스는 유지했다. Bundle·Context·정책 선택은 현재 실행에 명시적으로
반영된다. 한 표에서 Actual·Expected·판정을 표시하며 직접 규칙이 없는 필드는 미판정이다.
정규화 타입/폭 오류와 누락은 ERROR/UNKNOWN으로 표시한다. 상세 사용법은
[GUI 사용 안내](local_gui.md)를 따른다.

## SQLite 원본 전환 (2026-10-11 승인)

현재 GUI와 `actual review-log` CLI는 `data/validator.sqlite3`에서 원본을 읽는다.
기존 YAML/JSON은 최초 가져오기와 교환/TEST/FIXTURE 자료다. DB 생성 이후 파일을
자동 동기화하거나 기존 수정을 덮어쓰지 않는다. 기존 Builder와 Resolver는 DB의 불변
리비전을 임시 파일로 투영하는 어댑터를 통해 그대로 재사용한다.

구현: 원본 내용의 해시 기반 보존, 부모/사유를 가진 리비전, Bundle별 규칙 인덱스,
GUI 규칙·정책 추가/수정/삭제, 전체 원본 가져오기/내보내기, 저장 전 모델·Builder·Resolver
검증, expected_revision을 통한 오래된 편집 거절. 검사 입력 원문·Context·정책·리비전과
전체 결과를 저장하며 과거 결과 조회와 동일 리비전 재실행을 제공한다.

GUI 폼은 현재 파일럿 RuntimeRule을 관리한다. 구조·매핑·기본 Context 전체 편집은
고급 원본 패키지 경로를 사용한다. 전체 규격 지식을 관계형 필드 테이블로 분해하거나
모든 엔티티별 GUI를 만든 상태는 아니다. candidate/provisional을 유지하고 실제 정책을
추정하지 않는다. 파일 기반 build/pilot/normalize 명령은 회귀와 가져오기 호환성에 유지한다.
저장 계약과 백업은 [SQLite 전환 계획](sqlite_transition.md)을 따른다.

## 완성 계획 1단계: DB 보호와 기준선 (2026-10-12)

스키마 v2와 명시적 v1→v2 migration을 추가했다. 변경 전 전체 백업, SQL 실패 rollback,
지원하지 않는/불완전한 스키마 거절, 원본 내용 해시 확인을 제공한다.
온라인 전체 백업과 검증 후 복원은 GUI 및 database CLI에서 실행한다.
복원은 전체 이력·원본 검증, 현재 head 확인, 자동 사전 백업과 staging 교체를 수행하고
새 head로 오래된 편집을 거절한다. 같은 프로세스의 검사와 복원은 직렬화한다.
전체 회귀 374개 통과. 기존 6개 규칙과 첨부 로그 판정은 변경하지 않았다.
현재 사실과 미완성은 [현재 상태](current_status.md), 절차는 [DB 운영](database_operations.md)을 따른다.

## 완성 계획 2단계: 지식 관리 (2026-10-12)

현재 등록 Bundle을 코드 고정 목록 대신 DB에서 읽는다. 실행 필드/비트/배열, 문서,
규칙·Capability 폼과 literal 검색, 단순 Context/Actual 조건 및 관계식 입력을 제공한다.
저장 전 검증된 미리보기 hash와 expected_revision을 다시 확인하며, 삭제/수정의 참조를 검증한다.
검토자·날짜·근거는 내용 해시에 연결한다. 수정 후 오래된 검토가 현재 내용의 승인으로 남지 않는다.
리비전 되돌리기는 새 리비전으로 복사하며 과거 검사 조회/재실행은 기존 경로를 유지한다.
스키마 v3 entity_index와 v2 사전 백업/migration을 구현했다. 전체 회귀 379개 통과.
지원 범위와 문서/규격 identity 보호는 [지식 관리 계약](knowledge_management.md)을 따른다.

## 프로젝트 완성 계획 3단계 추가 기록

복수 저장 응답 입력은 [saved_capture_inspections.md](saved_capture_inspections.md)를 따른다.
기존 단일 로그·Builder·raw/JSON 정규화·Resolver와 DB 이력을 유지한다. DUT/세션/Namespace별로
평가하고 원문·불확실성·충돌을 보존한다. 실제 Namespace 규칙을 추가한 단계는 아니다.

## 프로젝트 완성 계획 4단계 추가 기록

[제품 Profile·정책·Context 계약](product_profiles.md)에 따라 SQLite Source 리비전 관리,
명시적 선택·후보 제안·등록 FW 비교와 scope별 원본/설정 snapshot을 추가했다.
기존 Builder·정규화·Resolver와 이전 검사 재현을 유지하며 실제 제품값은 TEST와 구분한다.
실제 제품 정의가 없는 현재 DB의 제품 등록 목록은 비어 있다.

## 프로젝트 완성 계획 5단계 (2026-10-12)

[원문 대조와 실행 범위 표](nvme_requirement_coverage.md)에 따라 두 Bundle의 우선 요구사항을
candidate로 확대했다. 용량·THINP·공통 LBAF 인코딩/metadata·atomic 상속/관계·큐 max·
RPMB/ACWU/HMB와 새 Bundle HIR 일관성을 기존 Builder·정규화·Resolver로 실행한다.
원문 hash를 확인한 명시적 등록, 사전 전체 백업·리비전 CAS와 과거 검사 재현을 유지한다.
실행 규칙은 사람 검토 전 candidate이고 실제 id-ns는 TEST/FIXTURE 검증이다.
전체 구조 재추출·실제 SSD 명령·OCP/MFND·제품값 추정은 수행하지 않았다.

## 프로젝트 완성 계획 6단계: 추가 규격 연결 (2026-10-12)

[추가 규격 계약과 적용 범위](supplemental_requirements.md)에 따라 OCP DSSD2.6 원문 hash와
요구 ID를 보존하여 두 Bundle의 요구사항 → Capability → NVMe Field/Bit 및 직접 제약을
candidate로 등록한다. 제품 Profile에 명시적으로 연결한 정책과 적용 Context만 실행하며
실제 제품값·적용 대상·FW를 추정하지 않는다. MFND는 사용자 지시로 제외한다.
기존 엔진의 충돌·단일 명시적 override와 원래/대체 규칙·검토 근거를 trace로 연결한다.
실제 제품 바인딩과 정책 자료, 기타 OCP 요구·동작 검사는 등록 대기/미구현으로 구분한다.
