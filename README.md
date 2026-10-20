# ID_TEST_AUTO

SSD NVMe Identify 검증을 위한 Knowledge & Rule Engine 프로젝트입니다.

최상위 설계 문서는 [Software Design Specification](docs/ssd_nvme_validation_system_design.md)입니다. 구현 전에 이 문서를 읽고, 실제 Spec 및 내부 정책은 승인된 Knowledge 데이터로 입력합니다.

## 현재 상태

구현 사실과 미완성은 [현재 상태](docs/current_status.md), 원본 보호와 스키마 v3 마이그레이션은
[DB 운영 안내](docs/database_operations.md)를 따릅니다. GUI에서 지식뿐 아니라 검사 이력을 포함한
전체 DB 백업·복원을 제공합니다. 기존 규칙과 첨부 로그 판정은 유지합니다.

저장 id-ctrl/id-ns 텍스트·raw·JSON을 [복수 입력 묶음](docs/saved_capture_inspections.md)으로
검사할 수 있습니다. DUT·수집 세션·Namespace별로 분리하며 확인되지 않은 query 정보는
UNKNOWN입니다. Namespace 요구사항의 candidate 확대는 5단계에서 TEST/FIXTURE로 검증했습니다. 실제 id-ns 로그와 SSD 명령 실행은 후속 범위입니다.

[제품 Profile·정책·Context 관리](docs/product_profiles.md), 명시적 선택과 후보 제안,
등록된 FW 비교를 추가했습니다. 관찰값·사용자 입력·가정·정책 요구와 검사 당시 설정을 보존합니다.
실제 제품 정의는 아직 등록하지 않았으며 미확인 선택 조건은 UNKNOWN으로 남습니다.

5단계에서는 원문 네 PDF를 대조하여 용량·THINP·LBAF·atomic·큐·기능 일관성 candidate를
확대했습니다. [실행 가능 / 추가 정보 / 동작 검사 / 미구현 표](docs/nvme_requirement_coverage.md)와
GUI의 요구사항 범위 패널에서 확인할 수 있습니다. SQLite에 명시적으로 등록하며 파일 변경으로
기존 DB를 덮어쓰지 않습니다. 사람 검토 전 규칙의 PASS는 전체 적합성 승인이 아닙니다.

6단계에서는 확보된 [OCP2.6 추가 규격 subset](docs/supplemental_requirements.md)을
candidate 정책/Capability로 등록했습니다. 실제 제품 Profile에 명시적으로 연결한 경우만
실행하며 적용 범위·버전 누락은 UNKNOWN입니다. 충돌과 원래/대체 override 근거를 보존합니다.
실제 제품 정책 자료는 미확보, MFND는 제외이며 전체 OCP 적합성 완료를 뜻하지 않습니다.

### 먼저 사용하기: 로컬 GUI

검토 전 규칙의 실험 실행을 추가했습니다. 첨부 DUT 로그에 SQES/CQES·NPSS·AWUPF/AWUN
규칙과 수정 가능한 임시 개발 정책을 적용하고, 기존 Resolver의 Expected/판정/trace를 표시합니다.
공식 승인과 구분되는 `authoritative=false` 결과입니다. [규칙과 가정 수정 안내](docs/experimental_rules.md)를 참고하세요.

