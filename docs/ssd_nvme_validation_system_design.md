# SSD NVMe ID Validation & Knowledge-Based Test Automation System
## Software Design Specification (SDS)

> 저장소 설계 갱신 (2026-10-11 승인): §36–37과 [SQLite 전환 계획](sqlite_transition.md)을
> 따른다. SQLite가 현재 원본이며 과거 YAML 원본/SQLite 캐시 설명을 대체한다.
> 기존 파일 형식은 엔진 어댑터·가져오기/내보내기·TEST/FIXTURE에 유지한다.

**문서 목적**  
본 문서는 삼성 서버 SSD 제품의 신규 FW/CS FW 검증 시 수행하는 NVMe Identify 기반 검증 업무를 자동화하기 위한 시스템의 상세 설계 문서다.  
Claude Code, Codex 또는 일반 개발자가 본 문서를 기준으로 PoC부터 운영 가능한 버전까지 구현할 수 있도록 아키텍처, 데이터 모델, Rule Resolver, Spec Delta Engine, TC 실행, 결과 판정, 저장소 구조, 테스트 전략을 정의한다.

---

# 1. 프로젝트 개요

## 1.1 배경

현재 신규 FW 또는 CS FW가 배포되면 다음 업무를 수작업으로 수행한다.

1. 사내 Confluence의 Answer Sheet에서 `id-ctrl`, `id-ns` 등 예상값 확인
2. Linux Test PC에 SSD 장착
3. `nvme-cli`로 실제 Identify 값 수집
4. Excel에서 Actual과 Answer Sheet 비교
5. 불일치 시 정책 협의회 문서, Spec, 내부 정책, 담당자 확인
6. Answer Sheet가 stale인지, FW 구현이 잘못되었는지 판단
7. Raw Data / 정리 데이터 / 검증 결과를 Excel로 정리

문제는 Answer Sheet가 항상 정답이라는 보장이 없으며, 값이 다음과 같은 다양한 조건에 의해 달라진다는 점이다.

- Product: PM1753, PM1763 등
- Product Flavor: MPF / COTS(FDP)
- FW Version / FW Type
- NVMe Base Spec Version
- OCP Spec Version
- MFND Spec Version
- Controller Mode: SPF / MPF
- Controller Role: Standalone / Parent / Child
- Form Factor: E1.S / E3.S / U.2
- Capacity: 2 / 4 / 8 / 16 / 32 TB
- Data Placement: Non-FDP / FDP
- FDP Configuration: SRG / MRG 및 세부 Parameter
- SIGN / MRG 등 Image Type
- VF 여부
- Namespace Configuration
- 제품/고객/사내 특수 정책
- FW-specific exception

따라서 본 시스템은 단순 비교 Script가 아니라 **Spec, Product Context, Capability, Policy를 조합하여 Expected 값을 계산하고 근거를 추적할 수 있는 Knowledge-Based Validation Engine**을 목표로 한다.

---

# 2. 핵심 설계 원칙

## 2.1 Answer Sheet를 절대적인 Source of Truth로 사용하지 않는다

Answer Sheet는 비교용 참고 자료이며, 최종 Expected는 다음 요소로부터 계산한다.

```text
NVMe Schema
+ External Spec Requirements (OCP/MFND/...)
+ Product Spec Profile
+ Product Context
+ Internal Policy
+ Product/FW Exception
= Effective Expected Profile
```

Answer Sheet는 별도 Reference Source로 가져와 다음 비교에 사용한다.

```text
Calculated Expected
vs
Confluence Answer Sheet
vs
Actual SSD
```

예:

```text
Calculated Expected : 0x14
Answer Sheet        : 0x10
Actual SSD          : 0x14

=> SSD PASS
=> Answer Sheet stale 가능성
```

---

## 2.2 사람이 관리하는 것은 Base + Delta + Rule이며 Full Snapshot은 자동 생성한다

예:

```text
OCP 2.4 Base
OCP 2.5 Delta
OCP 2.6 Delta
OCP 2.7 Delta
```

시스템이 자동 생성:

```text
Effective OCP 2.4
Effective OCP 2.5
Effective OCP 2.6
Effective OCP 2.7
```

**Generated Snapshot은 절대 사람이 직접 수정하지 않는다.**

---

## 2.3 Spec Version과 Product를 분리한다

잘못된 구조:

```text
PM1753_OCP26_EXPECTED.yaml
PM1763_OCP26_EXPECTED.yaml
...
```

권장 구조:

```text
OCP 2.6 Requirements
        +
PM1753 Product Profile
        +
PM1753 Product Policy
        ↓
PM1753 Effective Expected
```

하나의 Spec 지식을 여러 제품에서 재사용할 수 있어야 한다.

---

## 2.4 NVMe 문서 조합과 외부 Requirement Spec의 역할을 분리한다

### NVMe Base Spec + NVM Command Set Spec
NVMe 지식은 Base Spec 단독 버전이 아니라 명시적으로 등록한 문서 조합으로 관리한다.
Base와 NVM Command Set의 revision과 출처를 각각 유지하며, 두 문서 모두
**Schema/Meaning과 Requirement**를 정의할 수 있다. Identify 명령 공통 동작,
응답 구조, 명령 세트별 보완 정의를 필드 수준의 근거로 연결한다.

- Field 존재 여부
- Offset
- Length
- Bit 의미
- Reserved / Defined
- Value Type
- Feature 의미
- 고정값, 허용값, 조건부 요구사항과 필드 간 의존 관계

Base `2.0e` + NVM Command Set `1.0e`, Base `2.1` + NVM Command Set `1.1`은
서로 다른 Bundle이다. 버전 번호로 다른 문서의 revision이나 호환성을 추정하지 않는다.
구체적인 후보 데이터 계약과 검토 흐름은 72절을 따른다. 아래 기존 예시의 단일
`NVME` 버전은 이전 Builder의 설명용 형식이며 새 Bundle의 문서 선택을 대체하지 않는다.

### OCP / MFND / 기타 Spec
주로 **Requirement/Capability**를 정의한다.

- 어떤 기능이 Required / Optional인지
- 어떤 Controller Role에서 지원되는지
- 어떤 ID field/bit에 어떤 조건이 필요한지
- Minimum / Maximum / Exact / Bit requirement

---

## 2.5 Rule은 값이 아니라 근거까지 추적 가능해야 한다

모든 Rule에는 최소 다음 정보를 둔다.

```text
rule_id
source_type
source_document
source_version
source_section
introduced_in
last_changed_in
status
verified_by
verified_date
```

최종 결과에서 다음 질문에 답할 수 있어야 한다.

> "왜 이 제품의 이 field가 이 값이어야 하는가?"

---

## 2.6 AI는 최종 PASS/FAIL 결정자가 아니다

AI의 역할은 다음으로 제한한다.

- 정책 문서 후보 검색
- 관련 Feature 추정
- ID Field / Bit와 Feature의 연결 후보 제안
- 동의어 확장
- 정책 원문 요약
- 미등록 Knowledge Rule 후보 생성

AI가 생성한 Rule은 자동으로 `confirmed`가 되지 않는다.

```text
AI Candidate
→ Human Review
→ Confirm
→ YAML Knowledge 등록
→ Git Review
```

---

# 3. 시스템 목표

## 3.1 Functional Goals

시스템은 다음을 수행해야 한다.

1. `nvme-cli`로 Actual ID 자동 수집
2. Raw Data 보존
3. DUT Context 정의
4. 적용 Spec Version 결정
5. Spec Version별 Effective Snapshot 생성
6. Product Context에 따라 적용 Rule 선택
7. Effective Expected Profile 생성
8. Actual과 Expected 비교
9. Bitmask Field XOR 분석
10. ID → Feature 역매핑
11. Answer Sheet와 계산 Expected 비교
12. PASS / FAIL / N/A / REVIEW / UNKNOWN / CONFLICT / ERROR 판정
13. JSON / Excel / Text Report 생성
14. 모든 Expected 값의 근거 추적
15. Spec Version Upgrade 시 영향받는 ID 목록 생성
16. Regression TC 후보 자동 생성

---

# 4. 시스템 전체 아키텍처

```text
                 ┌────────────────────────────┐
                 │        Knowledge Repo       │
                 │                             │
                 │ NVMe Schema Base/Delta      │
                 │ OCP Requirement Base/Delta  │
                 │ MFND Requirement Base/Delta │
                 │ Feature Mapping             │
                 │ Product Profiles            │
                 │ Internal Policies           │
                 │ Exceptions                  │
                 └──────────────┬─────────────┘
                                │
                          build_knowledge
                                │
                                ▼
                 ┌────────────────────────────┐
                 │   Effective Snapshot DB     │
                 │ Generated Snapshot/Trace   │
                 └──────────────┬─────────────┘
                                │
                                │
┌───────────────┐               │
│ Linux Test PC │               │
│   nvme-cli    │               │
└──────┬────────┘               │
       │                         │
       ▼                         ▼
┌───────────────┐       ┌────────────────────┐
│   Collector   │       │      Resolver      │
└──────┬────────┘       └─────────┬──────────┘
       │                          │
       ▼                          ▼
┌───────────────┐       ┌────────────────────┐
│  Normalizer   │       │ Effective Expected │
└──────┬────────┘       │      Profile       │
       │                └─────────┬──────────┘
       └──────────────┬───────────┘
                      ▼
               ┌───────────────┐
               │   Validator   │
               └──────┬────────┘
                      ▼
               ┌───────────────┐
               │ Diff Analyzer │
               └──────┬────────┘
                      ▼
              ┌────────────────┐
              │ Report Engine  │
              └────────────────┘
```

---

