# 원문 위치와 독립 출처 대조

## 원문 위치

규격 원문은 `spec/`에 등록 파일명으로 둔다. `spec/manifest.json`이 PDF·Markdown SHA-256과
아직 없는 문서(Base 2.0e, NVM 1.0e)를 기록하며 `tests/unit/test_spec_sources.py`가
후보 카탈로그의 고정 해시와 일치하는지 검사한다. 판정 근거는 PDF page/figure이며
Markdown 변환본은 대조용 보조 자료다.

```powershell
ssd-validator knowledge build --candidate --source candidates/nvme --documents-root spec --output generated/candidate
```

## 후보 지식 해시

`candidate_knowledge_hash`는 후보 JSON을 파싱한 정규화 바이트로 계산한다. 줄바꿈·들여쓰기가
달라도 같은 내용이면 같은 값이다. 이전 방식(원시 바이트) 해시는 `byte_knowledge_hash`로 함께
기록하며, 과거 DB 리비전의 기존 고정값도 계속 인정한다.

## CNS 01h 세 출처 대조 (Base 2.1)

| 출처 | 역할 |
|---|---|
| `candidates/nvme/structures.json` | 이 프로젝트의 PDF 기계 추출 후보 |
| nvme-id-ctrl-ko `source/catalog.json` | 독립적으로 추출·정리된 외부 카탈로그 |
| `spec/…Base…2.1….md` Figure 312 구간 | (범위, 약어) 존재 여부를 확인하는 세 번째 근거 |

```powershell
.\.venv\Scripts\python.exe tools\apply_source_crosscheck.py --catalog ..\nvme-id-ctrl-ko\source\catalog.json          # 미리보기
.\.venv\Scripts\python.exe tools\apply_source_crosscheck.py --catalog ..\nvme-id-ctrl-ko\source\catalog.json --write  # 반영
```

- 외부 카탈로그와 Markdown이 모두 확인한 비트만 `structures.json`에 추가하거나 이름을 바로잡는다.
  기존 후보 비트와 겹치면 반영하지 않고 `skipped`로 남긴다. 결과는 여전히 `candidate`다.
- 그 밖의 차이(한쪽만 있음, 불일치, Markdown 미확인)는 `candidates/nvme/crosscheck/base21_cns01.json`의
  `review_rows`로 남기며 자동으로 한쪽을 선택하지 않는다.
- `tools/extract_identify_structures.py`로 PDF를 다시 추출하면 이 도구를 다시 실행한다.
- `structures.json`이 바뀌면 후보 지식 해시가 바뀌므로 두 bundle 설정의 `candidate_knowledge_hash`를
  새 값으로 갱신하고, 실제 DB에는 사전 백업 후 원본 가져오기로 새 리비전에 등록한다.
- Base 2.0e CNS 01h는 외부 카탈로그가 없어 대조하지 않았다. 원문 PDF 확보 후 같은 방식으로 확장한다.
