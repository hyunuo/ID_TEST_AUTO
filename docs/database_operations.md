# 원본 DB 보호와 마이그레이션

현재 지원 스키마: v3. 원본 DB는 `data/validator.sqlite3`다.
이 파일은 캐시나 generated 산출물이 아니며 지식 수정과 검사 이력을 포함한다.

## 전체 백업

GUI의 `DB 백업·복원` → `전체 DB 백업 저장`을 사용한다.
서버가 실행 중이어도 SQLite backup API로 일관된 전체 사본을 만든다.
원본 지식, 모든 리비전, 규칙 인덱스, 입력 로그 바이트, 검사 옵션과 결과를 포함한다.
파일 SHA-256과 크기를 표시한다. SQLite 사본은 파일 헤더가 달라질 수 있으므로 원본 파일과
사본의 바이트 해시가 같아야 한다고 판단하지 않는다. 자료 내용과 무결성을 검증한다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli database status
.\.venv\Scripts\python.exe -m ssd_validator.cli database backup --output data\backups\manual-20261012.sqlite3
```

CLI는 기존 출력 파일을 덮어쓰지 않는다. 이름이 있으면 새 이름을 지정한다.
`--database <경로>`로 다른 원본 DB를 지정할 수 있다.
원본 JSON 내보내기는 지식 교환용이며 검사 이력을 포함하지 않는다.
data/ 안의 DB 및 백업 파일은 Git에서 제외한다.

## 복원

같은 DB를 사용하는 다른 서버를 종료하고 하나의 서버에서 수행한다.
GUI에서 현재 상태를 불러오고 백업 파일을 선택한 뒤 복원을 실행한다.
현재 GUI의 DB 백업 업로드 제한은 64 MiB다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli database status
.\.venv\Scripts\python.exe -m ssd_validator.cli database restore --input data\backups\manual-20261012.sqlite3 --expected-revision 1
```

expected-revision에는 복원 직전에 status에서 확인한 현재 head 값을 넣는다.

처리 순서:

1. 임시 파일에서 SQLite integrity/foreign key 및 지원 스키마를 확인한다.
2. 원본 문서 해시와 입력 로그 해시를 확인한다.
3. 모든 원본 리비전을 기존 모델·Builder·Resolver로 검증한다.
4. 현재 head가 요청한 head와 같아야 한다. 다르면 복원을 거절한다.
5. 현재 DB를 data/backups/pre-restore-<ID>.sqlite3로 자동 백업한다.
6. 복원 자료를 staging DB에서 필요 시 마이그레이션하고 원본을 교체한다.
7. 복원 자료의 과거 리비전/검사 ID는 유지한다. 현재와 복원 자료의 최대 head보다 큰
   새 head를 만들어 복원 사실을 기록한다. 복원 전 화면의 편집을 거절하기 위한 조치다.

검증 실패와 staging 마이그레이션 실패는 현재 DB를 바꾸지 않는다.
같은 프로세스에서 DB 복원과 검사 저장은 직렬화한다. 다른 서버 프로세스의 교체를 조율하는
분산 잠금은 구현하지 않았다. 복원 전 다른 서버를 종료하는 운영 조건이 필요하다.
복원 전 상태가 필요하면 자동 백업 파일을 다시 선택해 같은 절차로 복원한다.

## v1 → v2 → v3 마이그레이션

v2는 `database_migration` 감사 테이블을 추가한다. 규격/정책/규칙/Context 값은 변경하지 않는다.

- v1 원본을 처음 열면 무결성과 필수 테이블을 확인한다.
- 변경 전에 data/backups/pre-migration-v1-<ID>.sqlite3에 전체 백업한다.
- 트랜잭션에서 감사 테이블 생성, 스키마 버전 변경, 백업 경로와 migration 이력 기록을 수행한다.
- SQL 오류는 rollback한다. 기존 지식 리비전과 입력·검사 결과는 유지한다.
- 처음 만드는 DB는 바로 v3로 생성한다.
- v1/v2 백업 복원은 staging에서 순서대로 v3로 마이그레이션한 뒤 적용한다.
- 모르는 버전, 다른 프로그램의 DB, 필수 테이블이 없는 DB는 자동 수정하지 않는다.

향후 버전은 명시적인 순차 migration과 백업·실패·이력 보존 테스트를 추가해야 한다.
버전 번호만 바꾸거나 모든 기존 DB를 현재 형식으로 추정해서 열면 안 된다.

v2→v3는 사전 전체 백업 후 entity_index를 추가하고 기존 모든 리비전의 원본에서 검색 인덱스를 채운다.
실행 규칙과 검사 이력은 바꾸지 않는다. 실패는 rollback한다.
[지식 관리 계약](knowledge_management.md)을 따른다.

## 실패 시 점검

- Unsupported schema: 지원 버전의 도구와 백업을 확인한다. schema_version을 직접 바꾸지 않는다.
- REVISION_CONFLICT: 현재 상태를 다시 조회하고 수정 또는 복원을 다시 검토한다.
- Hash/integrity 오류: 손상된 백업으로 원본을 덮어쓰지 않는다. 다른 검증된 백업을 사용한다.
- Windows 파일 사용 중 오류: 같은 DB를 사용하는 다른 서버/DB 편집기를 종료한다.