# 5. 권장 기술 스택

## 5.1 Core

- Python 3.11 이상, 권장 3.12+
- `nvme-cli`
- YAML
- JSON
- SQLite
- Git

## 5.2 Python Libraries

권장:

- `pydantic` v2: YAML/JSON Data Model Validation
- `ruamel.yaml` 또는 `PyYAML`: YAML
- `openpyxl`: Excel Report
- `typer`: CLI
- `rich`: CLI output
- `pytest`: Unit/Integration Test

선택:

- `SQLAlchemy`: SQLite Query Layer가 복잡해질 경우
- `jsonschema`: 외부 Schema Validation이 필요한 경우

PoC에서는 stdlib `sqlite3`로도 충분하다.

---

# 6. Repository 구조

```text
ssd-id-validator/
│
├── pyproject.toml
├── README.md
├── config/
│   └── app.yaml
│
├── knowledge/
│   │
│   ├── specs/
│   │   ├── nvme/
│   │   │   ├── 2.0/
│   │   │   │   └── base/
│   │   │   │       ├── id_ctrl.yaml
│   │   │   │       └── id_ns.yaml
│   │   │   ├── 2.1/
│   │   │   │   └── delta.yaml
│   │   │   └── ...
│   │   │
│   │   ├── ocp/
│   │   │   ├── 2.4/
│   │   │   │   └── base.yaml
│   │   │   ├── 2.5/
│   │   │   │   └── delta.yaml
│   │   │   ├── 2.6/
│   │   │   │   └── delta.yaml
│   │   │   └── ...
│   │   │
│   │   └── mfnd/
│   │       ├── 1.5/
│   │       │   └── base.yaml
│   │       ├── 1.6/
│   │       │   └── delta.yaml
│   │       └── ...
│   │
│   ├── features/
│   │   └── features.yaml
│   │
│   ├── mappings/
│   │   ├── field_to_feature.yaml
│   │   └── capability_to_field.yaml
│   │
│   ├── products/
│   │   ├── PM1753/
│   │   │   ├── profile.yaml
│   │   │   ├── policies.yaml
│   │   │   └── exceptions.yaml
│   │   └── PM1763/
│   │
│   ├── policies/
│   │   ├── common/
│   │   └── product/
│   │
│   └── answer_sheet/
│       └── imported/
│
├── generated/
│   ├── effective/
│   │   ├── nvme/
│   │   ├── ocp/
│   │   └── mfnd/
│   ├── manifests/
│   └── knowledge.db
│
├── src/
│   └── ssd_validator/
│       ├── models/
│       ├── spec_builder/
│       ├── resolver/
│       ├── collector/
│       ├── normalizer/
│       ├── validator/
│       ├── analyzer/
│       ├── storage/
│       ├── reporter/
│       ├── policy_search/
│       └── cli.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── golden/
│
└── results/
```

---

# 7. 핵심 Domain Model

전체 시스템에서 다음 객체를 핵심 Domain Object로 정의한다.

1. `SpecFamily`
2. `SpecVersion`
3. `FieldSchema`
4. `RequirementRule`
5. `Capability`
6. `CapabilityMapping`
7. `ProductProfile`
8. `DutContext`
9. `InternalPolicy`
10. `ExceptionRule`
11. `EffectiveSnapshot`
12. `EffectiveExpectedProfile`
13. `ActualSnapshot`
14. `ValidationResult`

---

# 8. DUT Context 모델

실제 검증 대상 장비의 전체 조건이다.

예:

```yaml
product:
  model: PM1753
  flavor: MPF

fw:
  version: "A123"
  type: CS

hardware:
  form_factor: E3.S
  capacity_tb: 16

controller:
  mode: MPF
  role: parent

virtualization:
  vf_enabled: false

image:
  type: SIGN

data_placement:
  type: NON_FDP

namespace:
  nsid: 1
  configuration: default

spec_profile:
  nvme: "2.1"
  ocp: "2.6"
  mfnd: "1.6"
```

---

# 9. Product Flavor 모델

## 9.1 MPF

MPF 제품은 최소 다음 축을 분리한다.

```text
Controller Mode
- SPF
- MPF

Controller Role
- standalone
- parent
- child
```

예:

```yaml
controller:
  mode: MPF
  role: child
```

`mode`와 `role`을 하나의 enum으로 합치지 않는다.

이유:

- MPF mode 전체에 적용되는 Rule
- Parent에만 적용되는 Rule
- Child에만 적용되는 Rule

을 각각 표현해야 하기 때문이다.

---

## 9.2 COTS / FDP

Data Placement는 다음처럼 모델링한다.

```yaml
data_placement:
  type: FDP

  fdp:
    supported: true
    enabled: true
    profile: MRG

    reclaim_group_count: 16
    ruh_count: 8
    selected_config_id: 1
```

Non-FDP:

```yaml
data_placement:
  type: NON_FDP

  fdp:
    supported: false
    enabled: false
```

SRG:

```yaml
data_placement:
  type: FDP

  fdp:
    supported: true
    enabled: true
    profile: SRG
    reclaim_group_count: 1
```

중요:

`SRG/MRG`는 편의상 Profile 이름으로 사용하고, 실제 판정은 가능한 경우 다음과 같은 구조적 Parameter를 기준으로 한다.

- FDP supported
- FDP enabled
- reclaim_group_count
- ruh_count
- selected_config
- namespace relation
- 기타 Spec 정의 Parameter

새로운 FDP Profile이 생겨도 DB Schema를 변경하지 않도록 한다.

---

# 10. Form Factor / Capacity 모델

Form Factor:

```text
E1.S
E3.S
U.2
```

Capacity:

```text
2 TB
4 TB
8 TB
16 TB
32 TB
```

DB에서는 문자열보다 정규화된 값 사용을 권장한다.

```yaml
hardware:
  form_factor: E3.S
  capacity_tb: 16
```

---

# 11. Rule 종류

Expected를 하나의 `expected=value` 형태로만 표현하면 안 된다.

다음 Rule Type을 지원한다.

```text
EXACT
MIN
MAX
RANGE
ENUM
BIT_SET
BIT_CLEAR
MASK
DERIVED
LOOKUP
OPTIONAL
NOT_APPLICABLE
CAPABILITY
```

예:

```yaml
check:
  type: EXACT
  value: "0x001F"
```

```yaml
check:
  type: MIN
  value: 8
```

```yaml
check:
  type: BIT_SET
  bit: 3
```

```yaml
check:
  type: RANGE
  min: 100
  max: 200
```

---

# 12. NVMe Schema 모델

NVMe는 Versioned Schema로 관리한다.

예:

```yaml
spec_family: NVME
version: "2.0"
command: id-ctrl

fields:
  - field_id: NVME.ID_CTRL.FIELD_X
    name: FIELD_X
    offset: 100
    length: 1
    endian: little
    value_type: bitmask

    bits:
      - bit: 0
        state: defined
        feature: feature_a

      - bit: 1
        state: reserved
```

Reserved는 `expected=0`과 동일하게 취급하지 않는다.

잘못된 모델:

```yaml
expected: 0
```

권장:

```yaml
state: reserved

validation:
  behavior: must_be_zero
```

Semantic State와 Validation Rule을 분리한다.

---

# 13. NVMe Schema Delta

새 NVMe Spec에서 Reserved가 Defined로 바뀌는 경우:

```yaml
spec_family: NVME
version: "2.1"
inherits: "2.0"

schema_changes:

  - action: modify
    target:
      field_id: NVME.ID_CTRL.FIELD_X
      bit: 1

    previous:
      state: reserved

    current:
      state: defined
      feature: feature_b
```

Builder는 `previous`가 실제 이전 Effective Snapshot과 일치하는지 검증한다.

불일치하면 Build 실패:

```text
BUILD ERROR

NVMe 2.1 delta expected:
FIELD_X[1] = reserved

Inherited NVMe 2.0 snapshot:
FIELD_X[1] = defined
```

---

# 14. OCP / MFND Requirement Delta

OCP/MFND는 주로 Requirement/Capability 변화로 표현한다.

예:

```yaml
spec_family: OCP
version: "2.6"
inherits: "2.5"

changes:

  - action: modify
    rule_id: OCP.FIELD_A.REQ

    previous:
      requirement: optional

    current:
      requirement: required

  - action: add
    rule:
      rule_id: OCP.FIELD_B.BIT3
      target:
        command: id-ctrl
        field_id: NVME.ID_CTRL.FIELD_B
        bit: 3

      check:
        type: BIT_SET
```

---

# 15. Spec Delta Engine

## 15.1 Source

사람이 관리:

```text
Base
Delta 1
Delta 2
Delta 3
```

## 15.2 Build

시스템:

```text
Base
+ Delta 1
= Effective v1

Effective v1
+ Delta 2
= Effective v2
```

각 버전의 Effective Snapshot을 항상 생성한다.

---

## 15.3 Delta Action

최소 지원:

```text
ADD
MODIFY
REMOVE
REDEFINE
DEPRECATE
REQUIREMENT_CHANGE
```

가능하면 `previous/current` Guard를 사용한다.

---

## 15.4 Version Graph

PoC에서는 각 Version이 하나의 Parent를 가지는 Linear Inheritance를 지원한다.

```text
2.4 → 2.5 → 2.6 → 2.7
```

향후 Branch/Errata가 필요할 경우 DAG로 확장한다.

---

# 16. Capability 모델

Feature 또는 Command 지원 여부를 구조화한다.

예:

```yaml
capability_id: dataset_management

name: Dataset Management

aliases:
  - DSM
  - Deallocate
  - TRIM
```

MFND에서 Controller Role별 Command Support를 정의할 수 있다.

