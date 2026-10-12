# 추가 규격과 제품 정책 — 6단계

기준: 2026-10-12. MFND는 사용자의 지시에 따라 제외한다. 확보된 OCP 원문은
`OCP2_6.pdf`, **Datacenter NVMe SSD Specification Version 2.6 (09252024)**, 211페이지다.
SHA256: `44ccfd8c1b40eae70fa292a231379448182c5987456fe75e0d54fe6befd96872`.
원문 §3의 PCIe-attached Datacenter NVMe SSD 범위와 §4.1 NVMe-1의
Base2.0e/NVM1.0e/PCIe Transport1.0e or later 요구를 보존한다. Transport 원문과
compliance report가 없어 전체 OCP/NVMe 적합성으로 판정하지 않는다.

## 원문 기반 candidate 등록

원문 p9–11, p15의 표를 확인하고 기존 두 NVMe Bundle에 각각 아래 subset을 연결한다.
`candidates/ocp/requirements.json`은 재현 가능한 원문 대조 후보 패키지이며 실제 원본은
명시적으로 등록한 SQLite의 `knowledge/supplemental_requirements.json`, 제품 정책과
Bundle Capability 매핑이다. 파일 변경으로 기존 DB를 자동 갱신하지 않는다.
전체 OCP 추출이나 사람 승인을 수행한 것은 아니다.

| OCP 요구 ID | 원문 물리/인쇄 페이지 | Capability 또는 직접 제약 | 필드/비트 | 남은 범위 |
|---|---:|---|---|---|
| NVMe-CFG-14 | 10 §4.3 | MASK 0xf0 = 0x60 | CNS01.SQES[7:4] | NVMe low nibble/minimum 규칙과 함께 적용 |
| NVMe-CFG-15 | 10 §4.3 | MASK 0xf0 = 0x40 | CNS01.CQES[7:4] | NVMe low nibble/minimum 규칙과 함께 적용 |
| NVMe-CFG-19 | 10 §4.3 | EXACT 0 각각 | CNS01.HMPRE, HMMIN | 명시적 HMB 미지원 요구; Reserved에서 생성하지 않음 |
| NVMe-AD-3 / AD-4 | 10 §4.4 | OCP.ADVERTISED.NAMESPACE_MANAGEMENT | CNS01.OACS bit3 | Namespace Management/Attachment 실제 실행·동작 |
| NVMe-AD-5 | 10 §4.4 | OCP.ADVERTISED.FORMAT_NVM | CNS01.OACS bit1 | SES 000/001/010 및 Format 실제 동작 |
| NVMe-AD-6 | 10 §4.4 | OCP.ADVERTISED.NVME_MI | CNS01.OACS bit6 | MI Receive tunneling/Send 금지의 실제 동작 |
| NVMe-AD-12 | 11 §4.4 | OCP.ADVERTISED.DEVICE_SELF_TEST | CNS01.OACS bit4 | Self-test 실행, 결과·이력 |
| NVMe-IO-9 | 15 §4.5 | OCP.ADVERTISED.COMPARE_WRITE | CNS01.FUSES bit0 | Fused operation 실제 동작·atomicity |
| NVMe-AD-2 | 10 §4.4 | OCP.ADVERTISED.OPTPERF | CNS00.NSFEAT bit4 | FPI 진행률, 기타 performance/endurance hint 값 |

10개 요구 ID, 11개 실행 규칙, 6개 Capability 매핑을 Bundle별로 등록한다.
AD-3/AD-4는 같은 지원 비트에 연결되지만 원문 요구 ID와 판정을 각각 유지한다.
Capability 지원 값은 비트 1, 미지원 값은 0이며 해당 NVMe 필드 정의로 매핑한다.
OACS는 Base2.0e p270 / Base2.1 p330 Fig280/312, FUSES는 p281/p341,
NSFEAT는 NVM1.0e p57 / NVM1.1 p81 Fig97/114 근거다. 최신 구조를 옛 Bundle에 이식하지 않는다.
NVM1.1 OPTPERF는 NSFEAT[5:4] 2비트 인코딩(p81, p90 Fig115)이다. OCP 원문이 요구한
bit4만 검사하여 01b/11b를 허용하고 10b를 단순 nonzero 지원으로 통과시키지 않는다.
bit5를 임의로 지우지 않으며 전체 hint 값 적합성은 별도 미구현 범위다.
새 필드나 전체 구조를 추출하지 않고 5단계에서 등록한 필요한 필드를 재사용한다.

