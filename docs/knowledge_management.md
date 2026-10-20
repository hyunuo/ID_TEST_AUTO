# 지식 관리 GUI — 완성 계획 2단계

SQLite 원본 리비전에서 Bundle·문서·실행 필드·비트·배열·규칙·Capability 매핑을 검색/관리한다.
기존 Builder, Source 검증, normalize_json/layout_from_profile, resolve/evaluate를 재사용한다.

## 기본 사용

1. `지식 관리`에서 종류와 Bundle을 선택하고 ID·이름·근거로 검색한다.
2. 행을 선택해 편집하거나 `추가`를 선택한다.
3. 필드에는 응답 명령, offset/요소 길이, 타입/Endian, CNS/CSI, 원문 위치를 입력한다.
   비트 정의와 배열 count/stride를 별도 폼으로 관리한다. Reserved는 zero 제약과 별도다.
4. Capability에는 대상 필드·비트·배열 인덱스와 지원/미지원 값을 입력한다.
5. 규칙은 `관리` 탭의 `규칙·정책 편집` 폼에서 편집한다. Context/Actual의 EQ/비트 조건과
   필드 간 비교는 폼으로 입력한다. AND/OR/NOT 등 복잡한 식만 고급 조건을 사용한다.
6. 변경 사유를 입력하고 `검증·변경 미리보기`를 선택한다.
7. 변경한 항목의 이전/이후를 확인하고 저장한다. 저장은 새 리비전을 만든다.

Bundle 선택 목록은 현재 DB 등록 자료에서 읽는다. 도구 버전/Actual VER로 규격을 자동 선택하지 않는다.
새 Bundle은 등록된 동일 문서/structure 조합을 사용자가 명시적으로 복제한다.
규격 쌍이 다른 자료에 기존 필드를 자동 복사하지 않는다. 새 규격 버전은 근거와 추출 자료를
확보한 뒤 검증된 전체 원본 패키지로 가져온다.

## 문서와 참조

원문 PDF 등록의 문서 ID·component·revision·SHA256·페이지·상속은 추출에 고정된 식별 정보다.
파일 이름 수정과 새 일반 출처 등록은 GUI로 가능하다. 고정 식별 정보 변경은 해당 원문의
추출 데이터가 함께 바뀌어야 하므로 일반 폼에서 자동 적용하지 않는다.
일반 규격/정책 출처는 고유 문서 ID와 버전으로 등록한다.

저장 전 검증:

- 모델 타입, 중복 ID, Source 문서/버전과 원문 페이지.
- 필드/비트/배열 경계, query/structure 바인딩, response 크기와 겹침.
- 조건/비교 대상, Capability와 규칙 참조, 지원하지 않는 표현.
- 해당 항목 삭제가 다른 규칙/문서 참조를 끊는지 확인.
- 기존 원문 hash 연결 및 선택한 Bundle의 Builder/Resolver 오류.

규칙 자체의 충돌은 자동 제거하지 않는다. 실행 시 CONFLICT와 양쪽 근거를 표시한다.

## 검토 기록

검토자·검토일·근거를 모두 직접 입력한다. 기록은 종류/Bundle/ID/내용 SHA256에 연결한다.
수정 후 내용이 달라지면 이전 검토가 현재 내용의 승인으로 표시되지 않는다. 기록 자체는 보존한다.
규칙/Capability의 confirmed 변경은 provenance의 검토자/날짜와 검토 기록이 일치해야 한다.
확인된 비-fixture 근거도 experimental에서는 실행할 수 있으나 authoritative=false를 유지한다.
기존 strict TEST/FIXTURE 경계는 유지한다.

필드 검토 기록은 Builder 전체 Source의 candidate 상태를 자동 confirmed로 바꾸지 않는다.
개별 검토 기록과 실행 provenance 상태는 분리한다. AI가 검토자나 승인 날짜를 생성하지 않는다.

## 미리보기·동시 편집·되돌리기

미리보기는 DB에 쓰지 않는다. 저장 시 같은 expected_revision과 preview_hash로 다시 검증한다.
다른 수정/복원이 있었다면 REVISION_CONFLICT, 폼 내용이 달라졌다면 PREVIEW_CHANGED로 거절한다.
여러 항목을 각각 저장할 때는 새 리비전의 목록을 다시 불러온다.

`리비전 되돌리기`에서 과거 리비전과 사유를 선택하고 미리보기 후 저장한다.
과거 데이터를 새 head로 복사하며 리비전/검사 이력을 삭제하지 않는다.
당시 검사 결과 조회와 동일 리비전 재실행은 기존 경로를 유지한다.

## 저장 구조와 migration

- 스키마 v3: revision별 `entity_index`를 추가한다. 원본 내용에서 만드는 검색 인덱스다.
- v2→v3는 전체 사전 백업 후 트랜잭션으로 인덱스를 생성/채운다.
- v1 백업은 v1→v2→v3 순서로 이동한다. 원본 문서/리비전/검사 입력과 결과는 변경하지 않는다.
- Source 검증, 원본 저장, rule_index/entity_index 갱신은 한 revision/트랜잭션에서 처리한다.
- query/배열 바인딩, 추가 출처, 내용별 검토 기록은 DB의 `knowledge/management.json` 논리 원본에 보존한다.
  기존 파일이 없는 과거 리비전은 기존 기본 바인딩을 그대로 사용한다.
- 인덱스와 원본을 각각 편집하지 않는다. 생성 Snapshot을 편집하지 않는다.

## 현재 범위

폼은 Builder/Resolver에서 사용하는 실행 필드와 규칙 레지스트리를 관리한다.
전체 PDF 구조 후보와 nested template는 원본 참고/전체 패키지 경로로 유지한다.
추가 query 필드를 등록할 수 있으나 복수 Identify 로그·Namespace 입력 통합은 3단계다.
필드·배열 등록 성공이 해당 응답을 실제 로그에서 수집/검증했다는 뜻은 아니다.
실제 SSD 명령, 제품 Profile/FW 선택, OCP/MFND 요구사항 추출은 이번 단계에서 추가하지 않았다.

## 프로젝트 완성 계획 6단계: 추가 규격 연결 (2026-10-12)

[추가 규격 계약과 적용 범위](supplemental_requirements.md)에 따라 OCP DSSD2.6 원문 hash와
요구 ID를 보존하여 두 Bundle의 요구사항 → Capability → NVMe Field/Bit 및 직접 제약을
candidate로 등록한다. 제품 Profile에 명시적으로 연결한 정책과 적용 Context만 실행하며
실제 제품값·적용 대상·FW를 추정하지 않는다. MFND는 사용자 지시로 제외한다.
기존 엔진의 충돌·단일 명시적 override와 원래/대체 규칙·검토 근거를 trace로 연결한다.
실제 제품 바인딩과 정책 자료, 기타 OCP 요구·동작 검사는 등록 대기/미구현으로 구분한다.