```yaml
spec_family: MFND
version: "1.6"

capabilities:

  - capability_id: command_a

    roles:
      standalone: supported
      parent: supported
      child: unsupported
```

---

# 17. Capability → ID Mapping

Capability와 ID Field/Bit를 연결한다.

```yaml
capability_id: command_a

representations:

  - command: id-ctrl
    field_id: NVME.ID_CTRL.FIELD_X
    bit: 3

    values:
      supported: 1
      unsupported: 0
```

Resolver:

```text
role = child
↓
MFND 1.6
↓
command_a = unsupported
↓
FIELD_X[3] = 0
```

---

# 18. ID → Feature Reverse Mapping

Mismatch 분석용 Knowledge이다.

```yaml
field_id: NVME.ID_CTRL.ONCS

bits:
  - bit: 2
    feature: dataset_management

    aliases:
      - DSM
      - Deallocate
      - TRIM
```

Validation 시:

```text
Expected = 0x13
Actual   = 0x17
XOR      = 0x04

Changed Bit = 2
↓
Reverse Mapping
↓
dataset_management
↓
관련 정책 검색 후보 생성
```

---

# 19. Product Profile

Product는 모든 Expected 값을 직접 저장하지 않는다.

제품이 어느 Spec을 따르는지 선언한다.

예:

```yaml
product: PM1753
flavor: MPF

profiles:

  - profile_id: PM1753_MPF_A

    fw:
      from: "A000"
      to: "A999"

    specs:
      nvme: "2.0"
      ocp: "2.5"
      mfnd: "1.5"

  - profile_id: PM1753_MPF_B

    fw:
      from: "B000"

    specs:
      nvme: "2.1"
      ocp: "2.6"
      mfnd: "1.6"
```

FW Version 문자열 비교 규칙은 제품별 Version Scheme Adapter로 분리한다.

문자열 lexical comparison을 임의로 사용하지 않는다.

---

# 20. Internal Policy

Spec에 없는 Form Factor / Capacity / 제품 정책 등을 표현한다.

예: Form Factor

```yaml
rule_id: PM1753.RDT3.E3S

layer: internal_policy

applies_when:
  product.model: PM1753
  hardware.form_factor: E3.S

target:
  command: id-ctrl
  field_id: VENDOR.RDT3_ENTRY_TIME

check:
  type: EXACT
  value: 120

provenance:
  source_type: policy
  document_id: POLICY-123
  revision: 4
  section: "3.2"
```

---

# 21. Capacity Rule

Lookup 형태를 지원한다.

```yaml
rule_id: PM1753.FW_DOWNLOAD_TIME

layer: internal_policy

target:
  command: id-ctrl
  field_id: VENDOR.FW_DOWNLOAD_TIME

check:
  type: LOOKUP
  key: hardware.capacity_tb

  values:
    2:  "VALUE_A"
    4:  "VALUE_B"
    8:  "VALUE_C"
    16: "VALUE_D"
    32: "VALUE_E"
```

---

# 22. Derived Rule

예: NS Size처럼 Context 또는 다른 값에서 계산되는 경우.

```yaml
rule_id: PM1753.NSZE.DEFAULT

target:
  command: id-ns
  field_id: NVME.ID_NS.NSZE

check:
  type: DERIVED
  function: calculate_nsze

inputs:
  - hardware.capacity_tb
  - namespace.configuration
  - actual.id_ns.lbaf
```

단, 실제 Source of Truth가 Capacity별 고정 테이블이면 Derived 대신 LOOKUP을 사용한다.

**계산 가능하다고 무조건 수식화하지 않는다.**

---

# 23. Applicability

Expected와 Applicability를 반드시 분리한다.

예:

```yaml
rule_id: FDP.FIELD_X

applicable_when:
  data_placement.type: FDP
```

Non-FDP 제품에서 해당 항목은:

```text
N/A
```

이지:

```text
Expected = 0
```

이 아니다.

---

# 24. FDP 모델 상세

FDP는 최소 세 가지 개념을 분리한다.

## 24.1 Capability

```yaml
fdp:
  supported: true
```

## 24.2 Configuration

```yaml
fdp:
  configurations:

    - id: 0
      profile: SRG
      reclaim_group_count: 1
      ruh_count: 8

    - id: 1
      profile: MRG
      reclaim_group_count: 16
      ruh_count: 8
```

## 24.3 Runtime State

```yaml
fdp:
  enabled: true
  selected_config_id: 1
```

이 셋을 하나의 `fdp_mode`로 합치지 않는다.

---

# 25. Validation Status

최종 상태:

```text
PASS
FAIL
N/A
REVIEW
UNKNOWN
CONFLICT
ERROR
```

정의:

### PASS
신뢰 가능한 Rule에 따른 Expected 조건을 Actual이 만족.

### FAIL
적용 Rule과 Expected가 명확하며 Actual이 위반.

### N/A
해당 Context에서는 검증 대상이 아님.

### REVIEW
근거는 있으나 Human Review 필요.

예:
- imported Answer Sheet와 Calculated Expected 불일치
- low confidence rule
- AI candidate only

### UNKNOWN
Expected Rule이 없음.

### CONFLICT
두 개 이상의 authoritative Rule이 서로 호환되지 않음.

### ERROR
Command execution, parsing, schema error 등 시스템 실행 오류.

---

# 26. Rule Precedence

기본 Layer:

```text
1. NVMe Schema
2. External Spec Requirement
3. Internal Common Policy
4. Product Policy
5. Product/FW Exception
```

그러나 단순 Last-Write-Wins는 사용하지 않는다.

Resolver는 동일 Target에 적용되는 모든 Rule을 수집한다.

### 호환 가능한 경우

예:

```text
OCP: value >= 8
Product: value = 16
```

=> Compatible

### 충돌

```text
OCP: bit 3 = 1
Product Policy: bit 3 = 0
```

=> `CONFLICT`

Override가 필요한 경우 명시적으로 선언한다.

```yaml
override:
  enabled: true
  overrides:
    - OCP.RULE.123

reason: "Customer specific requirement"
source: POLICY-999
```

명시적 Override 없이는 silent override 금지.

---

# 27. Rule Specificity

같은 Layer에서 여러 Rule이 적용될 수 있다.

예:

```text
Common Capacity Rule
PM1753 Capacity Rule
PM1753 + E3.S + 16TB Rule
```

Resolver는 Rule의 조건이 더 구체적인 Rule을 우선 Candidate로 볼 수 있으나, 값이 충돌하는 경우 자동 overwrite하지 않고 다음 조건을 적용한다.

1. 동일 Layer
2. 둘 다 authoritative
3. 서로 다른 Expected
4. 명시적 Override 관계 없음

=> `CONFLICT`

---

# 28. Rule Provenance

모든 Effective Rule은 최종 Report에 다음 Chain을 제공한다.

```text
Target:
NVME.ID_CTRL.FIELD_X[3]

Expected:
1

Reason:
command_a must be supported

Derived From:
MFND 1.6 capability rule
→ MPF parent supports command_a
→ capability_to_field mapping
→ FIELD_X[3] = 1

Source:
MFND 1.6 / Section ...
```

---

# 29. Effective Expected Profile

Resolver 출력 예:

```yaml
context_id: PM1753_A123_E3S_16TB_PARENT

fields:

  - target:
      command: id-ctrl
      field_id: NVME.ID_CTRL.FIELD_X
      bit: 3

    applicable: true

    check:
      type: BIT_SET

    provenance:
      - rule_id: MFND.CMD_A.PARENT
      - rule_id: MAP.CMD_A.FIELD_X_BIT3

  - target:
      command: id-ctrl
      field_id: VENDOR.FW_DOWNLOAD_TIME

    applicable: true

    check:
      type: EXACT
      value: "VALUE_D"

    provenance:
      - rule_id: PM1753.FW_DOWNLOAD_TIME
```

---

# 30. Actual Collector

## 30.1 기본 Command

예:

```bash
nvme id-ctrl /dev/nvme0 -o json
nvme id-ns /dev/nvme0n1 -o json
```

실제 제품 환경에 맞는 추가 Command를 Plugin 방식으로 확장한다.

---

## 30.2 저장 항목

각 실행에서 최소 다음을 보관한다.

```text
command
device
timestamp
nvme-cli version
return code
stdout
stderr
raw JSON
normalized JSON
```

Raw는 절대 덮어쓰지 않는다.

---

# 31. Normalization

nvme-cli 출력 형식 차이를 Normalizer에서 흡수한다.

내부 값 표현:

- Numeric field: Python `int`
- Bitmask: Python `int`
- Hex display: Report 단계에서 format
- String: trim / padding rule 명시
- Byte Array: canonical hex string
- Capacity: integer bytes 또는 TB normalized value

Raw Display와 Canonical Value를 모두 보존할 수 있다.

예:

```json
{
  "field_id": "NVME.ID_CTRL.ONCS",
  "raw": "0x001f",
  "value": 31
}
```

---

# 32. Bitmask Diff Analyzer

Expected와 Actual이 Bitmask일 경우:

```python
diff = expected ^ actual
```

각 changed bit를 추출한다.

예:

```text
Expected 0x13
Actual   0x17
Diff     0x04

Changed bits:
- bit 2
```

이후 Reverse Mapping을 수행한다.

---

# 33. Answer Sheet Adapter

초기 PoC에서는 Confluence 자동 연동 없이 수동 Export를 권장한다.

예:

```text
knowledge/answer_sheet/imported/PM1753_A123.xlsx
```

Adapter가 정규화하여:

