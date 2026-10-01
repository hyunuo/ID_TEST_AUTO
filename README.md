# ID_TEST_AUTO

SSD NVMe Identify 검증을 위한 Knowledge & Rule Engine 프로젝트입니다.

최상위 설계 문서는 [Software Design Specification](docs/ssd_nvme_validation_system_design.md)입니다. 구현 전에 이 문서를 읽고, 실제 Spec 및 내부 정책은 승인된 Knowledge 데이터로 입력합니다.

## 현재 상태

Phase 1의 Pydantic 모델, YAML 검증, Base/Delta Builder, Effective Snapshot, provenance, Spec Diff와 CLI를 구현했습니다. 테스트 입력은 `TEST/FIXTURE` 전용이며 실제 Spec·정책 데이터는 없습니다.

Product Resolver, SQLite, 실제 SSD 수집·검증은 이번 구현 범위에 포함되지 않습니다. 상세 계약과 남은 결정 사항은 [Phase 1 구현 문서](docs/phase1_implementation.md)에 기록했습니다.

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
generated/                 재생성 가능한 Snapshot, Manifest, SQLite Cache
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

- `knowledge/`의 Base, Delta, Rule, Mapping, Profile이 Source of Truth입니다.
- Generated Snapshot과 SQLite는 수정 대상이나 Source of Truth가 아닙니다.
- Answer Sheet는 비교 참고 자료이며 계산된 Expected를 대체하지 않습니다.
- 실제 NVMe/OCP/MFND field 값, offset, bit 정의와 내부 정책을 추측하지 않습니다.
- Rule 충돌과 Unknown을 임의로 해결하지 않으며 Last-write-wins를 사용하지 않습니다.
- Rule과 파생 결과의 traceability/provenance를 유지합니다.
- 모든 합성 데이터는 `example`, `dummy`, `fixture`임을 명시합니다.
- Secret과 Credential은 저장소에 기록하지 않습니다. 사내 데이터의 커밋 및 외부 반출은 승인된 정책을 따릅니다.
