# SSD NVMe ID Validation & Knowledge-Based Test Automation System
## Software Design Specification (SDS)

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

## 2.4 NVMe Base Spec과 OCP/MFND 같은 Requirement Spec의 역할을 분리한다

### NVMe Base Spec
주로 **Schema/Meaning**을 정의한다.

- Field 존재 여부
- Offset
- Length
- Bit 의미
- Reserved / Defined
- Value Type
- Feature 의미

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
                 │ YAML/JSON + SQLite Cache    │
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

YAML이 Source of Truth이다.

SQLite는:

```text
Compiled Query Cache
```

로 사용한다.

```text
YAML Source
↓
Schema Validation
↓
Delta Build
↓
Conflict Check
↓
Effective Snapshot
↓
SQLite
```

SQLite 파일:

```text
generated/knowledge.db
```

삭제해도 Source YAML에서 재생성 가능해야 한다.

---

# 37. SQLite 권장 Table

초기 설계:

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
- SQLite는 전체 Knowledge를 빠르게 Query하기 위한 Cache 역할

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