```json
{
  "field_id": "NVME.ID_CTRL.ONCS",
  "value": 23,
  "source": "answer_sheet",
  "revision": "..."
}
```

형태로 변환한다.

장기적으로 Confluence REST API Adapter를 추가한다.

---

# 34. Answer Sheet 분석 상태

별도 상태를 Result Metadata에 포함한다.

예:

```text
ANSWER_SHEET_MATCH
ANSWER_SHEET_STALE_SUSPECTED
ANSWER_SHEET_UNKNOWN
```

SSD Validation 결과와 Answer Sheet 상태를 분리한다.

예:

```text
SSD Validation: PASS
Answer Sheet: STALE_SUSPECTED
```

---

# 35. Policy Search / AI Integration

PoC에서는 Optional.

Mismatch가 발생했는데 Rule이 없는 경우:

```text
Field/Bit
↓
Feature Reverse Mapping
↓
Feature aliases
↓
Policy Search
↓
Candidate documents
```

AI 출력은 Candidate만 제공한다.

예:

```json
{
  "status": "candidate",
  "feature": "dataset_management",
  "documents": [
    {
      "id": "POLICY-123",
      "confidence": 0.92
    }
  ]
}
```

Human Confirm 전에는 Expected DB에 반영하지 않는다.

---

# 36. SQLite 역할

2026-10-11 사용자 승인으로 SQLite를 **원본 저장소**로 전환한다.
이 결정은 본 문서의 과거 YAML 원본/SQLite 캐시 설명보다 우선한다.
YAML/JSON은 최초 마이그레이션, 가져오기·내보내기와 TEST/FIXTURE에 사용한다.
GUI와 saved-log CLI는 DB에서 읽고, 관리 GUI의 수정은 새 불변 리비전으로 저장한다.

```text
관리 GUI / 명시적 원본 가져오기
↓
기존 모델·Builder·Resolver로 저장 전 검증
↓
SQLite 원본 새 리비전
↓
기존 Builder / 정규화 / Resolver
↓
검사 결과 + 사용 리비전 + 입력·선택 옵션 보존
```

SQLite 파일:

```text
data/validator.sqlite3
```

이 DB는 삭제 가능한 생성물이 아니다. 원본 전체 내보내기는 지식 데이터를 보존하며,
검사 이력까지 백업하려면 SQLite backup API를 사용하는 전체 DB 백업을 사용한다.
검증 후 복원은 자동 사전 백업과 새 head를 기록한다. 운영 절차는 [DB 보호](database_operations.md)를 따른다.
generated/의 Snapshot은 계속 재생성 가능한 산출물이며 직접 편집하지 않는다.

---

# 37. SQLite 권장 Table

현재 전환 구현:

```text
repository_meta       DB schema version
revision              불변 원본 버전, 부모 버전, 변경 사유, 시간
source_blob           SHA-256으로 식별하는 원본 문서 내용
revision_source       리비전별 논리 원본 경로와 내용 연결
rule_index            Bundle/필드/정책/검토 상태 조회 인덱스
validation_run        입력 원문·옵션·리비전·전체 결과
database_migration    스키마 변경과 사전 백업 기록 (v2)
entity_index          원본 리비전별 관리 검색 인덱스 (v3)
```

원본은 SQLite 내부 문서 내용으로 손실 없이 보존한다. rule_index는 동일 트랜잭션에서
원본으로부터 생성하며 독립적으로 편집하지 않는다. 기존 엔진 어댑터가 임시 파일로
투영하되 결과 출처는 sqlite://knowledge/revisions/<revision>/<source-path>로 고정한다.
전체 필드/근거를 개별 관계형 테이블로 재설계하는 작업은 이번 전환의 선행 조건이 아니다.

완성 계획 2단계는 DB 기반 Bundle 선택과 문서/실행 필드/비트/배열/규칙/Capability 관리 폼,
저장 전 미리보기, 내용 해시별 검토 기록, 참조 검증과 새 리비전 되돌리기를 제공한다.
배열/query 바인딩과 검토 기록은 management.json 논리 원본에 보존하고 인덱스와 함께 갱신한다.
v2→v3는 사전 백업 후 기존 원본의 검색 인덱스만 추가하며 과거 검사/원본을 변경하지 않는다.
규칙/Capability의 검토된 비-fixture 근거는 experimental에서 실행 가능하나 authoritative=false다.
strict TEST/FIXTURE 경계와 필드 Builder provenance는 자동 변경하지 않는다.
[구체적 관리 계약](knowledge_management.md)을 따른다.

향후 필요에 따른 정규화 후보(아래는 현재 구현 테이블을 의미하지 않는다):

```text
spec_family
spec_version
field_schema
field_bit_schema
feature
capability
field_feature_mapping
capability_field_mapping
requirement_rule
product
product_profile
product_spec_binding
internal_policy
exception_rule
effective_rule
provenance
build_manifest
```

추후:

```text
validation_run
validation_assertion
actual_value
answer_sheet_value
```

를 추가할 수 있다.

---

# 38. Spec Upgrade Impact Analysis

예:

```text
Old:
NVMe 2.0
OCP 2.5
MFND 1.5

New:
NVMe 2.1
OCP 2.6
MFND 1.6
```

시스템은 Effective Snapshot끼리 비교한다.

출력:

```text
Affected IDs

NVME.ID_CTRL.FIELD_A
Reason: OCP 2.5 → 2.6
Old: optional
New: required

NVME.ID_CTRL.FIELD_B[3]
Reason: NVMe 2.0 → 2.1
Old: reserved
New: defined

NVME.ID_CTRL.FIELD_C[2]
Reason: MFND 1.5 → 1.6
Parent command support changed
```

이 결과를 Regression TC 후보로 사용한다.

---

# 39. TC 모델

Field마다 TC를 하나씩 만들지 않는다.

추천:

```text
TC_NVME_ID_CTRL
TC_NVME_ID_NS
TC_FDP_IDENTIFY
TC_MFND_CAPABILITY
...
```

TC 내부에 여러 Assertion이 존재.

예:

```yaml
tc_id: TC_NVME_ID_CTRL

title: Verify NVMe Identify Controller

collector:
  type: nvme_cli
  command: id-ctrl

assertion_source:
  effective_profile:
    command: id-ctrl
```

Runner가 Effective Profile에 정의된 모든 applicable assertion을 수행한다.

---

# 40. TC Result 예시

```text
TC_NVME_ID_CTRL

VID                     PASS
SSVID                   PASS
FIELD_X[3]              PASS
FW_DOWNLOAD_TIME        FAIL
FIELD_Y                  N/A
FIELD_Z                  UNKNOWN
FIELD_Q                  CONFLICT
```

---

# 41. CLI 설계

## 41.1 Knowledge Build

```bash
ssd-validator knowledge build
```

옵션:

```bash
ssd-validator knowledge build --clean
ssd-validator knowledge build --spec ocp --version 2.6
```

---

## 41.2 Spec Diff

```bash
ssd-validator spec diff \
  --family ocp \
  --from 2.5 \
  --to 2.6
```

---

## 41.3 Product Profile Diff

```bash
ssd-validator profile diff \
  --product PM1753 \
  --old-fw A999 \
  --new-fw B001
```

---

## 41.4 Validation

```bash
ssd-validator run \
  --product PM1753 \
  --fw A123 \
  --device /dev/nvme0 \
  --namespace /dev/nvme0n1 \
  --form-factor E3.S \
  --capacity-tb 16 \
  --mode MPF \
  --role parent \
  --data-placement NON_FDP
```

Context YAML도 지원:

```bash
ssd-validator run --context context/pm1753_test.yaml
```

---

# 42. Result Directory

```text
results/
└── 2026-10-01_010203_PM1753_A123/
    ├── context.yaml
    ├── manifest.json
    ├── effective_expected.json
    ├── actual_normalized.json
    ├── validation.json
    ├── report.xlsx
    ├── summary.txt
    └── raw/
        ├── id_ctrl.json
        ├── id_ctrl.txt
        ├── id_ns.json
        └── id_ns.txt
```

---

# 43. Canonical JSON Result

JSON을 시스템의 최종 Machine-Readable Result로 정의한다.

Excel은 JSON을 기반으로 생성한다.

예:

```json
{
  "run_id": "20261001_PM1753_A123_001",
  "product": "PM1753",
  "fw": "A123",
  "summary": {
    "PASS": 120,
    "FAIL": 2,
    "N/A": 10,
    "REVIEW": 1,
    "UNKNOWN": 3,
    "CONFLICT": 0,
    "ERROR": 0
  },
  "assertions": []
}
```

Excel을 Source Data로 사용하지 않는다.

---

# 44. Excel Report 구성

권장 Sheet:

```text
Summary
Validation
Expected_Resolved
Actual_Normalized
Answer_Sheet
Diff
Provenance
Raw_ID_CTRL
Raw_ID_NS
Run_Context
```

Validation Sheet 예:

| Field | Bit | Expected | Actual | Result | Reason | Source |
|---|---:|---|---|---|---|---|
| FIELD_X | 3 | 1 | 1 | PASS | MFND parent supports CMD_A | MFND 1.6 |
| FIELD_Y | - | 120 | 110 | FAIL | E3.S policy | POLICY-123 |

---

# 45. Build Validation

Knowledge Build 시 반드시 검사할 항목:

1. YAML syntax
2. Pydantic schema
3. Duplicate `rule_id`
4. Duplicate `field_id`
5. Missing Parent Version
6. Delta previous mismatch
7. Unknown Field target
8. Unknown Feature
9. Circular inheritance
10. Invalid Product Profile
11. Rule condition key 오류
12. Unsupported Rule Type
13. Impossible Range
14. Explicit Conflict
15. Dangling provenance source

