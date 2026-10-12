# 제품 Profile·정책·Context (4단계)

실제 제품 자료는 아직 없다. 기본 제품명, FW 순서, 내부 정책이나 OCP/MFND 요구값을 생성하지 않는다.
기존 Profile 없는 Bundle 검사도 유지한다. 테스트 제품은 임시 DB에만 등록한다.

## 관리와 선택

GUI `제품 관리`에서 Profile, product_policy, context를 등록한다. 먼저 기존 문서 관리에서
해당 제품/정책 자료의 ID와 버전을 등록하고, 각 항목에 출처·절·지식 상태를 입력한다.
변경 사유, 참조 검증, 미리보기 해시, 리비전 충돌 거절, 검토 근거와 되돌리기는 기존 서비스를 사용한다.
confirmed 변경에는 일치하는 검토자·날짜·근거가 필요하다. 실행/빌드 성공은 승격 근거가 아니다.

- Profile: stable ID, 이름, 하나의 Bundle, 정책 ID 목록, 선택적 Context ID, 선택 조건, FW 비교와 provenance.
- 정책: Bundle, RuntimeRule 목록, provenance. 폼에서 Capability 지원/미지원 요구와 단순 Context 조건을
  입력한다. 복합 조건·필드 제약·권고 등은 고급 규칙 입력을 사용하고 기존 표현을 보존한다.
- Context: Bundle, 타입 있는 facts와 항목별 declared/assumption 출처, provenance.
  관찰 NSID와 제품 적용 여부는 preset으로 등록할 수 없다.

검사 화면에서 Profile을 **명시적으로 선택**한다. GUI가 해당 Bundle을 표시하고 등록 정책을 적용한다.
API/CLI의 Bundle이 Profile 바인딩과 다르면 ERROR이며 암묵적으로 바꾸지 않는다.
선택 후 Atomic 기본값은 `Profile Context 사용`이다. 사용자 Context 행에서 추가·덮어쓰기·
unknown(null로 제거)를 명시할 수 있다. 복수 입력의 조건을 바꿨으면 `입력 묶음 검사`를 다시 누른다.
Profile 없는 기존 임시 개발 정책 선택과 Profile 정책 선택은 별도 경로다. Profile에서는 LAB 기본 정책과
묵시적인 LAB Context 가정을 가져오지 않는다. NVMe 규격 규칙은 계속 함께 평가한다.

## 후보 제안과 적용 조건

`입력에서 후보 제안`은 입력의 Controller model(mn), firmware(fr), serial(sn), 명시적 Namespace
query 정보와 사용자 Context를 비교한다. 여러 DUT·세션·Namespace는 기존 scope별로 비교한다.
문자열과 숫자/boolean을 서로 변환하지 않으며 조건은 AND로 결합한다. 조건 trace에 값·출처·누락을 기록한다.

후보 0개는 UNKNOWN, 복수 후보는 AMBIGUOUS, 조건이 누락된 후보는 pending이다.
확정 후보 한 개여도 pending이 있으면 UNKNOWN이다. 후보 한 개이고 미확인 후보가 없어도
CANDIDATE라는 제안만 제공하며 자동 선택하지 않는다. 후보 제안은 검사 이력을 생성하지 않는다.
Controller 입력 충돌은 CONFLICT로 보존한다.

명시적 선택도 조건을 검사한다. 조건 거짓이면 해당 Profile 판정은 N/A, 누락/미등록 FW 비교는 UNKNOWN이다.
제품 정책에 `product.profile_applicable` Context gate를 추가해 미확인 조건을 PASS로 평가하지 않는다.
이 gate는 Actual 지원 비트로 결정하지 않으며 사용자 Context에서 직접 덮어쓸 수 없다.
필수 기능의 Actual 지원 비트가 꺼져 있으면, Profile이 적용되는 경우 요구사항은 FAIL이다.

## FW 비교

