# 현재 구현과 미완성 범위

기준: 2026-10-12, 프로젝트 완성 계획 6단계.
이 문서는 현재 구현 사실을 요약한다. 전체 목표 구조는 설계 문서를 따른다.

## 1단계 검증 결과

- 전체 회귀: 374개 통과. 새 DB 보호/CLI 테스트 8개를 추가했고 기존 GUI API 테스트를 확장했다.
- 백업/복원/이력/버전 migration 집중 테스트: 9개 통과.
- 첨부 로그 재검사: 규칙 6개 PASS, 필드 PASS 5 / REVIEW 61 / UNKNOWN 3, 원본 리비전 r1 유지.
- 실제 DB migration 전후 비교: 원본 문서 9개와 기존 검사 7개의 입력·옵션·결과가 동일하다.
- 새 규칙·정책 값·실제 SSD 명령을 추가하지 않았다. JavaScript 문법과 diff whitespace도 확인했다.
- 다음 작업은 2단계 지식 관리 GUI다. 이번 완료 범위는 1단계이며 2–8단계 완료를 의미하지 않는다.

## 구현

- 기존 Base/Delta Builder, Source 검증, Snapshot/Manifest/Spec Diff.
- 기존 resolve/evaluate, 조건·비트·관계 제약, 명시적 override와 출처 추적.
- 두 규격 Bundle 후보: Base 2.0e + NVM 1.0e, Base 2.1 + NVM 1.1.
- id-ctrl 텍스트 로그와 공통 Actual, 초기 6개 필드/규칙과 5단계 focused 요구사항 확대.
- raw/JSON 정규화 서비스와 GUI 복수 입력 연결. 단일 자동 입력은 기존 id-ctrl 텍스트 경로다.
- SQLite 원본 문서/리비전, 실행 규칙·정책 편집, 원본 교환, 검사 이력·당시 리비전 재실행.
- 현재 스키마 v3: 지원 버전 확인, v1/v2 자동 사전 백업과 감사 migration, 실패 rollback.
- 전체 DB 온라인 백업 및 검증 후 복원, 복원 전 자동 백업, 복원 후 오래된 편집 거절.
- GUI와 CLI의 DB 상태·백업·복원. [운영 절차](database_operations.md)를 따른다.

## 2단계 추가 구현

스키마 v3 entity_index와 v2 사전 백업/migration, DB 기반 Bundle 선택을 추가했다.
Bundle·문서·실행 필드·비트·배열·Capability 폼과 검색, 단순 조건/관계식 입력,
검증된 변경 전후 미리보기, 참조 검증, 내용 해시별 검토 기록, 새 리비전으로 되돌리기를 제공한다.
원본과 인덱스를 한 트랜잭션에서 유지하고 기존 결과 조회/당시 리비전 재실행을 보존한다.
[사용 계약](knowledge_management.md)을 따른다.

## 3단계 추가 구현

복수 id-ctrl/id-ns 저장 텍스트와 raw/JSON 입력을 하나의 GUI/API/CLI 검사로 연결한다.
DUT·수집 세션·Namespace별 공통 Actual과 Expected/판정을 분리하며 추가 필드·배열·누락·
중복·충돌·원문 해시를 보존한다. 확인되지 않은 수집 query와 도구 버전은 UNKNOWN이다.
DB v3의 기존 불변 검사 저장을 사용하므로 스키마 변경 없이 과거 단일/복수 검사와 전체
백업·복원을 지원한다. [입력 및 판정 계약](saved_capture_inspections.md)을 따른다.
실제 id-ns 실행 규칙은 등록하지 않았다. 합성 규칙은 임시 테스트 DB에서만 검증한다.

검증: 전체 회귀 390개 통과(432.33초), 추가 nested JSON 오매핑 방지 테스트와 영향 경로
집중 검증 통과. 실제 DB의 첨부 Controller 검사 #10에서 규칙 6개 PASS, 지식 r1 유지,
CNS/CSI/NSID/도구 버전 UNKNOWN 보존을 확인했다. JS 문법·Python 컴파일·diff whitespace 확인.
실제 추가 Namespace 로그가 없어 실제 id-ns 형식 수용 테스트는 대기 중이다.