Build Error 시 Effective Snapshot과 SQLite를 생성하지 않는다.

---

# 46. Determinism

같은:

```text
Knowledge Commit
+
DUT Context
+
Actual Raw Data
```

에 대해서는 항상 동일한 결과가 나와야 한다.

Build Manifest:

```json
{
  "git_commit": "...",
  "knowledge_hash": "...",
  "builder_version": "...",
  "generated_at": "..."
}
```

Validation Report에 이 Manifest를 포함한다.

---

# 47. Git Workflow

권장:

```text
feature/new-ocp-2.7
```

개발자/검증자가 Delta 입력.

PR에서 자동 수행:

```text
lint
schema validation
build knowledge
delta guard validation
conflict detection
unit tests
snapshot diff
```

Review 후 merge.

Knowledge 변경도 Code 변경과 동일하게 리뷰한다.

---

# 48. 신규 Spec Version 등록 Workflow

예: OCP 2.7

사람:

1. 2.6 → 2.7 Spec 비교
2. ID 관련 변화 추출
3. `delta.yaml` 작성
4. Source Section 기록
5. PR 생성

CI:

1. OCP 2.6 Effective 로드
2. Delta previous guard 검증
3. OCP 2.7 Effective 생성
4. 2.6 vs 2.7 Diff 생성
5. 영향 ID 출력
6. 기존 Product 중 OCP 2.7을 사용하는 Profile 영향 분석

---

# 49. 신규 Product 등록 Workflow

1. Product Profile 생성
2. FW → Spec Version Mapping 등록
3. Form Factor/Capacity Support 등록
4. MPF/COTS Flavor 등록
5. Product Policy 입력
6. Product-specific Exception 입력
7. Context Matrix Test 작성

---

# 50. Context Matrix Test

제품별 주요 조합을 Golden Test로 만든다.

예:

```text
PM1753 / MPF / SPF / E3.S / 16TB
PM1753 / MPF / Parent / E3.S / 16TB
PM1753 / MPF / Child / E3.S / 16TB

PM1753 / COTS / Non-FDP / E1.S / 8TB
PM1753 / COTS / FDP-SRG / E1.S / 8TB
PM1753 / COTS / FDP-MRG / E3.S / 32TB
```

각 조합에 대해 Effective Profile이 예상과 동일한지 검증한다.

---

# 51. Unit Test 필수 항목

## Spec Builder

- Base build
- Delta add
- Delta modify
- Delta remove
- Previous mismatch
- Reserved → Defined
- Defined → Reserved
- Broken inheritance

## Resolver

- Exact
- Min/Max
- Lookup
- Derived
- Bit rule
- Form Factor condition
- Capacity condition
- Parent/Child condition
- FDP applicability
- Conflict
- Explicit override

## Validator

- PASS
- FAIL
- N/A
- UNKNOWN
- CONFLICT
- Parsing ERROR
- Bit XOR

---

# 52. Golden Snapshot Test

Effective Snapshot 파일 자체를 Golden Fixture와 비교한다.

예:

```text
tests/golden/ocp/2.6.json
tests/golden/mfnd/1.6.json
tests/golden/products/PM1753_PARENT_16TB.json
```

Spec Builder 변경 시 예상치 못한 Rule 변화 검출 목적.

---

# 53. Security / Environment

사내 문서 및 제품 정보가 포함될 수 있으므로:

- 외부 AI에 Raw internal document 자동 전송 금지
- Secret / Credential YAML 저장 금지
- Confluence Token 환경변수 또는 Secret Manager 사용
- Report의 외부 반출 정책 별도 준수
- Git repository 접근권한 제한
- Policy Document 본문 대신 ID/Section/Hash만 저장하는 방식 고려

---

# 54. Performance Requirement

초기 목표:

- Knowledge Build: 수 초~수십 초 이내
- Single DUT Resolve: 1초 이내
- id-ctrl/id-ns comparison: 체감 즉시
- SQLite는 버전이 있는 Knowledge 원본과 검사 이력을 저장한다. 파일 형식은 어댑터/교환용이다.

성능보다 Determinism과 Traceability를 우선한다.

---

# 55. Logging

구조화 Logging 권장.

예:

```json
{
  "event": "rule_applied",
  "rule_id": "PM1753.FW_DOWNLOAD_TIME",
  "target": "VENDOR.FW_DOWNLOAD_TIME",
  "context": {
    "capacity_tb": 16
  }
}
```

Debug Mode에서는 Resolver가 Rule 선택/제외 이유를 출력할 수 있어야 한다.

---

# 56. Explain 기능

필수 권장 기능.

```bash
ssd-validator explain \
  --context context.yaml \
  --field NVME.ID_CTRL.FIELD_X \
  --bit 3
```

출력:

```text
Target:
NVME.ID_CTRL.FIELD_X[3]

Applicable: YES
Expected: 1

Reasoning:
1. Product PM1753 uses MFND 1.6
2. Controller role = parent
3. MFND 1.6 requires command_a support for parent
4. command_a maps to FIELD_X[3]
5. supported => bit must be set

Sources:
- MFND 1.6, Section ...
```

이 기능은 신뢰성 확보에 매우 중요하다.

---

# 57. Unknown 처리 전략

Rule이 없을 때 프로그램이 추론해서 임의 Expected를 만들지 않는다.

```text
UNKNOWN
```

처리 후:

```text
Field
Bit
Product Context
Known Feature Mapping
Candidate Policies
```

를 출력하여 Knowledge 등록 작업을 돕는다.

---

# 58. Conflict 처리 전략

예:

```text
OCP 2.6:
FIELD_X[3] = 1

Internal Policy:
FIELD_X[3] = 0
```

명시적 override가 없으면:

```text
CONFLICT
```

Validation을 FAIL로 바꾸지 않는다.

먼저 Knowledge 자체의 충돌로 처리한다.

---

# 59. Confidence 사용

Knowledge Rule에 상태를 둘 수 있다.

```text
confirmed
provisional
candidate
deprecated
```

권장 판정:

```text
confirmed   → PASS/FAIL 가능
provisional → REVIEW
candidate   → REVIEW 또는 UNKNOWN
deprecated  → 적용 금지
```

---

# 60. PoC Scope

처음부터 모든 Spec / 모든 제품을 넣지 않는다.

권장 첫 범위:

```text
Product:
PM1753 또는 PM1763 중 하나

Commands:
id-ctrl
id-ns

Spec:
현재 제품이 사용하는 NVMe/OCP/MFND Version

Context:
대표 Form Factor 1~2개
대표 Capacity 2~3개
MPF Parent/Child
또는 COTS Non-FDP/SRG/MRG
```

---

# 61. Phase 1 — Core Engine

개발 대상:

- Pydantic Data Model
- YAML Loader
- Spec Base/Delta Builder
- Effective Snapshot Generator
- Product Profile Loader
- Rule Resolver
- CLI `knowledge build`
- CLI `spec diff`
- Unit Test

Acceptance:

- Spec Version 전체 Snapshot 자동 생성
- Invalid Delta build 실패
- Provenance 유지
- Deterministic output

---

# 62. Phase 2 — Actual Validation

개발 대상:

- nvme-cli Collector
- Normalizer
- Effective Expected Resolver
- Validator
- Bit Diff Analyzer
- JSON Result
- Text Summary

Acceptance:

```text
DUT Context + Device
→ 자동 수집
→ 자동 Expected 계산
→ 자동 비교
→ PASS/FAIL/etc 출력
```

---

# 63. Phase 3 — Excel / Existing Workflow Compatibility

개발 대상:

- Excel Report
- Answer Sheet Import
- Answer Sheet comparison
- Raw Sheet export

Acceptance:

기존 수작업 Excel 결과보다 정보가 적지 않아야 하며, 다음 정보가 추가되어야 한다.

```text
Expected Source
Spec Version
Rule ID
Policy ID
Reason
```

---

# 64. Phase 4 — Advanced Knowledge

개발 대상:

- Feature Mapping
- Capability Mapping
- MFND Parent/Child Matrix
- FDP Profiles
- Spec Upgrade Impact Analysis
- Regression TC Candidate

---

# 65. Phase 5 — Confluence / AI Integration

개발 대상:

- Confluence Adapter
- Policy Search
- Semantic Search
- AI candidate generation
- Human Approval workflow

AI는 Source of Truth가 아니라 Knowledge 작성 지원 도구다.

---

# 66. Acceptance Criteria — 최종 시스템

시스템은 다음 질문에 답할 수 있어야 한다.

### Q1
PM1753 MPF Parent / E3.S / 16TB / FW A123에서 FIELD_X 값은 무엇이어야 하는가?

### Q2
왜 그 값이어야 하는가?

### Q3
어느 Spec / 정책 / Rule에서 결정되었는가?

### Q4
OCP 2.5 → 2.6으로 올라가면 어떤 ID가 영향을 받는가?

### Q5
NVMe 2.0에서 Reserved였던 bit가 2.1에서 Defined되었는가?

### Q6
MFND 1.6에서 Parent와 Child가 지원하는 Command 차이가 어떤 ID에 영향을 주는가?

### Q7
E1.S / E3.S / U.2에 따라 달라지는 Expected는 무엇인가?

### Q8
2/4/8/16/32TB에 따라 달라지는 Expected는 무엇인가?

### Q9
Non-FDP / SRG / MRG Context에서 어떤 항목이 N/A 또는 Applicable인가?

### Q10
Actual과 Answer Sheet가 다를 때 SSD 문제인지 Answer Sheet stale 가능성인지 근거를 제시할 수 있는가?

---

# 67. 구현 시 하지 말아야 할 것

