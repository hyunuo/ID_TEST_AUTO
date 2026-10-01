# Phase 1 Implementation Contracts

The architecture source of truth remains `ssd_nvme_validation_system_design.md` and `AGENTS.md`.
This document records implementation choices for the requested Phase 1 subset; it does not replace the SDS.

## Scope

Implemented: Pydantic v2 contracts, source YAML loading and validation, explicit linear spec inheritance,
guarded schema/requirement deltas, effective snapshots, provenance, manifests, structural diffs,
`knowledge build` / `spec diff`, unit/integration/golden tests.

Not implemented: Product Profile selection, DUT Rule Resolver, DERIVED/LOOKUP execution, SQLite,
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
All guards are checked before any delta operation is applied.

Whole-field changes cannot coexist with bit changes on that field within one delta.
Repeated changes to the same field/bit or rule are rejected. Disjoint bit changes are sorted deterministically.
Target identity changes are errors. Rename must be an explicit remove/add workflow.
Explicit null sets an optional property to null; it is not an implicit property deletion operator.

Schema deprecation is separate from reserved/defined semantics.
Reserved state never synthesizes an expected-zero rule. Only an explicit validation behavior expresses that requirement.

## Provenance and determinism

Effective records retain `introduced_in`, `last_changed_in`, Source document/section/status,
relative Source YAML path, SHA-256 of original bytes and ordered change history.
These version markers describe builder-observed history, not an invented historical date from the external specification.
Remove events remain in `snapshot.changes`, and removed-item diffs include the removal evidence.
Bit diffs filter history to the bit and whole-field events instead of attributing unrelated bit changes to that bit.

The knowledge hash covers relative Source paths and original bytes, including comments.
Uncommitted Knowledge content is therefore distinguished even when Git HEAD is unchanged.
Canonical snapshots and `manifests/build.json` contain no wall-clock time.
`manifests/execution.json` contains `generated_at` separately; its hash and the artifact index can differ between runs.
Builder semantics changes must update the builder version. Reproduction also requires the same dependency/toolchain behavior.

## Build validation and conflict limits

Checks include YAML/schema validity, duplicate IDs, missing/circular/nonlinear inheritance,
delta guard mismatches, unknown Field/Bit/Feature/Source/schema references,
bad condition keys, incompatible value types, invalid masks/ranges and literal confirmed-rule conflicts.

Literal conflict checks operate within one effective snapshot, partitioning scalar-equality condition scopes.
They intersect EXACT/MIN/MAX/RANGE/ENUM and whole/partial Bit constraints without dropping compatible requirements.
Different layers/specificity/file ordering never select a winner.
Explicit overrides remain in the artifact with their original and overriding rules; enabled overrides need confirmed evidence.
Chained overrides are explicitly unsupported in this subset.
Context partitioning fails with `CONFLICT_CHECK_LIMIT` above 4096 combinations rather than claiming all contexts were checked.

Cross-family/product-context Rule Resolution and dynamic LOOKUP/DERIVED/CAPABILITY evaluation are not performed.
Declared function/capability references can be validated but that does not establish runtime correctness.
No SSD PASS/FAIL is emitted. Candidate and Unknown knowledge are not converted into authoritative results.

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

## Decisions still needed for later phases

- Approved actual Spec/Policy data and provenance naming adapters for source documents.
- FW version schemes, Product Profile ambiguity and Context Spec override policy.
- Complete condition language, missing facts/applicability/authority semantics.
- Cross-family Schema compatibility declarations and Rule Resolution.
- Dynamic calculations, dependencies on Actual, and prevention of circular validation.
- General override authority/scope/chains and scalable static conflict checking.
- SQL query/cache requirements, dependency locking and concurrent artifact publication/recovery.