## 4단계 추가 구현

제품 Profile·Bundle 바인딩·제품 정책/Capability 요구·Context를 SQLite 리비전과 GUI에서
관리한다. 명시적 Profile 선택과 scope별 후보 제안, 등록 FW 비교, 조건 누락/복수 후보 처리,
관찰값·사용자 입력·선언 Context·가정·정책 요구 분리, 당시 설정과 원본 hash를 보존한다.
실제 제품값은 추가하지 않았으며 TEST 등록·선택·판정·이력·백업/복원은 임시 DB에서 검증한다.
Profile이 없는 기존 검사·옛 리비전도 유지한다. [계약과 사용법](product_profiles.md)을 따른다.

검증: 전체 회귀 405개 통과(553.44초), 별도 제품 GUI/API/CLI 통합 테스트 통과.
FW 경계/미등록 비교, 없음·복수·조건 누락, 필수 Capability 우회 방지, Namespace Context,
당시 Profile/정책으로 재실행, 참조·검토·CAS와 백업/복원을 TEST 데이터로 검증했다.
브라우저에서 실제 DB r1/Profile 0개, 관리 폼과 첨부 로그 검사 #11의 기존 6개 PASS,
PASS 5 / REVIEW 61 / UNKNOWN 3을 확인했다. 실제 제품값이나 SSD 명령을 추가하지 않았다.

## 미완성

| 범위 | 현재 상태 |
|---|---|
| 전체 지식 관리 GUI | 실행 레지스트리 폼 구현. PDF 구조 후보/nested template 전체 편집은 패키지 경로 |
| 복수 응답 통합 | 저장 입력 묶음 구현. 실제 id-ns 로그 및 추가 명령 형식 확인 대기 |
| 제품 Profile/FW | 명시적 선택·등록 비교·후보 제안 구현. 실제 제품 정의·FW 비교 자료 미확보 |
| NVMe 규칙 coverage | focused 파일럿. 전체 요구사항 검증 완료 아님 |
| OCP | DSSD2.6 우선 10개 요구 ID candidate 등록. 실제 제품 바인딩/전체 OCP/동작 검사는 대기 |
| MFND/실제 제품 정책 | MFND는 사용자 지시로 제외. 실제 제품 정책 원문과 적용 정의는 미확보 |
| 보고서/배포 | JSON 내보내기와 개발 서버. 정식 수용 테스트/배포 묶음 미완성 |
| 실제 SSD 명령 | 미구현, 최후순위 |

## 판정의 의미

검토 전 규칙은 experimental로 실행하며 provenance의 candidate/provisional은 그대로 남는다.
authoritative=false다. 일부 실행 규칙의 PASS는 전체 Identify 필드 또는 제품 적합성 PASS가 아니다.
로그 입력 누락은 UNKNOWN, 잘못된 타입은 ERROR, 불가능한 규칙 조합은 CONFLICT로 보존한다.

첨부 id-ctrl 로그의 기존 기본 결과: 규칙 6개 PASS,
필드 PASS 5 / REVIEW 61 / UNKNOWN 3. 1단계는 이 규칙과 기대값을 변경하지 않는다.

## 운영상 남은 제한

- DB 복원은 하나의 서버만 같은 DB를 사용하는 조건으로 수행한다.
- 전체 백업 복원 업로드는 현재 64 MiB로 제한한다.
- 전체 규격 문서/필드를 개별 관계형 테이블로 분해한 상태는 아니다.
- 새 규격 쌍의 무근거 복제는 거절한다. 새 버전/추출 원문은 검증된 전체 패키지로 가져온다.
- 모델/Builder/Resolver 코드의 버전별 실행 파일 보관은 구현하지 않았다. 현재 검사 결과 자체는
  보존되며, 향후 엔진 동작 변경 시 과거 리비전 재실행의 호환성을 별도로 검증해야 한다.