## 금지 1: 거대한 if/else

```python
if product == "PM1753":
    if capacity == 16:
        if mode == "MPF":
            ...
```

이런 구조는 만들지 않는다.

조건은 Rule Data로 관리한다.

---

## 금지 2: Product별 Full Expected 복사

Spec 지식 중복을 만든다.

---

## 금지 3: Last Rule Wins

충돌을 숨긴다.

---

## 금지 4: AI 결과를 Confirmed Rule로 자동 등록

Human Review 필수.

---

## 금지 5: Generated Snapshot 수동 수정

Source는 Base/Delta/Rule이다.

---

## 금지 6: Excel을 Source of Truth로 사용

Excel은 Report 또는 Import Reference다.

---

# 68. 권장 개발 순서

Claude Code/Codex에게 구현을 맡길 경우 다음 순서를 권장한다.

```text
Step 1
Project skeleton / Pydantic model

Step 2
YAML schema + sample knowledge

Step 3
Spec Delta Builder

Step 4
Effective Snapshot + provenance

Step 5
Rule condition matcher

Step 6
Resolver + conflict engine

Step 7
SQLite compiler

Step 8
nvme-cli collector interface

Step 9
normalizer

Step 10
validator

Step 11
bit diff analyzer

Step 12
JSON result

Step 13
Excel reporter

Step 14
spec/profile diff

Step 15
explain command

Step 16
Answer Sheet adapter

Step 17
Confluence / AI integration
```

---

# 69. 개발 Agent에게 주는 구현 지침

개발 Agent는 다음 원칙을 따른다.

1. 이 문서의 Domain Model을 먼저 구현하고 UI는 나중에 구현한다.
2. YAML은 사람이 읽고 수정하기 쉬워야 한다.
3. 모든 YAML을 Pydantic으로 Validation한다.
4. Generated Data와 Source Data를 명확히 분리한다.
5. Resolver는 pure/deterministic function에 가깝게 설계한다.
6. Rule 적용 이유를 Explain할 수 있어야 한다.
7. 모든 Override는 명시적이어야 한다.
8. 모든 Conflict를 숨기지 않는다.
9. Unknown을 억지로 추론하지 않는다.
10. Unit Test 없이 Rule Engine을 확장하지 않는다.
11. Spec Field의 실제 이름/offset/bit 값은 샘플 값으로 하드코딩하지 말고 실제 승인된 Spec 데이터로 채운다.
12. 내부 Spec/MFND/OCP 정책 값은 별도 Knowledge YAML로 입력 가능하도록 한다.
13. 실제 NVMe/OCP/MFND 문서 내용을 코드 내부 상수로 박지 않는다.
14. Rule/Schema Version 변화가 과거 결과의 재현성을 깨지 않도록 Git commit/hash를 결과에 남긴다.

---

# 70. 최종 권장 개념 모델

```text
                    ┌─────────────┐
                    │ NVMe Schema │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        OCP Requirements           MFND Requirements
              │                         │
              └────────────┬────────────┘
                           │
                    Capability Model
                           │
                   Field/Bit Mapping
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
 Product Profile      Internal Policy       Exceptions
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
                       DUT Context
                           │
                           ▼
                       Resolver
                           │
                           ▼
                Effective Expected Profile
                           │
                           │
              Actual SSD ──┴── Answer Sheet
                           │
                           ▼
                       Validator
                           │
                           ▼
                  Result + Provenance
```

---

# 71. 핵심 결론

본 시스템의 본질은 **Expected Value를 저장하는 DB**가 아니다.

보다 정확히는:

> **“어떤 Spec/Policy/Context가 어떤 ID Field/Bit에 어떤 요구사항을 만드는지 관리하고, 특정 DUT Context에서 최종 Expected를 재현 가능하게 계산하는 Knowledge & Rule Engine”**

이다.

사람이 관리해야 하는 핵심 데이터는:

```text
Base Spec
Spec Delta
Capability Mapping
Product Profile
Internal Policy
Exception
Provenance
```

이며 시스템은 이를 이용해 자동으로:

```text
Effective Spec Snapshot
Effective Expected Profile
Affected ID
TC Assertion
Validation Result
Explain Trace
```

를 생성한다.

이 구조를 지키면 향후:

```text
NVMe 2.x → 2.y
OCP 2.6 → 2.7
MFND 1.6 → 1.7
새로운 Form Factor
새로운 Capacity
새로운 FDP Profile
새로운 Product
```

이 추가되어도 핵심 코드 변경을 최소화하고, 대부분 **새로운 Delta / Rule / Profile 데이터 추가**만으로 대응할 수 있다.

---

# 72. NVMe 복수 문서와 Identify 후보 지식 구축

이 절은 실제 NVMe 원문을 반영하는 단계의 설계 계약이다. 이전 절의 단일 NVMe 버전
예시보다 이 절의 문서·Bundle 구분을 우선한다. 기존 Builder의 Source YAML 형식과
검증 동작은 유지하고, 후보 Bundle 컴파일러를 별도 경로로 둔다.

## 72.1 문서와 Bundle

문서는 종류, revision, 원본 파일명, SHA-256으로 식별한다. 원본 PDF 위치는 실행 시
`--documents-root`로 지정하며 개인 PC의 절대 경로를 지식 데이터에 저장하지 않는다.

| Bundle ID | Base 문서 revision | NVM Command Set 문서 revision |
| --- | --- | --- |
| `nvme-2.0e-nvm-1.0e` | `2.0e` | `1.0e` |
| `nvme-2.1-nvm-1.1` | `2.1` | `1.1` |

문서 이력은 문서별로 관리한다. Bundle은 두 개의 정확한 문서 ID를 선택하는 데이터이며,
제품 이름이나 버전 정렬로 선택하지 않는다. 이후 승인된 Base/Delta로 옮길 때에도
각 문서의 변경 이력과 서로 다른 문서의 보완 관계를 보존한다.

## 72.2 Identify 구조와 요구사항을 분리한다

구조 후보는 필드 ID, 바이트 위치·길이, 비트 범위, 배열·하위 구조, Reserved·Vendor
영역과 출처를 표현한다. CNS `00h`, `01h`, `05h`, `06h`, `08h`의 응답은 각각
독립적인 구조로 식별하며, 필요한 CSI·Namespace 질의 조건을 함께 기록한다.
명령 이름이 같아도 응답을 합치지 않는다.

요구사항 후보는 대상 구조·필드, 조건, 예외, 의무 수준, 요구 내용, 다른 필드·기능·
실행 상태에 대한 의존성과 출처를 기록한다. 표의 행뿐 아니라 설명·주석·참조된 절을
분석한다. 명시적 요구사항과 단순한 연관성, 명령 동작 요구사항은 구분한다.
Reserved라는 구조 정보만으로 expected=0을 만들지 않는다.

모든 후보의 provenance는 정확한 문서와 revision, 절, 표/그림, PDF 페이지와 인쇄
페이지를 추적할 수 있어야 한다. 원문에서 확인하지 못한 값이나 의미는 UNKNOWN으로
남긴다. 추출 신뢰도 점수나 빌드 성공은 원문 검토·승인을 대체하지 않는다.

## 72.3 에이전트와 검토 경계

```text
등록한 PDF + 명시적 Bundle
        ↓
요구사항 분석 에이전트 → 규칙·의존 관계 후보
        ↔
구조·매핑 담당 → 기존 CLI/헤더와 필요한 필드·버전 대조
        ↓
통합 담당의 교차 검토 + 자동 검증
        ↓
candidate Snapshot + 커버리지·미해결 보고서
        ↓
사람의 원문 검토·승인
        ↓
승인된 Knowledge → 기존 Builder → 향후 제품 Expected 계산
```

두 에이전트는 같은 문서 등록부를 사용한다. 요구사항 분석 중 구조 누락을 발견하면
임의 필드를 만들지 않고 구조 담당에게 반환한다. 통합 담당은 문서 간 중복·보완·충돌과
조건 누락을 확인한다. 에이전트가 작성한 내용은 교차 검토 후에도 candidate이다.
confirmed 전환에는 별도의 사람 검토자와 검토 근거가 필요하다.

## 72.4 데이터 경계와 빌드

| 경로 | 역할 |
| --- | --- |
| `candidates/nvme/catalog.json` | 원문 등록부와 명시적 Bundle |
| `candidates/nvme/structures.json` | 구조·하위 필드 후보와 커버리지 |
| `candidates/nvme/requirements.json` | 요구사항·의존 관계 후보와 미해결 참조 |
| `knowledge/` | 기존 승인 절차를 거치는 Source 지식 |
| `generated/candidate/` | 후보 컴파일러가 생성하는 검토용 산출물 |

후보는 별도 입력 계약으로 검증하며, 기존 Builder에 자동 유입하지 않는다.
후보 컴파일러는 기존 검증 원칙과 결정적 직렬화·해시 도구를 재사용할 수 있지만
기존 Delta 검증을 거쳤다는 의미를 임의로 부여하지 않는다. 모든 generated 파일은
입력에서 다시 생성하며 수동 수정하지 않는다.

`knowledge build --candidate`는 후보 입력 검증·원문 해시 확인·Bundle별 검토 산출물을
담당한다. `spec bundle-diff`는 두 명시적 Bundle의 후보 구조와 요구사항을 비교한다.
후보 Diff는 원문 해석의 승인이나 제품 영향 판정을 의미하지 않는다.

## 72.5 보완 정의, 충돌, 미완료 상태

