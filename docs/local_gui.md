# 로그 검증 GUI 사용 안내

## 실행

프로젝트 루트에서 실행합니다. 실제 SSD 명령은 실행하지 않습니다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli gui --sample ..\id-ctrl_test.txt
```

표시된 로컬 URL을 열고 첨부 로그 열기를 누르거나 txt/log를 선택합니다.
다른 프로그램이 해당 포트를 사용하면 --port 8767처럼 다른 포트를 지정합니다.
종료는 실행 터미널의 Ctrl+C입니다. 외부 서버로 로그를 보내지 않습니다.

## 하나의 사용 흐름

4단계의 `제품 Profile 선택과 Context`와 `제품 관리` 패널을 추가했다.
Profile을 등록한 후 명시적으로 선택하면 바인딩 Bundle·등록 정책·Context를 사용한다.
`입력에서 후보 제안`은 선택을 바꾸지 않는다. 제품 자료가 없으면 기본 목록은 비어 있다.
[제품 설정과 FW 비교 계약](product_profiles.md)을 따른다.

복수 응답은 상단 입력 묶음에서 id-ctrl/id-ns 파일을 함께 추가한다. 명령·형식·DUT·세션·
Namespace와 확인된 query/도구 정보를 입력한 뒤 `입력 묶음 검사`를 누른다.
각 Namespace scope의 판정과 원문·메타데이터를 같은 화면에서 조회한다.
[복수 응답 사용 계약](saved_capture_inspections.md)을 따른다. 아래 단일 로그 자동 검사도 유지한다.

1. 저장된 단일 id-ctrl 로그를 선택합니다.
2. 제품 적용 규격 Bundle, 정책, Atomic 관계 적용 Context를 선택합니다.
3. 자동으로 공통 Actual 정규화 → 기존 Builder → Resolver/evaluate를 실행합니다.
4. 한 표에서 필드별 Actual·Expected 제약·판정을 확인합니다.
5. 필드를 누르면 적용 규칙, 원문 근거, 정규화 상태, 입력 관측값과 전체 trace를 확인합니다.
6. 결과 JSON 저장으로 현재 선택과 전체 보고서를 저장합니다.

정책은 임시 개발 정책(Format NVM·Firmware Download 지원 요구)과 규격 규칙만 적용 중
선택합니다. Atomic 적용은 가정/미적용/미확인으로 선택할 수 있습니다.
미확인은 Context 사실을 제거하여 UNKNOWN으로 평가하고 미적용은 N/A로 처리합니다.
선택을 바꾸면 동일한 로그로 재검사합니다. GUI 선택은 현재 실행에만 적용하며 Source를
수정하지 않습니다. GUI Context 선택은 Source 기본값보다 우선하며 결과에 기록됩니다.

개발용 TEST/FIXTURE 버튼은 기본 화면에서 제거했습니다. 기존 CLI의 knowledge build,
pilot run, actual normalize, spec bundle-diff와 application 서비스는 그대로 유지합니다.
별도의 Builder/Resolver 버튼을 누를 필요가 없습니다.

## 실제 재사용 경로

텍스트 adapter → 공통 ActualFact → Source에서 Builder가 만든 FieldRegistration →
layout_from_profile → 기존 normalize_json의 타입/폭/누락 검사 → 기존 resolve/evaluate입니다.
텍스트를 내부 객체로 변환할 뿐 CLI JSON 응답이나 raw 바이트를 만들어내지 않습니다.
보고서의 source_format=text와 source hash는 원본 로그를 가리킵니다.

매핑된 모든 관측값은 actual_data.actual_facts에 보존하고 현재 규칙의 입력은
actual_data.validation_facts로 선택합니다. 정규화 중 오류가 난 값을 Resolver에 넣지
않으며 필드에 ERROR를 표시합니다. 원문·Power State·매핑되지 않은 필드도 보존합니다.

현재 규칙은 SQES/CQES 최소값, NPSS 범위, AWUPF/AWUN 관계와 두 임시 기능 정책입니다.
첨부 로그는 6개 규칙 PASS, 직접 대상 5개 필드 PASS, 61개 필드 REVIEW, 3개 UNKNOWN입니다.
AWUN은 관계 검사의 비교값으로 사용하지만 AWUN 자체의 독립 요구사항이 없어 REVIEW입니다.
실행 규칙이 없는 필드는 PASS로 만들지 않습니다. 필요한 규칙 입력이 로그에 없으면
누락 필드 행과 Expected 제약을 표시하고 UNKNOWN으로 남깁니다.

검토 전 규칙 실행을 끄면 후보 근거 검토만 수행합니다. 실험 실행의 provenance는
candidate/provisional로 유지하고 authoritative=false로 표시합니다. GUI의 규칙 전체
PASS는 SSD 전체 적합성을 의미하지 않습니다. 도구 버전은 UNKNOWN으로 보존하며 DUT VER로
제품 Bundle을 자동 변경하지 않습니다.

## Source 수정과 기존 CLI

GUI와 saved-log CLI는 `data/validator.sqlite3`를 원본으로 사용합니다. 첫 실행에 기존
knowledge/ 및 candidates/ 데이터를 가져오고, 이후 파일 수정은 DB에 자동 반영하지 않습니다.

`규칙·정책 관리`를 펼쳐 관리 Bundle과 규칙을 선택하세요. 제약·조건·출처를 수정하고
변경 사유를 입력해 저장하면 기존 Builder/Resolver 검증 후 새 리비전으로 저장합니다.
규칙 추가·삭제도 같은 경로를 사용합니다. confirmed 승격은 일반 편집 기능에 포함하지 않습니다.
단순 조건과 필드 관계는 폼으로 입력하며 AND/OR/NOT 등 복잡한 조건만 고급 입력을 사용합니다.
`지식 관리`에서 Bundle·문서·실행 필드/비트/배열·Capability 매핑을 관리합니다.
변경은 미리보기 후 새 리비전으로 저장합니다. 검토 근거와 되돌리기 계약은
[지식 관리 안내](knowledge_management.md)를 따릅니다. 기본 Context 전체 편집은 패키지 경로입니다.

`검사 이력`에서 과거 결과를 열거나 당시 리비전·Context·정책·원본 로그로 재실행할 수 있습니다.
원본 전체 내보내기는 지식 자료만 포함합니다. 검사 이력까지 보존하려면 `DB 백업·복원`의
전체 백업을 사용하세요. 서버 실행 중에도 일관된 사본을 만들며 복원은 검증과 자동 사전 백업을 수행합니다.
복원 전 같은 DB를 사용하는 다른 서버를 종료하세요. DB 파일은 삭제 가능한 캐시가 아닙니다.
현재 스키마 v3와 CLI 백업·복원 절차는 [DB 운영 안내](database_operations.md)에 기록했습니다.
상세 계약은 [SQLite 전환 계획](sqlite_transition.md)을 따릅니다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli actual review-log --input ..\id-ctrl_test.txt --bundle nvme-2.1-nvm-1.1 --experimental
```

generated/는 직접 편집하지 않습니다. PDF hash 재검증과 Bundle 비교는 기존 CLI로 수행합니다.
GUI 실행 시 원본 PDF를 재검증했다고 주장하지 않으며 manifest의 documents_verified=false를
보존합니다. 실제 SSD 수집, Excel, 자동 Product 선택은 후순위입니다.

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
