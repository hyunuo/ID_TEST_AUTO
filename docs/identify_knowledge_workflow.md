# NVMe Identify 후보 지식 구축과 검토

이 문서는 NVMe 원문에서 `id-ctrl`·`id-ns` 구조와 관련 요구사항을 추출하고 검토하는
절차를 설명한다. 설계 기준은 [SDS 72절](ssd_nvme_validation_system_design.md#72-nvme-복수-문서와-identify-후보-지식-구축)이다.
후보 빌드는 검토 자료를 만들며, 승인된 제품 Expected나 SSD 판정을 만들지 않는다.

## 입력과 실행

다음 원문 네 개를 하나의 로컬 폴더에 둔다. 원본은 저장소에 복사하지 않는다.

- `NVM-Express-Base-Specification-2.0e-2024.07.29-Ratified.pdf`
- `NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf`
- `NVM-Express-NVM-Command-Set-Specification-1.0e-2024.07.29-Ratified.pdf`
- `NVM-Express-NVM-Command-Set-Specification-Revision-1.1-2024.08.05-Ratified.pdf`

PowerShell에서 `$specDocuments`를 실제 원문 폴더로 바꾸어 실행한다.

```powershell
$specDocuments = "D:\specifications"
ssd-validator knowledge build --candidate --source candidates/nvme --documents-root $specDocuments --output generated/candidate
ssd-validator spec bundle-diff --source candidates/nvme --from nvme-2.0e-nvm-1.0e --to nvme-2.1-nvm-1.1
```

Bundle은 `2.0e + 1.0e`, `2.1 + 1.1` 두 조합을 명시한다. 등록된 파일의 SHA-256이
다르면 같은 이름의 원문이라고 가정하지 말고 실제 revision과 등록 내용을 확인한다.
개인 PC의 절대 경로는 커밋하지 않는다.

추출 자체를 재실행할 때는 별도 Python 환경에 `requirements-extraction.lock`을 설치한다.
기존 후보의 검증·빌드에는 PDF 파서 의존성이 필요하지 않다.

```powershell
python -m pip install -r requirements-extraction.lock
python tools/extract_identify_structures.py --source-dir $specDocuments
python tools/extract_identify_requirements.py --pdf-dir $specDocuments
```

입력 PDF 해시를 등록된 원문과 대조한 후에만 고정된 페이지 범위를 추출한다.
추출물의 `document_hashes`도 catalog와 일치해야 빌드할 수 있다.
추출기를 다시 실행하면 후보 입력이 교체되므로 사람의 수정이 있는 경우 Git Diff를 검토한다.

## 원본과 산출물

| 데이터 | 관리 방법 |
| --- | --- |
| `catalog.json` | 원문 파일명·revision·해시와 Bundle의 문서 선택을 관리한다. |
| `structures.json` | 응답별 구조와 공통 필드 ID, 하위 구조·비트, 출처·미완료 범위를 관리한다. |
| `requirements.json` | 필드명 참조·요구사항·조건·의존 관계·미해결 항목을 관리한다. 빌드에서 필드 ID 후보에 연결하며 미일치·모호성을 보존한다. |
| `generated/candidate/` | 빌드 결과만 저장한다. 수정 사항은 후보 입력에 반영하고 다시 빌드한다. |

세 입력 파일은 `candidates/nvme/` 아래에 있다. 후보 입력은 AI가 작성한 검토 대상이며,
`knowledge/`의 확정 지식을 대체하지 않는다. 원문은 사실 확인의 근거이고, 후보 JSON은
원문의 기계 판독 가능한 해석 초안이다. Snapshot과 Diff는 입력에서 생성한 자료다.

## 요구사항 중심의 작업 계약

**요구사항 분석 담당**이 주 작업을 수행한다. 규격 문장을 조건·제약·예외·의존성으로
분해하고 필요한 필드와 Capability 매핑을 식별한다. 전체 구조 추출 완료를 기다리지 않는다.
의무·권고·허용·설명과 명령 실행 동작을 구분하고 다른 절의 근거도 추적한다.

**구조·매핑 담당**은 nvme-cli/libnvme의 기존 정의와 출력 형식을 재사용하는 방향으로
필요한 필드 ID·CNS/CSI·비트·배열 인덱스를 확인한다. 실제 연동에서는 릴리스/커밋을
고정한다. 기존 structures.json은 보조 참조 자료이며 모든 필드의 재추출·승인을
규칙 실행의 선행 조건으로 요구하지 않는다. 규격별 의미 차이나 표의 불확실한
열 관계는 원문을 렌더링해 확인하고 미해결 사항을 요구사항 담당에게 전달한다.

통합 담당은 양쪽 결과를 원문과 대조하고, 보완 정의와 충돌을 구별한다. Base의 의미가
명령 세트별 정의로 위임된 경우 두 근거를 연결한다. 단순히 나중에 읽은 문서를 우선하거나
같은 바이트 위치의 정의를 덮어쓰지 않는다. 검토 후에도 데이터는 candidate로 유지한다.

대표 항목 CMIC, LBA Format, AWUN/AWUPF, NSZE/NCAP/NUSE, Power State Descriptor로
구조·규칙 표현과 버전 비교를 먼저 확인한 뒤 나머지 범위를 확장한다. 이 목록은 검토 순서이며
해당 항목의 추출·승인이 완료되었다는 선언이 아니다.

## 검토자가 확인할 내용

1. **문서와 응답:** Bundle과 revision이 맞는지, CNS·CSI·Namespace 질의 조건이 섞이지 않았는지 확인한다.
2. **구조:** 바이트·비트 범위, 배열 개수와 간격, 하위 구조, Reserved와 Vendor 영역을 원문 표와 대조한다.
3. **요구사항:** 원문의 의무 수준, 조건·예외, 다른 필드 및 실행 상태 의존성을 확인한다. Reserved를 자동으로 0 요구로 바꾸지 않는다.
4. **보완과 충돌:** 양쪽 출처를 보존하고, 명시적 위임·보완인지 실제 상충인지 확인한다. 확인할 수 없으면 미해결로 둔다.
5. **출처와 차이:** PDF 페이지와 인쇄 페이지를 구별하고, 두 revision 원문을 대조해 구조뿐 아니라 문구·의무 수준의 변경을 확인한다.
6. **완료 범위:** 응답의 바이트 커버리지, 하위 비트·설명 검토, 관련 절·역참조 탐색을 각각 확인한다. 미해결 또는 범위 제외 항목에 사유가 있는지 확인한다.

빌드 성공은 입력 계약과 기계적으로 검사할 수 있는 일관성을 확인한 결과다. 표에 모든
바이트가 표시되어도 하위 비트와 모든 관련 절을 검토한 것은 아닐 수 있다. 검토 보고서와
미해결 목록을 함께 읽고, 근거가 없는 값을 추측으로 보충하지 않는다.

## 수정과 승인

오류는 후보 입력에서 고치고 빌드·Diff·관련 테스트를 다시 실행한다. Core 모델이나
검증 의미를 바꾸면 해당 동작과 오류 사례의 테스트를 추가한다. 기존 Builder 회귀
테스트도 실행한다. 후보 Diff는 문서 간 후보 해석의 차이이며 DUT 영향 분석은 후속 범위다.

사람이 원문과 대조한 범위에 대해 검토자와 검토 근거를 남긴 뒤에만 별도 승격 절차를
진행할 수 있다. 현재 후보 CLI는 자동 승격 기능을 제공하지 않는다. 승인 시에도 출처와
각 문서의 이력을 보존해 Source Base/Delta로 옮기며, 생성된 Snapshot을 원본으로 복사해
관리하지 않는다. 미해결 범위는 승인한 항목과 함께 숨기지 않고 유지한다.

조건부 Expected Profile과 판정 엔진은 합성 TEST/FIXTURE로 먼저 검증한다.
[규칙 실행 파일럿](rule_execution_pilot.md)은 실제 후보의 자동 승격·실행과 분리한다.
이 문단은 초기 파일럿 기록이다. SQLite 원본 관리와 명시적 제품 Profile 선택은 현재 구현되었다. 실제 SSD 수집과 Excel은 후속이다.

## 프로젝트 완성 계획 5단계 (2026-10-12)

[원문 대조와 실행 범위 표](nvme_requirement_coverage.md)에 따라 두 Bundle의 우선 요구사항을
candidate로 확대했다. 용량·THINP·공통 LBAF 인코딩/metadata·atomic 상속/관계·큐 max·
RPMB/ACWU/HMB와 새 Bundle HIR 일관성을 기존 Builder·정규화·Resolver로 실행한다.
원문 hash를 확인한 명시적 등록, 사전 전체 백업·리비전 CAS와 과거 검사 재현을 유지한다.
실행 규칙은 사람 검토 전 candidate이고 실제 id-ns는 TEST/FIXTURE 검증이다.
전체 구조 재추출·실제 SSD 명령·OCP/MFND·제품값 추정은 수행하지 않았다.