기존 Builder·Resolver·provenance·정규화·Bundle 비교를 재사용하는 GUI를 추가했습니다.
프로젝트 루트에서 다음 명령을 실행하고 표시된 로컬 주소를 여세요.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli gui --sample ..\id-ctrl_test.txt
```

로그 파일 선택 → 규격 Bundle 선택 → 필드 클릭으로 Actual과 후보 근거를 확인하고
JSON으로 저장할 수 있습니다. 로그를 넣으면 정규화·Builder·Resolver를 자동으로 호출하고
한 표에서 Actual·Expected·판정을 보여줍니다. Context와 정책을 선택하면 동일 로그를 재검사합니다.
개발용 TEST/FIXTURE 버튼은 기본 화면에서 제거했고 기존 CLI 기능은 유지했습니다.
실제 로그의 후보 지식 REVIEW/UNKNOWN, 검토 전 실험 판정, 합성 데이터의 판정을 구분합니다.
상세 범위는 [GUI 사용 안내](docs/local_gui.md)를 참고하세요.

`관리` 탭의 `규칙·정책 편집`에서 Bundle별 규칙을 추가·수정·삭제하고 변경 사유와 새 리비전을 저장합니다.
`검사 이력`에서 저장 결과 조회와 당시 입력·조건·규칙으로 재실행할 수 있습니다.
첫 실행에 기존 자료를 `data/validator.sqlite3`로 가져옵니다. 이후 이 DB가 원본이며
파일 변경을 자동 덮어쓰지 않습니다. 원본 내보내기와 DB 백업 방법은
[SQLite 전환 계획](docs/sqlite_transition.md)에 기록했습니다.

다음 개발 순서와 단계별 실행 프롬프트는 [프로젝트 완성 계획](docs/project_completion_plan.md)을 따릅니다.

2단계 지식 관리: Bundle·문서·실행 필드·비트·배열·Capability를 GUI 폼으로 검색/관리합니다.
단순 조건·관계식 입력, 변경 미리보기, 검토 근거와 리비전 되돌리기를 제공합니다.
스키마 v3 migration은 사전 백업 후 검색 인덱스만 추가하고 원본/과거 검사를 보존합니다.
[지식 관리 사용 안내](docs/knowledge_management.md)를 참고하세요.

Phase 1의 Pydantic 모델, YAML 검증, Base/Delta Builder, Effective Snapshot, provenance, Spec Diff와 CLI를 구현했습니다. Core 회귀 테스트는 `TEST/FIXTURE`를 사용하며, 실제 규격 후보와 임시 개발 정책은 experimental 경로에 등록했습니다.

조건부·관계형 규칙 실행 파일럿을 추가했습니다. TEST/FIXTURE에서 Expected Profile,
규칙별 판정과 provenance trace를 생성합니다. Product Profile 자동 선택, 실제 SSD
명령 실행과 Excel은 후속 범위입니다. SQLite 원본 저장소와 GUI 관리·검사 이력을 추가했습니다.
상세 계약은 [Phase 1 구현 문서](docs/phase1_implementation.md)에 기록했습니다.

현재 개발의 우선순위는 전체 구조 재추출보다 **규격 요구사항·필드 간 관계·Capability 매핑**입니다.
명령 실행과 기본 구조 해석은 nvme-cli/libnvme를 재사용하고, 필요한 필드의 규격별 의미를 확인합니다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli pilot run --source tests/fixtures/rule_pilot/knowledge --input tests/fixtures/rule_pilot/input.json
```

이 명령의 PASS/FAIL은 합성 fixture 결과입니다. 실제 NVMe/OCP/MFND 승인 지식이 아닙니다.
[규칙 실행 파일럿](docs/rule_execution_pilot.md)에 입력·상태·제약과 후속 순서를 정리했습니다.

저장한 Identify raw/JSON을 제품 Bundle 기준으로 해석하는 오프라인 정규화도 추가했습니다.
도구 버전과 장치의 보고 버전은 수집 이력으로 유지하며, 제품의 적용 규격을 바꾸지 않습니다.
raw 미매핑 영역·추가 JSON 필드는 보존하고 누락은 UNKNOWN으로 처리합니다.
실행 방법과 fixture Resolver 연결은 [Identify 정규화](docs/actual_normalization.md)를 참고하세요.

NVMe Base 2.0e + NVM Command Set 1.0e, Base 2.1 + NVM Command Set 1.1의
Identify 후보 지식 구축 경로를 추가했습니다. `candidates/nvme/`에는 CNS 00h/01h/05h/06h/08h의
구조 후보와 원문 요구사항 검토 목록이 있습니다. 모두 **candidate**이며 승인된 실제 Knowledge가 아닙니다.
전체 바이트 영역과 문서 검색 범위를 기록하지만 비트 의미·조건·참조의 완전한 검토는 아직 완료되지 않았습니다.
[후보 빌드·검토 절차](docs/identify_knowledge_workflow.md)를 참고하세요.

```powershell
# 원문은 spec/ 폴더에 둡니다(spec/manifest.json 참고).
ssd-validator knowledge build --candidate --source candidates/nvme --documents-root spec --output generated/candidate
ssd-validator spec bundle-diff --source candidates/nvme --from nvme-2.0e-nvm-1.0e --to nvme-2.1-nvm-1.1
```

후보 빌드는 원문 SHA-256을 확인하고 검토 보고서·문서 조합별 Snapshot·Diff를 생성합니다.
기존 `knowledge build`는 `--candidate` 없이 후보 JSON을 읽지 않습니다.
PDF 추출 도구를 다시 실행할 때만 별도 `requirements-extraction.lock` 환경이 필요합니다.

