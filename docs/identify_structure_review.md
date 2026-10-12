# Identify structure candidate review

## Role after the requirement-first change

This catalog is supporting reference material, not a replacement implementation of
nvme-cli/libnvme. Command submission and base layout decoding will reuse those projects
with a pinned release/commit at integration time. Only fields needed by the current
rules need mapping/version verification before the offline fixture pilot can proceed.
Full catalog reconstruction or human review of every offset is not a prerequisite.
Header definitions do not approve normative requirements for a selected spec Bundle.
See [the rule execution pilot](rule_execution_pilot.md).

This is a candidate extraction, not approved NVMe knowledge or an executable
expected-value profile. All five requested responses are represented separately:
CNS 00h, 01h, 05h, 06h and 08h. NVM-specific responses use CSI 00h. Base CNS 01h
and 08h are command-set independent. CNS 01h has a Base fragment and an NVM
supplement; supplement absence outside its listed fields is intentional.

## Reproduce

Run `python tools/extract_identify_structures.py --source-dir <PDF directory>`
with `pypdf` and `pdfplumber` installed. The default output is
`candidates/nvme/structures.json`. The four input basenames are fixed in the
script; input PDFs remain read-only. The script extracts table geometry, retains
the corresponding figure text, and produces the same output for the same sources
and parser versions. No generated snapshot is edited.
The extractor first verifies all four SHA-256 hashes against `catalog.json` and
records them in `document_hashes`. A changed PDF is rejected before extraction
at fixed page anchors. Output paths inside `generated/`, input PDF paths and
non-JSON outputs are rejected before writing.

## Source boundaries

| Document | Response | Body figure | PDF pages | Printed pages |
|---|---|---|---|---|
| Base 2.0e | CNS 01h | 280 | 262–287 | 262–287 |
| Base 2.0e | CNS 08h | 285 | 292–294 | 292–294 |
| Base 2.1 | CNS 01h | 312 | 321–350 | 299–328 |
| Base 2.1 | CNS 08h | 319 | 357–360 | 335–338 |
| NVM 1.0e | CNS 00h | 97 | 57–64 | 57–64 |
| NVM 1.0e | CNS 01h supplement | 99 | 65–66 | 65–66 |
| NVM 1.0e | CNS 05h | 100 | 67 | 67 |
| NVM 1.0e | CNS 06h | 102 | 69–70 | 69–70 |
| NVM 1.1 | CNS 00h | 114 | 80–89 | 80–89 |
| NVM 1.1 | CNS 01h supplement | 117 | 90–92 | 90–92 |
| NVM 1.1 | CNS 05h | 118 | 93–97 | 93–97 |
| NVM 1.1 | CNS 06h | 120 | 99–103 | 99–103 |

Base 2.0e's list of figures disagrees with body captions. The anchors above use
the actual body. Base 2.1 PDF page numbers exceed printed numbers by 22.

Nested templates cover PSD (Base Figures 281/313), LBAF (NVM Figures 98/116),
and ELBAF (NVM Figures 101/119). `nested_template_id` joins an array field to a
top-level template. Each template's bit offsets are relative to one element;
each array's byte offset is relative to its response. Array count and stride are
checked against the explicitly numbered first and last entries in the source.

## Pilot and remaining review

CMIC's four individual bits and reserved range were compared with Base 2.0e
page 262 and Base 2.1 printed page 299. LBAF array endpoints and its nested bit
table were visually checked on rendered NVM 1.0e page 64, with continuation on
page 65. These are still candidate observations, not human approval.

Byte coverage and semantic completeness are different. `byte_coverage_complete`
checks offsets and lengths; `coverage_status` remains `partial` because exhaustive
bit semantics have not been reviewed. Multi-bit and labelled single-bit
candidates are conservative; other single-bit rows, enumerated values, applicability columns,
footnotes, scales, encodings and inherited meanings need review. Raw descriptions
and figure text are retained so these details are not silently discarded.

The extraction contains 12 document fragments, 367 field entries and six nested
descriptor templates. All ten complete response
definitions cover bytes 0 through 4095 without overlap. The other two fragments
are intentionally sparse CNS 01h NVM supplements. The candidate model validates
all fragments and their storage bounds. These counts measure extraction coverage,
not approval or complete normative interpretation.

Reserved bytes do not imply a must-be-zero validation rule. Unknown extraction
gaps remain explicit. Vendor-specific regions remain uninterpreted. Fields
whose meaning is supplied by another command-set document are marked delegated;
merging requires an explicit relationship and preserves both sources. No field
selection uses last-write-wins.

Reviewers should first resolve `coverage_gaps` and parser diagnostics, then
compare all bit tables, controller-type columns and notes, and finally resolve
cross-document requirements with the separately extracted rule candidates.
No field or rule in this artifact may be promoted simply because automated
offset checks passed.

## 프로젝트 완성 계획 5단계 (2026-10-12)

[원문 대조와 실행 범위 표](nvme_requirement_coverage.md)에 따라 두 Bundle의 우선 요구사항을
candidate로 확대했다. 용량·THINP·공통 LBAF 인코딩/metadata·atomic 상속/관계·큐 max·
RPMB/ACWU/HMB와 새 Bundle HIR 일관성을 기존 Builder·정규화·Resolver로 실행한다.
원문 hash를 확인한 명시적 등록, 사전 전체 백업·리비전 CAS와 과거 검사 재현을 유지한다.
실행 규칙은 사람 검토 전 candidate이고 실제 id-ns는 TEST/FIXTURE 검증이다.
전체 구조 재추출·실제 SSD 명령·OCP/MFND·제품값 추정은 수행하지 않았다.