모든 추출 규칙·매핑은 candidate, 검토자/confirmed는 만들지 않는다. 정책은 제품별 내부값을
추정한 것이 아니라 OCP 추가 규격의 subset이다. 실제 Samsung/제품 Profile이나 FW 기준은
제공되지 않았으므로 제품 Profile을 자동 생성하거나 DUT가 OCP 대상이라고 추정하지 않는다.

## 적용 계약과 GUI 사용

1. 기존 5단계 NVMe 등록과 스키마 v3 DB를 유지한다. OCP 등록은 원문 hash, 참조, 현재
   정책/매핑 충돌, 예상 리비전을 확인한 뒤 전체 사전 백업과 새 Source 리비전으로 진행한다.
2. 제품 관리에서 **실제 근거가 있는 Profile**에 해당 Bundle의
   `OCP.2_6.<bundle_id>` 정책을 연결한다. 기존 Profile의 Bundle·선택 조건·FW 비교를 유지한다.
3. 적용 제품의 Context에 `ocp.datacenter_product` boolean true, `ocp.version` string
   `2.6`을 명시한다. 이 값은 사용자의 선언/제품 자료이며 관찰값에서 추정하지 않는다.
4. Profile을 선택해야 정책이 실행된다. Profile 없이 Context만 넣으면 정책은
   `not_selected`다. 연결된 정책의 experimental 실행을 끄면 `review_only`로 구분한다. Profile 적용 조건과 OCP 선언이 missing이면 UNKNOWN, false나 다른
   버전이면 N/A다. Namespace 규칙에는 서비스가 만든 특정 query scope gate도 필요하다.
5. 지원 여부는 독립적인 정책 요구다. Actual 지원 비트를 지워도 필수 지원 규칙이 N/A가
   되지 않고 FAIL이다. NVMe의 optional feature 일관성 검사는 별도로 함께 실행한다.

GUI의 `추가 규격 요구사항` 패널에서 버전·요구 ID·Capability·Field/Bit·원문·동작 검사 범위와
현재 규칙의 등록 상태, 연결 Profile, 대기 목록을 확인한다. 기존 제품/Capability 관리 폼,
미리보기·검토 근거·리비전 CAS를 재사용한다. 복잡한 직접 제약과 override는 기존 제품 정책의
고급 규칙 입력을 사용한다. 등록된 ledger 참조를 dangling 상태로 삭제하면 저장을 거절한다.
필요하면 ledger와 정책의 동시 변경을 검증된 Source 패키지로 반영한다.

```powershell
.\.venv\Scripts\python.exe tools/prepare_ocp_requirements.py
.\.venv\Scripts\python.exe -m ssd_validator.cli database status
# 예시: 5단계가 끝난 실제 현재 head가 r2일 때
.\.venv\Scripts\python.exe -m ssd_validator.cli knowledge register-supplemental --recipe candidates/ocp/requirements.json --pdf-dir .. --expected-revision 2 --reason "OCP2.6 source-read candidate subset; product applicability pending"
```

PDF hash 또는 기존 정책·매핑·문서 내용이 다르면 덮어쓰지 않고 오류로 중단한다.
같은 입력의 재등록은 변경 없음으로 반환한다. 파일 bootstrap은 후보 패키지를 실행 정책으로
자동 등록하지 않는다. 생성된 Snapshot/Excel을 원본으로 사용하지 않는다.

## 충돌, override와 trace

규칙은 함께 만족해야 한다. 적용된 NVMe·추가 규격·제품 정책의 literal 교집합이 불가능하면
CONFLICT와 참여 규칙 ID·원래 제약·각 출처를 함께 표시한다. 충돌 그룹은 최소 모순 집합을
증명한 것이 아니며 `active_literal_constraints_only`다. 일반 관계식의 모든 충돌 가능성,
미적용/미확인 조건의 잠재 충돌을 완전히 증명했다고 주장하지 않는다. candidate의 strict 모드는
REVIEW이며 experimental에서만 후보 제약을 실행한다.