두 문서가 같은 필드를 다룬다는 이유로 한 정의를 지우지 않는다. Base가 세부 의미를
명령 세트 문서에 위임한 경우에는 원문 근거가 있는 보완 관계로 연결한다. 보완 정의를
override로 취급하지 않으며, 출처 우선순위·파일 순서·마지막 기록으로 승자를 고르지
않는다. 호환 여부를 판단할 수 없는 내용은 미해결로, 상충한 정의는 충돌로 보존한다.

원문 항목마다 추출 완료, 미해결, 또는 범위 제외와 사유를 기록한다. 바이트 범위가
모두 덮였다는 사실과 모든 비트·주석·상호 참조를 검토했다는 사실은 다르다.
각 커버리지를 구분하고 누락된 요구사항을 “제약 없음”으로 처리하지 않는다.

## 72.6 이번 단계의 검증과 완료 경계

문서 식별·해시, Bundle 참조, 필드 중복·영역 겹침, 배열 경계, 하위 비트 범위,
출처 누락, 요구사항 대상 참조와 결정성을 테스트한다. 합성 오류 테스트와 실제
원문에서 확인한 변경 사례를 구분한다. 기존 Builder·CLI 회귀 검증을 유지한다.

이 단계의 산출물은 두 Bundle의 후보 지식, 후보 버전 차이, 커버리지·미해결 목록과
사람이 검토할 묶음이다. 원문 전체 검토가 끝나기 전에는 그 완료를 주장하지 않는다.
Product Profile 선택, DUT Context Resolver, 실제 SSD 수집·PASS/FAIL 판정, Excel,
SQLite와 자동 confirmed 승격은 이 단계에 포함하지 않는다.

실행과 검토 방법은 [Identify 지식 구축 절차](identify_knowledge_workflow.md)를 따른다.

---

# 73. 요구사항 중심의 규칙 실행 파일럿

## 73.1 재사용 경계와 우선순위

nvme-cli/libnvme의 명령 실행·기본 구조 해석을 재사용한다. 실제 연동 단계에서
릴리스/커밋을 고정하고 출력과 내부 필드 ID를 연결한다. 최신 헤더를 특정 규격
Bundle의 규범적 의미로 간주하지 않는다. Base 2.0e + NVM 1.0e와 Base 2.1 +
NVM 1.1은 별도 적용 범위이며 필요한 필드의 의미·비트·예외를 원문과 대조한다.
전체 Identify 구조 재추출이나 전체 오프셋 승인은 규칙 파일럿의 선행 조건이 아니다.

핵심 개발은 요구사항 → 조건·예외·의존성 → Capability → NVMe Field/Bit →
실행 가능한 Expected 제약으로 연결하는 것이다. OCP/MFND 원문과 버전이 없으면
실제 요구값을 추정하지 않고 미해결로 남긴다. 기존 구조 후보는 참조 자료다.

## 73.2 조건부·관계형 Expected

Effective Expected Profile은 고정 숫자 목록뿐 아니라 조건부 비트 요구와 필드 간
관계를 보존한다. resolve(Context, Snapshots, Mappings)는 명시적 Bundle을 선택하고,
evaluate(Expected Profile, Actual Facts)는 실제 관측값과 함께 남은 조건을 평가한다.
Actual의 기능 비트는 내부 일관성 검사의 조건으로 사용할 수 있으나, 정책에서
요구한 Capability 지원 자체의 검사를 우회하는 근거가 될 수 없다.

조건이 거짓이면 N/A, 필요한 사실이 없으면 UNKNOWN이다. 입력 타입 오류와
지원하지 않는 표현은 ERROR다. candidate/provisional과 MAY/SHOULD/동작 진술은
authoritative PASS/FAIL의 근거로 자동 전환하지 않고 REVIEW로 보존한다.
Reserved만으로 expected=0을 만들지 않는다. 모든 결과는 규칙·조건·관측값·근거와
변경 이력을 추적할 수 있어야 한다.

## 73.3 결합과 충돌

동시에 적용되는 규칙은 함께 만족해야 한다. 고정값·범위·마스크의 불가능한 교집합은
CONFLICT이며, 일반 관계식의 전역 만족 가능성까지 검사했다고 주장하지 않는다.
명시적 단일 단계 override는 confirmed 근거·이유·대상 ID를 요구하고 원래 규칙도
보존한다. Schema validation은 override할 수 없고 체인·순환은 지원하지 않는다.
규격 계층·파일 순서·last-write-wins로 승자를 선택하지 않는다.

## 73.4 구현 및 후속 범위

현재 구현은 기존 Loader/Builder와 literal 충돌 검사를 재사용한 TEST/FIXTURE 전용
실행 파일럿이다. fixture Context, bindings, 규칙과 Capability mapping을 받아
Expected Profile, fixture 판정과 trace를 JSON으로 출력한다. 실제 후보를 자동
승격하거나 실제 NVMe Bundle을 production 실행하지 않는다.

Product Profile 자동 선택·FW 비교·실제 SSD 수집·Excel·SQLite는 후속 범위다.
실행 계약·지원 제약·테스트와 후속 순서는 [규칙 실행 파일럿](rule_execution_pilot.md)을 따른다.

---

# 74. 도구 버전과 제품 규격을 분리한 Actual 정규화

제품의 적용 Bundle, 수집 도구 버전, 장치가 보고한 버전은 독립적인 정보다.
최신 CLI의 필드 이름이나 헤더 정의로 제품 Bundle·Reserved 여부·Expected를
자동 변경하지 않는다. 최신 구현은 해석 도구이며 규격별 규범적 의미의 원본이 아니다.

저장된 Identify raw와 수집 metadata를 함께 보존하고 선택한 Bundle 매핑으로
필요한 필드를 읽는다. raw 길이와 CNS/CSI/NSID/controller 질의는 정확히 확인한다.
모르는 영역은 unmapped로 보존하며 Reserved나 expected=0으로 추정하지 않는다.
전체 필드 값을 전달하므로 최신 도구의 비트 마스크 때문에 값이 유실되어서는 안 된다.

raw 없이 JSON을 사용할 때는 실제 도구 출력에 맞춘 명시적 경로 매핑을 요구한다.
추가 필드는 보존하되 제품 요구사항으로 채택하지 않고, 누락은 UNKNOWN, 타입 오류는
ERROR로 처리한다. raw 오류를 JSON으로 자동 우회하거나 누락을 0으로 채우지 않는다.
Reserved 관련 판정은 해당 Bundle의 승인된 명시적 규칙이 담당한다.

현재 오프라인 어댑터는 fixture/candidate 매핑을 읽고 관측값과 source hash를 남긴다.
OBSERVED는 정상적인 디코딩 상태이며 SSD PASS가 아니다. candidate 해석은 REVIEW다.
fixture Resolver 연결은 Source-built 필드 근거를 재사용하고 Bundle·장치·Namespace
혼합과 정규화 오류를 거부한다. 실제 장치 실행·production 판정은 아직 활성화하지 않는다.

상세 인터페이스와 실행 방법은 [Identify 정규화](actual_normalization.md)를 따른다.

## 75. 로컬 GUI와 저장 로그의 최소 사용 흐름

기존 Builder, Candidate Bundle compiler/diff, Rule Resolver/evaluate, provenance,
Actual normalizer는 계속 재사용한다. GUI는 이 서비스들을 연결하는 application 계층이며
별도 기대값 비교 엔진을 구현하지 않는다. 저장 id-ctrl 텍스트는 원문·줄·입력 hash를
보존하고 명시적으로 선택한 Bundle의 후보 정의와 요구사항에 연결한다.
candidate 연결은 REVIEW, 미확인 매핑은 UNKNOWN, 중복 입력은 ERROR,
매핑 모호성과 후보 구조 충돌은 CONFLICT다. 이 경로에서 production PASS/FAIL을 만들지 않는다.
VER와 도구 버전은 적용 Bundle을 자동 변경하는 근거가 아니다.
첫 화면은 DUT 로그 검토이며 기존 엔진은 TEST/FIXTURE 실행 패널로 제공한다.
승인된 실제 규칙과 ActualFact 연결은 후속 범위다. [GUI 사용 안내](local_gui.md)를 따른다.

## 76. 사용자 허용에 따른 검토 전 실행과 정책 가정

2026-10-11 사용자 요청으로 candidate의 실행 규칙 전환 및 정책 가정을 허용한다.
이 절은 앞선 fixture 전용 실행 및 승인 전 실행 제외 범위를 experimental 경로에 한해 대체한다.
실제 SSD 명령은 가장 후순위로 둔다. Base + NVM Bundle 선택과 Source/Builder 경계는 유지한다.

strict 모드는 기존 계약을 유지한다. 명시적 experimental 모드에서는 candidate/provisional
규칙·필드 근거를 그대로 보존하며 기존 Resolver/evaluate로 저장 DUT 로그를 평가한다.
confirmed 검토 기록을 만들지 않고, 결과 kind는 experimental_validation_report,
authoritative=false로 표시한다. PASS/FAIL의 의미는 등록된 실험 해석 및 가정에 대한 만족 여부다.
정책 가정은 Source 데이터로 표현하며 실제 제품의 공식 정책으로 주장하지 않는다.
현재 LAB_ASSUMED_DEVELOPMENT_PROFILE은 Format NVM·Firmware Download 지원을 요구한다.
실제 OCP/MFND 원문이 없으면 이 이름의 공식 요구사항으로 등록하지 않는다.

실험 충돌·누락·잘못된 입력도 CONFLICT/UNKNOWN/ERROR로 유지한다. MAY/SHOULD 자동 mandatory,
Reserved 자동 zero, 암묵적 override는 계속 허용하지 않는다. 기존 confirmed 단일 단계 override
계약은 유지한다. focused YAML projection은 전체 규격 추출 완료를 의미하지 않는다.
GUI는 DUT 규칙별 결과·Expected·Actual/Context·출처·가정을 제공한다.
구현 범위와 수정 가능한 Source는 [검토 전 규칙 실행](experimental_rules.md)을 따른다.

