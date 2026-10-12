# 조건부·관계형 규칙 실행 파일럿

## 현재 구현과 실행

전체 Identify 구조 재추출보다 요구사항·조건·예외·Capability 매핑을 우선한다.
이 파일럿은 실제 SSD를 수집하지 않고 합성 TEST/FIXTURE로 Resolver를 검증한다.
실제 NVMe 후보를 confirmed로 승격하지 않으며 OCP/MFND 실제 정책 값을 포함하지 않는다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli pilot run --source tests/fixtures/rule_pilot/knowledge --input tests/fixtures/rule_pilot/input.json
.\.venv\Scripts\python.exe -m pytest tests/unit/test_rule_pilot.py tests/integration/test_rule_pilot_cli.py -q
```

첫 명령은 기존 YAML Loader/Builder로 Source를 다시 빌드하고, 명시적으로 선택한
Snapshot에서 필드 정의·provenance·변경 이력을 가져온다. JSON 입력의 `bindings`는
필드 ID와 CNS/CSI, 배열 개수만 연결한다. 생성된 Snapshot을 Source로 입력하지 않는다.
샘플의 규격 이름·오프셋·질의 코드·제품 기능과 값은 합성 테스트 데이터다.
샘플 결과는 PASS 5개와 N/A 1개이며 실제 SSD 규격 적합성을 의미하지 않는다.

JSON 출력에는 Effective Expected Profile, 규칙별 결과, 원문/fixture 근거와
필드 변경 이력, 조건 참조와 관측값, override/충돌 관계가 포함된다.
추가 규칙·mapping·Context·Actual을 담은 입력 JSON의 경로와 원본 바이트 SHA-256도 보존한다.
CLI는 JSON을 표준 출력에만 쓰고 파일이나 generated 산출물을 수정하지 않는다.
완료한 보고서에서 FAIL/UNKNOWN/ERROR가 나온 경우에도 CLI 실행 자체는 성공할 수 있다.
계약 파싱·중복 키·선택 오류는 종료 코드 1로 실패한다. 소비자는 보고서의 status를 확인한다.

## 데이터와 인터페이스

`resolve(context, snapshots, mappings)`는 fixture Snapshot만 실행한다. Context의 Bundle과
mapping의 Bundle은 같아야 하고, 입력 Snapshot 집합은 명시적 `snapshot_keys`와 정확히
일치해야 한다. 각 요구사항 계층의 `schema_ref`도 선택해야 한다. Bundle의 Base/NVM
revision은 명시적으로 기록하며 다른 Bundle의 규칙을 자동 병합하지 않는다.
파일럿의 합성 revision은 실제 NVMe Bundle을 대신하는 승인 데이터가 아니다.

`PilotInput`은 Context, Bundle, 필드 bindings, 추가 규칙, Capability mappings,
정규화 Actual facts를 받는다. 배열은 `FieldRef(field_id, index)`로 식별하고 비트는
별도 `bit`로 참조한다. Actual 입력은 비트 디코딩 전의 전체 필드 값이다.
모든 선택된 Schema 필드를 등록해야 하며 필드 정의·이력·출처를 임의로 교체할 수 없다.

`evaluate(expected_profile, actual_facts)`는 조건을 Actual과 함께 다시 평가한다.
정수는 Schema 길이에 맞는 unsigned 값이며 bool, 문자열 숫자, 음수와 범위 초과를
허용하지 않는다. 문자열은 string 타입만 허용한다. bytes 정규화는 아직 지원하지 않는다.
사용하지 않는 Actual 필드도 타입·등록·인덱스를 검증해 `input_errors`에 남긴다.
중복 Actual 항목은 덮어쓰지 않고 입력 계약 오류로 거부한다.

## 규칙 의미와 안전 경계

조건은 Context의 명시적 path 또는 Actual의 필드 참조에 대한 EQ, BIT_SET/CLEAR,
AND/OR/NOT을 지원한다. 동등 비교는 타입까지 일치해야 한다. 누락은 UNKNOWN이다.
AND에서 거짓, OR에서 참은 다른 UNKNOWN보다 결정적이며 NOT UNKNOWN은 UNKNOWN이다.
잘못된 타입은 Boolean 단락 평가로 숨기지 않고 ERROR로 남긴다.
조건과 필요한 관측값은 출력에 보존한다.
Context 키와 path의 앞뒤 공백은 거부해 정규화에 의한 키 충돌을 방지한다.

제약은 EXACT, MIN/MAX, RANGE, ENUM, BIT_SET/CLEAR, MASK와 숫자 필드 간
`=`, `!=`, `<`, `<=`, `>`, `>=` 비교를 지원한다. 비교 필드도 배열/비트 참조가 가능하다.
LOOKUP, DERIVED, 임의 코드, 일반 수식, OPTIONAL/NOT_APPLICABLE check 실행은
지원하지 않으며 ERROR로 표시한다. N/A는 실제 조건이 거짓인 경우에 생성한다.
기존 rule의 applies_when/applicable_when은 Context 조건으로 각각 보존해 AND로 평가한다.

Context에서 조건을 확정하면 READY/N/A/UNKNOWN으로, Actual 의존성이 남으면
CONDITIONAL로 기록한다. evaluate는 이 조건을 실제 입력과 함께 재평가한다.
필수 Capability 규칙은 mapping으로 필드/비트의 EXACT 제약으로 확장한다.
원래 rule ID와 규칙·mapping의 근거를 모두 보존한다. 매핑이 없으면 ERROR다.
한 Capability를 여러 표현에 연결할 수 있으나 Capability 규칙 자체의 override는
파일럿에서 지원하지 않는다. 필수 기능 요구와 Actual 지원 비트에 따른 일관성 검사를
독립적으로 작성해야 한다. Actual 비트가 0이라고 필수 지원 요구가 제외되지 않는다.

모든 authoritative 근거는 confirmed와 검토자/날짜가 필요하다. 파일럿의 confirmed
근거는 fixture여야 한다. candidate/provisional/deprecated 근거 및 MAY/SHOULD/설명/
동작 진술은 REVIEW로 보존한다. malformed expression은 승인 상태와 별개로 ERROR다.
필드 등록 근거도 authority 판단에 포함한다. Reserved는 자동 zero 제약이 아니다.
명시적인 Schema must_be_zero만 별도 규칙으로 만들고 원래 Schema 이력을 연결한다.

동시에 적용되는 authoritative literal 제약의 교집합은 기존 Builder의 검사 기능을
재사용한다. 불가능한 고정값·범위·비트·마스크는 CONFLICT이며, Actual 조건이 있는
제약은 조건이 참으로 확정된 뒤 검사한다. UNKNOWN 조건을 임의로 활성화하지 않는다.
일반 관계식의 전역 만족 가능성 검사는 하지 않는다. 출력은 이 한계를 명시한다.

override는 confirmed 근거·이유·정확한 rule ID를 가진 단일 단계만 허용한다.
같은 필드/배열 항목에만 적용하며 Schema validation은 override할 수 없다.
적용 조건이 참이고 근거가 authoritative인 override만 원래 규칙을 제외한다.
원래 규칙은 N/A와 overriding ID로 결과에 남긴다. 체인·순환·누락 대상은 ERROR다.
같은 대상에 대한 복수 override는 서로의 제약도 함께 만족해야 한다.
파일 순서·계층 순서·last-write-wins로 승자를 고르지 않는다.

전체 상태의 우선순위는 ERROR, CONFLICT, FAIL, UNKNOWN, REVIEW, PASS, N/A다.
전체 PASS는 REVIEW/UNKNOWN을 포함하지 않는다. 규칙별 결과를 함께 확인해야 한다.
입력 순서가 의미를 바꾸지 않도록 필드·규칙·선택 Snapshot·결과를 정렬한다.

## 규격 검토와 후속 순서

대표 NVMe 후보는 용량 관계, THINP=0 조건, LBADS 인코딩과 unavailable sentinel,
AWUPF/AWUN 관계다. 각 후보는 Bundle·질의 조건·적용 범위·예외·의존 상태·원문
페이지를 검토표에 기록한다. 특히 원자성 표의 지원 조건과 NVM 1.1의 모드 범위를
누락하지 않는다. 이번 원문 대조는 AI 검토이며 인간 승인이나 전체 참조 완료가 아니다.

실행 모델은 대응하는 합성 FIXTURE로 검증했다. 실제 후보 데이터는 여전히
candidate/not_executable이며 자동으로 런타임 규칙에 변환하지 않는다.
OCP·MFND 원문과 대상 버전을 확보하면 요구사항 → Capability → NVMe Field/Bit로
분해하고 Context별 적용 조건을 원문과 함께 검토한다. Source 없이 값을 추정하지 않는다.

후속 개발 순서:

1. 대표 NVMe 규칙의 인간 검토 및 근거·적용 조건 승인.
2. 실제 OCP/MFND 문서의 요구사항·Capability·필드 매핑 후보 작성.
3. Product Profile Loader, DUT Context와 선택 모호성·FW 비교 계약 확정.
4. 승인된 실제 지식의 다중 문서 Bundle 실행 어댑터와 제품 Resolver 구현.
5. nvme-cli/libnvme 릴리스·커밋을 고정한 정규화 어댑터와 실제 수집 연동.

구조 해석은 기존 구현을 재사용하고 필요한 필드의 규격별 의미 차이만 대조한다.
실제 SSD, Excel, SQLite와 자동 confirmed 승격은 이번 범위 밖이다.

## 추가 구현: 오프라인 Actual 정규화

최신 도구의 수집 이력과 제품 Bundle을 분리하는 raw/JSON 어댑터를 구현했다.
Source-built Profile의 필드를 재사용하며 raw 전체 비트를 유지하고 미매핑 영역을
Reserved로 추정하지 않는다. JSON 누락은 UNKNOWN이고 후보 해석은 REVIEW다.
여러 수집 응답을 결합하는 fixture 경로는 Bundle·장치·Namespace·질의·근거를 검증한다.
실제 장치 수집이나 production 적합성 판정은 아직 포함하지 않는다.
상세 계약과 실행 명령은 [Identify 정규화](actual_normalization.md)를 따른다.

## 프로젝트 완성 계획 5단계 (2026-10-12)

[원문 대조와 실행 범위 표](nvme_requirement_coverage.md)에 따라 두 Bundle의 우선 요구사항을
candidate로 확대했다. 용량·THINP·공통 LBAF 인코딩/metadata·atomic 상속/관계·큐 max·
RPMB/ACWU/HMB와 새 Bundle HIR 일관성을 기존 Builder·정규화·Resolver로 실행한다.
원문 hash를 확인한 명시적 등록, 사전 전체 백업·리비전 CAS와 과거 검사 재현을 유지한다.
실행 규칙은 사람 검토 전 candidate이고 실제 id-ns는 TEST/FIXTURE 검증이다.
전체 구조 재추출·실제 SSD 명령·OCP/MFND·제품값 추정은 수행하지 않았다.