명시적 override는 기존 엔진 계약을 유지한다. confirmed 대체 규칙과 confirmed override 근거,
대상 ID, 이유, 검토자·날짜·검토 근거가 필요하다. 동일 필드/배열 instance만 허용하고 schema,
없거나 자기 자신인 대상, 체인/순환은 거절한다. Capability check 자체의 override는 지원하지
않으며 명시적 직접 필드 제약으로 표현·검토해야 한다. OCP NVMe-1의 일반 예외 문구만으로
자동 override를 만들지 않는다. 실제 OCP NVMe-AD-19 sanitize 예외는 동작 검사가 필요하여
이번 snapshot override로 실행하지 않는다.

결과의 `supplemental_trace`는 다음을 당시 리비전으로 보존한다.

- 원문 document/version/hash, 적용 제품 범위, requirement ID와 candidate 조건·예외/잔여 범위.
- 선택한 정책의 원래 rule, 실제 사용한 Capability mapping, expanded rule의 origin_rule_id와
  NVMe mapping provenance, 최종 조건·입력·판정.
- 충돌 참여 규칙 및 각 근거, override의 원래/대체 규칙 결과와 이유·review evidence·일치하는
  내용 해시의 product_policy 검토 기록, 실제 적용 여부.
- registry Source 경로/hash와 등록 대기 목록. Profile/Context/정책 원본은 기존 snapshot도 유지한다.

후보 제안과 실제 편집한 정책은 분리한다. `edited_review_needed`는 현재 정책/매핑이 원래
추출 후보와 달라졌음을 뜻한다. candidate rule은 제안이며 outcomes/effective_mappings가
실제 적용값이다. 과거 검사는 현재 규칙으로 바꾸지 않고 당시 Source 리비전으로 재실행한다.

## 완료와 대기 항목

| 항목 | 상태 | 필요한 후속 입력/검증 |
|---|---|---|
| OCP 2.6 우선 subset → Capability/직접 필드 → 기존 엔진 | candidate 등록 | 독립 사람 검토와 제품 적용 선언 |
| NVMe·OCP·제품 literal 충돌 및 단일 override 추적 | TEST 기능 검증 | 실제 예외 원문·허용 근거·검토 기록 |
| 실제 제품 정책/내부 기대값/제품 FW/OCP device profile | 등록 대기 | 제공된 자료 없음; 값이나 제품 식별값을 생성하지 않음 |
| MFND | 제외 | 사용자 지시에 따라 분석/등록하지 않음 |
| 실제 OCP 제품 적용 검사 | 등록 대기 | 제품 Profile에 OCP 정책 바인딩과 적용 Context 필요 |
| OCP 전체 규격, register/log/feature·보안·전원·§13 profile | 미구현 | 별도 원문 분석과 필요한 수집/관찰 입력 |
| Format/MI/DST/fused/OPTPERF의 실제 동작 | 동작 검사 필요 | Identify advertised bit PASS만으로 증명하지 않음 |
| 실제 SSD 명령 | 후순위 | 이번 범위에서 실행하지 않음 |

`test_supplemental_requirements.py`는 두 Bundle의 22개 규칙 인스턴스에 정상·위반·경계·
조건 거짓/버전 불일치·누락·출처, 지원 비트 우회 방지, Profile 미선택, cross-source 충돌,
TEST 단일 override와 검토 근거·과거 재현을 검증한다. 등록 hash/CAS/백업/멱등성도 확인한다.
실제 제품 정책이 없는 기능 검증은 TEST/임시 DB에서만 수행하며 실 DB에 합성 제품을 남기지 않는다.
HTTP/CLI 통합 테스트는 같은 서비스와 session guard, 관리 검색과 trace를 검증한다.

검증 기록: 전체 회귀 **743개 통과**(882.81초). 추가 내용 해시/검토 근거와
review-only 분리의 영향 경로 집중 테스트도 통과했다. 실제 DB schema v3를 유지하고
사전 백업 `data/backups/pre-stage6-r2-133467825b294aeeb292f9932c6de885.sqlite3` 후 r3에
후보 정책 2개를 등록했다. 실제 제품 Profile은 0개이며 기존 15개 저장 결과가 동일하다.
r2의 GUI 검사 #15 재실행(#16)이 일치했다. 첨부 로그 r3 검사 #17/#18/#19의 기존 NVMe
판정은 PASS, OCP는 제품 적용 바인딩이 없어 not_selected다. 실제 SSD 명령은 실행하지 않았다.
