# 검토 전 규칙을 실행하는 오프라인 개발 프로필

사용자의 2026-10-11 지시에 따라 candidate의 실행 규칙 전환과 제품 정책 가정을 허용한다.
실제 SSD 명령 실행은 가장 후순위로 둔다. 이번 변경은 저장 로그에 기존 Builder와
Resolver/evaluate를 연결하며 새 판정 엔진을 추가하지 않는다.

## 바로 실행

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli gui --sample ..\id-ctrl_test.txt
# 또는 CLI에서 명시적으로 실험 실행
.\.venv\Scripts\python.exe -m ssd_validator.cli actual review-log --input ..\id-ctrl_test.txt --bundle nvme-2.1-nvm-1.1 --experimental
```

GUI의 **검토 전 규칙 실행**은 기본으로 켜져 있다. 끄면 후보 근거 검토만 수행한다.
CLI에서 --experimental을 생략하면 후보 검토만 수행한다.

## 현재 실행 범위

| 규칙 | 제약 | 근거 / 가정 |
| --- | --- | --- |
| SQES_REQUIRED | 하위 nibble = 6 | 선택 Base 후보의 명시적 최소값 문장 |
| CQES_REQUIRED | 하위 nibble = 4 | 선택 Base 후보의 명시적 최소값 문장 |
| POWER_STATE_LIMIT | NPSS ≤ 31 | 후보의 0 기반 인코딩 및 최대 32 power states |
| ATOMIC_POWER_FAIL_BOUND | AWUPF ≤ AWUN | 선택 NVM 후보; 적용 가능 Context를 임시로 true 가정 |
| POLICY.FORMAT_NVM | OACS bit 1 = 1 | 임시 개발 프로필의 기능 요구 + Base 후보의 비트 매핑 |
| POLICY.FIRMWARE_DOWNLOAD | OACS bit 2 = 1 | 임시 개발 프로필의 기능 요구 + Base 후보의 비트 매핑 |

상위 queue size nibble의 recommended 값은 고정 기대값으로 만들지 않는다.
Reserved만으로 0 규칙을 생성하지 않는다. 모든 정책 가정은 LAB_ASSUMED_DEVELOPMENT_PROFILE의
provisional 데이터다. Samsung·OCP·MFND의 공식 제품 정책이나 규격으로 주장하지 않는다.
현재 로그에서 namespace/atomicity 적용 가능성은 증명할 수 없으므로 Context에 대한 가정으로
분리한다. 조건을 false로 수정하면 N/A, 제거하면 UNKNOWN이다.

## 기존 가져오기 자료 (SQLite 전환 이후)

현재 GUI와 saved-log CLI의 원본은 data/validator.sqlite3다. 아래 파일은 최초 가져오기 자료로
유지하며 파일 수정만으로 DB 원본이 바뀌지 않는다. GUI `관리` 탭의 규칙·정책 편집에서 수정하거나,
전체 원본 패키지를 내보내어 수정 후 검증하여 가져온다. [전환 계약](sqlite_transition.md)을 따른다.

- knowledge/experimental/id_ctrl/nvme-2.1-nvm-1.1.json
- knowledge/experimental/id_ctrl/nvme-2.0e-nvm-1.0e.json
- 각 Bundle 하위의 base.yaml, catalog.yaml

JSON의 rules, capabilities, context, assumptions를 수정한다. 개별 Bundle 하위 YAML은
선택한 6개 필드만 담은 Builder 입력 projection이다. 전체 규격 Snapshot이나 완전한 구조
추출로 간주하지 않는다. 이 입력을 빌드할 때는 해당 Bundle 폴더를 --source로 선택한다.
field_evidence에 실제 후보 정의·원문 문장·문서·페이지가 보존되어 있다.
candidate_knowledge_hash는 참조한 후보 묶음의 hash이며 후보가 바뀌면 실행을 중단하고
참조를 재검토하도록 한다. config와 YAML의 입력 hash가 결과에 남는다.

## 실행 계약

기본 Resolver 계약은 strict다. experimental 모드에서만 candidate/provisional을
실행 대상으로 허용한다. 원래 provenance 상태는 그대로 유지하며 confirmed reviewer나
검토 날짜를 만들어 넣지 않는다. 실제 로그를 TEST/FIXTURE로 바꾸지도 않는다.

결과는 experimental_validation_report, authoritative=false이며 profile.execution_mode는
experimental이다. PASS/FAIL은 등록한 가정과 해석에 대한 판정이며 승인 완료를 뜻하지 않는다.
조건·입력 누락은 UNKNOWN, 거짓은 N/A, 타입/중복 오류는 ERROR,
불가능한 literal 교집합은 CONFLICT다. candidate/provisional 충돌도 동일하게 검사한다.
MAY/SHOULD/동작 관찰 문장은 자동 mandatory로 바꾸지 않는다. confirmed 근거가 필요한
override 계약은 유지하며 암묵적 우선순위로 실험 규칙을 덮어쓰지 않는다.

GUI의 단일 필드 표에 실제 로그의 Expected 제약과 규칙 판정을 함께 보여준다. 각 규칙을 누르면 Expected 제약,
Actual/Context 관측값, 적용 여부, 원문 근거와 가정을 확인한다. 전체 필드 지식 검토 상태와
실행된 6개 규칙의 판정을 구분한다. 사용하지 않은 필드는 적합성이 검증된 것이 아니다.

GUI에서 Atomic Context와 정책 적용 범위를 선택할 수 있다. Source 기본값과 현재 선택은
결과에 함께 보존한다. 다음 우선순위는 저장 id-ns 연결과 규칙 확장이다.
SQLite 원본 관리와 검사 이력은 구현했다. 실제 SSD 명령, Excel, Product 자동 선택은 후속이다.
