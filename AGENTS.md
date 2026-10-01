# Project Rules

docs/ssd_nvme_validation_system_design.md
is the architecture and design source of truth.

## Source of Truth

Human-managed source:
- knowledge/
- spec base/delta
- product profiles
- policies
- mappings

Generated artifacts:
- generated/

Never manually edit generated artifacts.

## Mandatory Rules

- Do not invent NVMe/OCP/MFND specification values.
- Do not invent internal Samsung/product policy values.
- Unknown information must remain UNKNOWN.
- Do not silently resolve conflicts.
- Do not use last-write-wins rule resolution.
- Do not create large product-specific if/else logic.
- Product differences must be represented as data/rules.
- Reserved and expected=0 are different concepts.
- Every expected result must be traceable to provenance.
- Generated snapshots are build artifacts, not source data.
- Excel is not a source of truth.
- AI-generated specification knowledge must first be candidate data.
- Candidate data becomes confirmed only after validation/review.
- Every core domain change requires tests.

## Architecture

The intended model is:

Spec Base + Delta
→ Effective Spec Snapshot
→ Product Context
→ Policies / Capability Mapping
→ Rule Resolver
→ Effective Expected Profile
→ Actual NVMe Data
→ Validation Result

Validation statuses:

PASS
FAIL
N/A
REVIEW
UNKNOWN
CONFLICT
ERROR