## 프로젝트 완성 계획 5단계 (2026-10-12)

[원문 대조와 실행 범위 표](nvme_requirement_coverage.md)에 따라 두 Bundle의 우선 요구사항을
candidate로 확대했다. 용량·THINP·공통 LBAF 인코딩/metadata·atomic 상속/관계·큐 max·
RPMB/ACWU/HMB와 새 Bundle HIR 일관성을 기존 Builder·정규화·Resolver로 실행한다.
원문 hash를 확인한 명시적 등록, 사전 전체 백업·리비전 CAS와 과거 검사 재현을 유지한다.
실행 규칙은 사람 검토 전 candidate이고 실제 id-ns는 TEST/FIXTURE 검증이다.
전체 구조 재추출·실제 SSD 명령·OCP/MFND·제품값 추정은 수행하지 않았다.

검증: 전체 회귀 **717개 통과**(299.97초). 단계 5 규칙별/등록 테스트 310개와
GUI/API/CLI 통합 1개가 포함된다. Python 컴파일·JS 문법·diff whitespace도 확인했다.
실제 DB는 스키마 v3를 유지하고 전체 사전 백업 후 r1→r2로 후보만 등록했다.
기존 검사 11개의 저장 결과가 동일하며 검사 #11의 당시 r1 재실행(#12)이 완전히 일치했다.
첨부 id-ctrl 검사 #13과 GUI #14/#15: 규칙 PASS 10 / N/A 147, 필드 PASS 7 / N/A 1 /
REVIEW 58 / UNKNOWN 3, authoritative=false. Controller 로그만 있으므로 Namespace
규칙은 N/A다. 실제 id-ns 수용 검증과 사람 승인·동작 검사는 아직 미완성이다.
GUI에서 HMPRE ≥ HMMIN 판정과 Base2.1 물리 p334 근거, candidate 범위 표를 확인했다.
추가 제품 정의·실제 SSD 명령은 없으며 다음은 6단계 OCP/MFND·제품 요구 매핑이다.

## 프로젝트 완성 계획 6단계: 추가 규격 연결 (2026-10-12)

[추가 규격 계약과 적용 범위](supplemental_requirements.md)에 따라 OCP DSSD2.6 원문 hash와
요구 ID를 보존하여 두 Bundle의 요구사항 → Capability → NVMe Field/Bit 및 직접 제약을
candidate로 등록한다. 제품 Profile에 명시적으로 연결한 정책과 적용 Context만 실행하며
실제 제품값·적용 대상·FW를 추정하지 않는다. MFND는 사용자 지시로 제외한다.
기존 엔진의 충돌·단일 명시적 override와 원래/대체 규칙·검토 근거를 trace로 연결한다.
실제 제품 바인딩과 정책 자료, 기타 OCP 요구·동작 검사는 등록 대기/미구현으로 구분한다.

검증: 전체 회귀 **743개 통과**(882.81초), 단계 6 집중 검증 26개 통과와 이후
내용 hash/과거 검토 격리·review-only 분리 영향 테스트 통과. JS 문법·Python 컴파일·
diff whitespace를 확인했다. 실제 DB schema v3 / r3, 후보 OCP 정책 2개 / 실제 Profile 0개.
사전 전체 백업 후 기존 검사 15개의 결과를 보존했고 r2 검사 #15의 재실행(#16)이 일치했다.
첨부 Controller 로그 #17/#18/#19은 기존 NVMe 판정 PASS를 유지한다. OCP는 적용 제품 자료와
Profile 바인딩이 없으므로 미선택이며 전체 OCP 적합성을 판단하지 않았다.
독립 사람 검토, 실제 제품 정책/대상/FW 정의, 나머지 OCP 규칙과 동작 검사는 대기다.
MFND는 제외하고 다음 개발 단계는 7단계 화면/보고서다.