## 77. 저장 로그부터 필드별 판정까지 하나의 사용 흐름

기존 구현을 유지하고 일반 GUI를 로그 입력 → 공통 Actual → Bundle/Context/정책 적용 →
기존 Resolver → 필드별 Expected/판정/근거의 단일 흐름으로 통합한다.
75절의 GUI TEST/FIXTURE 실행 패널은 일반 화면에서 제거한다. 기존 CLI와 application
서비스는 유지하며 합성 데이터를 실제 DUT 흐름에 넣지 않는다.

텍스트 adapter는 후보 Bundle의 명시적 필드 연결을 이용해 공통 ActualFact를 보존한다.
Builder에서 나온 FieldRegistration으로 layout_from_profile을 만들고 기존 normalize_json의
타입·폭·누락 검사에 텍스트 해석 값을 전달한다. JSON은 내부 중간 표현이며 source_format은
text, 입력 hash는 원본 텍스트 바이트의 hash다. 텍스트에서 raw 응답을 재구성하지 않는다.
현재 candidate/provisional 정규화 값을 Resolver 입력으로 전달하는 것은 experimental 경로뿐이다.

공통 Actual에는 매핑된 관측값을 보존하고, 실제 규칙의 등록 필드만 validation_facts로
선택한다. 나머지 필드를 적합성이 판정된 것으로 표시하지 않는다. 한 필드의 여러 규칙을
함께 만족해야 PASS이며 타입/폭 오류는 정규화 ERROR, 필요한 누락 입력은 UNKNOWN이다.
필드 참조 관계에서 비교 입력으로 사용된 필드와 직접 제약을 판정한 필드를 구분한다.

GUI의 Bundle·Atomic 적용 Context·임시 개발 정책/규격만 적용 선택은 현재 실행 입력에
명시적으로 반영되고 결과에 저장된다. 파일 Source는 수정하지 않는다.
표의 Actual·Expected·판정과 상세 trace는 동일한 DUT 실행 결과다.
실제 SSD 명령 실행은 계속 최후순위이며 실험 결과의 authoritative=false 계약은 유지한다.

## 78. 복수 저장 응답과 검사 scope (3단계)

SavedCaptureSet은 원본 응답 바이트와 명령 종류, 형식, DUT·세션·Namespace, query와 도구 정보를
각각 보존한다. 사용자 입력 수집 사실(metadata)과 Bundle 필드 해석(interpretation)은 분리한다.
확인되지 않은 CNS/CSI/NSID는 UNKNOWN이다. raw 해석에는 명시적 CNS/CSI가 필요하다.
최신 도구 버전이나 추가 필드는 검사 Bundle을 자동 변경하지 않는다.

같은 DUT와 수집 세션을 명시한 응답만 함께 연결한다. Controller는 해당 그룹의 Namespace별
scope에 공유하고, NSID 미확인 Namespace는 응답별로 분리한다. 각 scope에서 기존 Builder,
layout_from_profile, normalize_raw/normalize_json, resolve/evaluate를 사용한다.
FieldRef의 기존 키는 유지하고 서로 다른 Namespace를 별도로 평가하여 값 덮어쓰기를 피한다.
중복/충돌은 원문과 입력 목록을 보존하고 자동 선택하지 않는다. 추가/미정의 필드는 관찰 자료다.

원본 envelope와 결과는 validation_run에 보존한다. v3 스키마를 바꾸지 않고 버전 있는 input_kind로
기존 단일 검사와 복수 입력 재실행을 구분한다. 당시 리비전/Bundle/Context/정책을 사용하며
전체 백업과 복원도 기존 서비스를 재사용한다. [입력 계약](saved_capture_inspections.md)을 따른다.
실제 id-ns 규칙과 형식 확인은 미완성이고 합성 fixture 검증과 구분한다.

## 79. 제품 Profile과 명시적 선택 (4단계)

SQLite Source의 선택적 knowledge/products.json은 ProductProfile, ProductPolicy, ProductContext를
등록한다. 기존 v3 entity_index에 투영하여 조회하며 원본/인덱스 이중 수정은 하지 않는다.
각 Profile은 하나의 Bundle과 정책 ID 목록, Context ID, 선택 조건, 명시적 FW 비교와 provenance를
참조한다. 실제 제품 자료가 없으면 빈 목록이며 제품값을 추정하지 않는다.

명시적 선택을 검사 옵션에 보존한다. API의 Bundle 불일치는 오류다. 후보 제안은 scope별로
관찰 identity/query와 사용자 입력을 비교하고 자동 선택하지 않는다. 후보 없음은 UNKNOWN,
복수 후보는 AMBIGUOUS, 누락 조건과 미등록 FW 비교는 UNKNOWN이다. FW 비교는 exact,
명시적 numeric_components, 등록 ordered_labels만 지원하며 사전순/prefix 처리를 추정하지 않는다.

제품 정책은 기존 RuntimeRule/Capability 매핑과 Builder, resolve/evaluate를 사용한다.
Profile 적용 여부를 Context gate로 보존하여 false=N/A, missing=UNKNOWN으로 평가한다.
필수 지원 요구를 Actual 지원 비트로 제외하지 않으며 충돌/승인된 override의 기존 계약을 유지한다.
Profile에서는 LAB 정책/Context를 묵시적으로 상속하지 않는다. 명시적으로 등록한 Context와
사용자 입력만 적용하며 실제 관찰 Namespace는 scope별로 연결한다.

검사 당시 Profile/정책/Context, Source hash·리비전, 선택 trace, 관찰값·사용자 입력·선언값·가정·
정책 요구·최종 Context를 분리하여 보존한다. 예전 Profile을 현재 값으로 바꿔 재실행하지 않는다.
confirmed에는 검토자와 검토 근거가 필요하며 실험 결과는 authoritative=false다.
[상세 계약](product_profiles.md)을 따른다. 실제 제품 정책/FW 자료와 후속 규격 확대는 별도 미완성이다.

## 80. 원문 대조 candidate 요구사항 확대 (5단계)

[실행 범위와 미해결 표](nvme_requirement_coverage.md)는 두 Bundle의 우선 요구사항을 기록한다.
전 구조 재추출 대신 필요한 CNS00/CNS01 필드와 배열 슬롯을 원문과 대조한다. 후보 규칙의
조건·예외·의무 수준·의존 입력·원문 페이지를 SQLite Source 리비전에 함께 보존한다.
명시적 PDF hash 검증 등록은 사전 전체 백업·CAS·수정 충돌 거절을 거쳐 기존 Builder,
정규화, resolve/evaluate를 재사용한다. 기존 schema v3와 과거 검사 이력은 유지한다.

조건 GE는 정수 literal과 정수 참조의 ≥ 비교만 지원한다. NLBAF 공통 prefix 배열 슬롯의
적용을 표현하기 위한 최소 확장이며 일반 수식/동적 lookup은 실행하지 않는다.
query/scope 적용 사실은 서비스가 만들며 사용자 입력이나 제품 Context로 덮어쓰지 않는다.
지원 비트에 종속된 Actual 일관성 검사와 제품의 필수 지원 요구는 독립적으로 유지한다.
Controller AWUPF 관계의 필수 문장은 추가 Atomic Context로 해제하지 않는다.

MAY equality는 필수로 변환하지 않고 Reserved에서 zero 기대를 만들지 않는다.
atomic zero-inheritance와 newer MAM 적용 조건을 보존한다. LBAF unique 형식/FLBAS,
ANA 상태·동작 atomic 검사는 미구현/추가 정보/동작 검사로 선언한다. 현재 결과는 candidate
실험 실행이며 모든 규격 승인·실제 SSD 적합성 완료를 의미하지 않는다.

## 81. 추가 규격 요구와 제품 정책 연결 (6단계)

SQLite의 supplemental ledger는 원문 document/version/hash, 제품 범위, requirement ID,
Capability와 NVMe Field/Bit의 근거, 직접 제약, 조건과 미검증 동작을 보존한다.
OCP2.6 candidate subset을 두 Bundle의 ProductPolicy와 CapabilityMapping에 연결하고
실제 제품 Profile 생성·적용 추정은 하지 않는다. MFND는 현 단계에서 제외한다.
선택한 Profile의 조건과 명시적 OCP 대상/버전 Context gate를 기존 Resolver로 평가한다.
Actual 지원 비트가 false라도 추가 정책의 필수 지원 요구를 제외하지 않는다.

적용 literal 제약의 불가능한 교집합은 CONFLICT이며 각 참여 출처를 보존한다.
일반 관계식의 완전한 충돌 증명은 지원하지 않는다. Override는 기존 confirmed 근거·대상·
이유·동일 instance·단일 단계 계약을 유지한다. 원래/대체 결과·검토 record와 registry hash를
supplemental_trace에 보존하고 당시 리비전으로 재실행한다. Capability check override 자체는
지원하지 않는다. 실제 OCP 동작 예외 문구를 임의의 필드 override 허가로 해석하지 않는다.

등록은 원문 hash·참조·현재 편집 충돌·CAS·사전 전체 백업을 거친 새 리비전이다.
스키마 v3, 기존 Builder·정규화·Resolver와 과거 검사를 유지한다. 확인되지 않은 실제
제품 정책값은 등록 대기이며 합성 데이터 검증을 실제 적합성으로 표시하지 않는다.
[6단계 계약](supplemental_requirements.md)을 따른다.