비교 방법은 Profile에 등록한다. 정의가 없으면 같은 문자열이라도 FW 조건은 UNKNOWN이다.

| 방법 | 계약 |
|---|---|
| exact | 문자열 동등 비교만. 범위/정렬을 정의하지 않음 |
| numeric_components | 명시한 개수의 점 구분 정수 구성요소만. 예: TEST의 1.10.0은 1.2.0보다 큼 |
| ordered_labels | 등록한 문자열 순서 목록의 위치로 비교. 미등록 label은 UNKNOWN |

FW_RANGE 경계는 양쪽 포함이다. prefix 제거, 사전순 비교, 자연 정렬, 제품별 if/else나 일반 수식을
추정하지 않는다. 잘못된 등록 경계/역전 범위는 저장 전에 거절한다. 실제 제품의 FW 비교 방식은
제품 자료 확보 후 입력해야 하며 위 TEST 예제를 실제 제품 정의로 사용하지 않는다.

## 저장과 trace

`knowledge/products.json`은 SQLite의 불변 Source 문서이며 파일 export/import 형식의 논리 경로다.
legacy 파일과 두 개의 수정 가능한 원본을 만들지 않는다. v3 entity_index의 기존 kind/bundle/ID
구조에 profile/product_policy/context 검색 인덱스를 저장한다. 새 SQL 테이블이나 스키마 migration은
필요하지 않으며 옛 리비전에 이 문서가 없으면 빈 등록 목록으로 해석한다.

각 scope의 product_selection은 당시 Profile·정책·Context 전체, Profile hash, 원본 registry source hash와
DB 리비전, 조건 trace, 관찰값과 원본 capture source, 사용자 입력, 선언 Context, 가정,
정책 요구, 최종 Context를 분리해 보존한다. profile_id도 검사 옵션에 저장한다.
과거 검사 조회·당시 리비전 재실행·전체 DB 백업/복원은 기존 경로를 사용한다. 수정된 최신 Profile로
옛 검사를 바꿔 실행하지 않는다. Namespace NSID는 각 scope의 명시적 수집 정보에서 연결한다.

제품 정책은 기존 Builder와 등록 Capability 매핑, Resolver의 조건·제약·충돌·override를 사용한다.
암묵적 우선순위와 last-write-wins는 없으며 승인된 단일 override의 기존 계약을 유지한다.
candidate/provisional 상태를 변경하지 않고 experimental 결과는 authoritative=false다.

API: `/api/products`, `/api/profiles/suggest`, 기존 `/api/entity/preview`·`save`,
`/api/analyze`·`analyze-captures`의 profile_id. GUI와 CLI 모두 같은 서비스를 사용한다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli actual review-captures --input saved-input.json --bundle <등록한-Bundle> --profile <등록한-Profile-ID> --experimental
```

실제 제품 Profile·FW 비교·정책 자료, 실제 id-ns 응답과 OCP/MFND 요구사항 등록은 여전히 미확보다.
이번 단계는 관리·선택·판정·재현 기능을 구현하며 실제 제품 적합성 완료를 의미하지 않는다.

## 프로젝트 완성 계획 6단계: 추가 규격 연결 (2026-10-12)

[추가 규격 계약과 적용 범위](supplemental_requirements.md)에 따라 OCP DSSD2.6 원문 hash와
요구 ID를 보존하여 두 Bundle의 요구사항 → Capability → NVMe Field/Bit 및 직접 제약을
candidate로 등록한다. 제품 Profile에 명시적으로 연결한 정책과 적용 Context만 실행하며
실제 제품값·적용 대상·FW를 추정하지 않는다. MFND는 사용자 지시로 제외한다.
기존 엔진의 충돌·단일 명시적 override와 원래/대체 규칙·검토 근거를 trace로 연결한다.
실제 제품 바인딩과 정책 자료, 기타 OCP 요구·동작 검사는 등록 대기/미구현으로 구분한다.
