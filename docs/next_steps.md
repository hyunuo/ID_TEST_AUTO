# 향후 작업

기준: 2026-10-20, 통합·간소화 1차 이후. 목표 우선순위는 검증 정확도(정합성) > 검증 편의성 > 유지보수성이다.
완료 내용은 [현재 상태](current_status.md)를 참고한다.

## 사람이 해야 하는 일 (자동화로 대신할 수 없음)

| 항목 | 필요한 것 | 왜 필요한가 |
|---|---|---|
| 실제 장비 로그 확보 | `nvme id-ctrl`, `nvme id-ns`의 텍스트·`-o json`·`-b` 바이너리, `nvme version` | 지금 판정 검증은 합성 TEST 장치뿐이다. 실제 제품에서 판정이 맞는지는 실제 로그로만 확인된다. 장치 로그는 저장소에 커밋하지 않는다. |
| 규칙·구조 사람 검토 | 규격을 아는 검토자와 승인 기준 | 모든 규칙과 구조는 candidate다. 실행 규칙 25종(LBAF 인덱스 복제 포함 151개)과 `candidates/nvme/crosscheck/base21_cns01.json`의 검토 행을 원문과 대조해 승인해야 한다. |
| 제품 정의 | 대상 제품 Profile, FW, OCP 적용 여부, 내부 정책 원문 | 없으면 제품 정책·OCP 판정은 계속 UNKNOWN 또는 미적용이다. |

## 정합성

1. **Base 2.0e CNS 01h 비트 정정.** 2.0e 비트 이름은 기계 추출 오류(설명 문장 조각)가 남아 있다. 2.0e PDF를 Markdown으로
   변환하고 `tools/apply_source_crosscheck.py`를 2.0e에도 적용한다(외부 카탈로그가 없어 PDF 추출 대 Markdown 2자 대조).
2. **필드 정의를 한 곳으로.** 필드 위치가 `structures.json`, `executable_requirements.json`(손입력), `base.yaml`,
   bundle 설정의 `field_evidence` 사본에 나뉘어 있다. FUSES offset 오류(524→522)가 이 구조에서 나왔다. 실행 필드를
   `structures.json`에서 생성하고 사본과 `candidate_knowledge_hash` 고정 체인을 없앤다.
   `tests/unit/test_layout_consistency.py`는 그때까지의 안전장치다.
3. **장치 보고 버전에 맞는 규격 자동 제안.** GUI는 불일치 경고만 한다. 기본 선택이 2.0e라서 2.1 장치를 잘못된 규격으로
   검사하기 쉽다.
4. **nvme-cli 출력 이름 대응 확장.** JSON `ds`(LBADS)만 대응했다. `domainid`(DID), `ocfs`(CDFS) 등 규격 약어와 다른
   이름과 다른 nvme-cli 버전의 출력을 실제 로그로 확인해 추가한다.
5. **비표준 로그 형식.** 사내 도구가 `NVME Identify Controller Full Dump:` 같은 형식을 쓴다면 표준 형식으로 바꾸는 입력
   어댑터를 추가한다. 지금은 안전하게 거부한다.

## 간소화 (DB와 GUI 편집은 유지, 판정 기준값 불변을 확인하며 단계적으로)

1. LBAF 규칙 128개를 "각 인덱스마다 적용" 규칙 2개로 표현하고 규칙 ID의 `STAGE5` 같은 작업 단계 이름을 없앤다.
2. 판정에 쓰이지 않는 기계 추출 요구사항(`candidates/nvme/requirements.json`, 8만 줄)을 실행 경로에서 분리해 검토 자료로 둔다.
3. 문서 정리: 단계 기록 문서를 `docs/history/`로 옮기고 README와 운영·지식 편집·원문 대조 문서만 남긴다.
4. 테스트 분리: 기본 테스트(빠름)와 DB·GUI·원문 등록 테스트(느림)를 나눈다. 전체는 현재 약 40분이다.
5. `tests/golden/baseline/engine_baseline.json`(2.1MB)의 중복 기록(scope별 반복)을 줄인다.

## 편의성

1. nvme-id-ctrl-ko의 한국어 설명·조건을 GUI 필드 상세에 통합하고, ko HTML 뷰어는 이 프로젝트 데이터에서 생성한다.
   ko 조건 231개는 판정 가능 / 외부 관측 필요 / 해석 안내로 분류해 규칙 후보로 옮긴다.
2. 응답 묶음 검사 결과에도 비트 지도를 표시한다(결과에 필드 정의 포함 필요).
3. 응답 묶음 검사 시간(6~8초)을 줄인다.

## 참고

- 합성 TEST 장치: `tools/make_synthetic_dut.py`, 판정 기준값: `tools/capture_baseline.py`.
- 실제 로그를 받으면 `tests/unit/test_synthetic_dut.py`와 같은 형식 일치 검사에 추가한다.
- MFND는 사용자 지시로 제외 상태다.