## 구조

```text
docs/                      최상위 SDS
config/                    비밀값을 포함하지 않는 애플리케이션 설정
knowledge/                 사람이 관리하는 Source Knowledge
  specs/{nvme,ocp,mfnd}/    승인된 Schema 및 Requirement Base/Delta
  features/                Feature 정의
  mappings/                Field/Feature 및 Capability/Field Mapping
  products/                Product Profile, Policy, Exception
  policies/{common,product}/
  answer_sheet/imported/   비교 참고 자료
generated/                 재생성 가능한 Snapshot, Manifest
data/validator.sqlite3     로컬 원본 DB와 검사 이력 (백업 필요, Git 제외)
src/ssd_validator/
  models/                  Pydantic Domain Model
  knowledge/               Source 로딩 및 검증
  spec_builder/            Base/Delta 및 버전별 Snapshot 생성
  resolver/                Profile 선택, 조건 평가, 제약 결합 및 Trace
  analyzer/                Spec Diff
  storage/                 직렬화, 산출물 및 Cache 저장
  application/             Use case 조합
tests/{unit,integration,fixtures,golden}/
results/                   검증 실행 산출물
```

`collector`, `normalizer`, `validator`, `reporter`, `policy_search`는 해당 구현 단계에서 추가합니다.

## 개발 환경

Python 3.12 이상을 사용합니다. 아래 명령은 프로젝트 루트에서 실행합니다.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps -e .
```

전체 테스트:

```bash
python -m pytest -q
```

Windows에서는 가상환경을 `.venv\Scripts\Activate.ps1`로 활성화합니다.
Source YAML과 Golden JSON은 `.gitattributes`에 따라 LF로 유지합니다.
심볼릭 링크 권한이 없는 로컬 Windows에서는 관련 테스트 2개가 사유와 함께 건너뛰어집니다.
CI는 Linux/Windows 모두 `SSD_REQUIRE_SYMLINK_TESTS=1`로 실제 링크 검증을 요구합니다.

Builder 0.2.0은 변경된 Rule의 승인 근거 재사용, LOOKUP 키 손실, 출력 경로 충돌을 방지합니다.
스냅샷 내부 컬렉션은 변경할 수 없으며 Target 정체성, 폐기된 bit, production/fixture 근거 경계도 검증합니다.

fixture Knowledge 빌드 및 버전 비교:

```bash
ssd-validator knowledge build --source tests/fixtures/knowledge --output generated
ssd-validator spec diff --source tests/fixtures/knowledge --family test --from fixture-v1 --to fixture-v4
```

특정 Spec을 선택하면 필요한 parent와 schema dependency도 생성합니다.

```bash
ssd-validator knowledge build --source tests/fixtures/knowledge --output generated --spec ocp --version fixture-v2
```

기본 Source 경로인 `knowledge/`에는 승인된 실제 데이터가 아직 없습니다. 빈 Source 빌드는 성공으로 처리하지 않습니다.

Golden baseline을 의도적으로 재생성할 때만 아래 명령을 실행하고 변경 내용을 검토합니다. 테스트는 Golden을 자동 갱신하지 않습니다.

```bash
python tests/regenerate_fixture_goldens.py --write
```

## 데이터 원칙

- GUI와 saved-log CLI의 원본은 `data/validator.sqlite3`의 불변 리비전입니다.
- `knowledge/`, `candidates/`는 최초 가져오기 자료입니다. DB 생성 후 파일 수정은 자동 반영하지 않습니다.
- Generated Snapshot은 원본이 아니며 직접 수정하지 않습니다. TEST/FIXTURE CLI는 파일 입력을 유지합니다.
- Answer Sheet는 비교 참고 자료이며 계산된 Expected를 대체하지 않습니다.
- 실제 NVMe/OCP/MFND field 값, offset, bit 정의와 내부 정책을 추측하지 않습니다.
- Rule 충돌과 Unknown을 임의로 해결하지 않으며 Last-write-wins를 사용하지 않습니다.
- Rule과 파생 결과의 traceability/provenance를 유지합니다.
- 모든 합성 데이터는 `example`, `dummy`, `fixture`임을 명시합니다.
- Secret과 Credential은 저장소에 기록하지 않습니다. 사내 데이터의 커밋 및 외부 반출은 승인된 정책을 따릅니다.
