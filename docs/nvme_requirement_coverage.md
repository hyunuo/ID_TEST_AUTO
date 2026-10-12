# NVMe 요구사항 확대 — 5단계

기준: 2026-10-12. 두 Bundle의 원문 PDF와 기존 curated 후보를 대조한 **candidate 실행 범위**다.
전체 규격 적합성이나 사람의 승인을 의미하지 않는다. 실제 원본은 SQLite 리비전이며
`candidates/nvme/executable_requirements.json`은 이번 등록을 위한 원문 대조 후보 패키지다.
파일 수정만으로 기존 DB를 갱신하지 않는다. `generated/`는 변경하지 않는다.

## 등록 내용과 근거

원문 네 PDF의 SHA256을 `candidates/nvme/catalog.json`과 대조했다. Base 2.0e + NVM 1.0e,
Base 2.1 + NVM 1.1을 별도로 확인했다. 아래 페이지는 물리 PDF 페이지다. Base 2.1의
인쇄 페이지는 물리 페이지보다 22 작다. 최신 도구/헤더의 정의를 이전 Bundle에 이식하지 않는다.

| 범위 | Base 2.0e + NVM 1.0e | Base 2.1 + NVM 1.1 | 실행 해석 / 중요한 예외 |
|---|---|---|---|
| 용량 관계 | NVM p10 §2.1.1 | NVM p12 §2.1.1 | 특정 NSID의 NSZE ≥ NCAP ≥ NUSE |
| THINP | NVM p10, NSFEAT p57 | NVM p12, NSFEAT p81 | bit0=0이면 NCAP=NSZE. NUSE=NCAP은 MAY라 필수 규칙 없음 |
| LBA 인코딩 | NVM p58, 64–65 Fig98 | NVM p81, 89–90 Fig116, 149–151 §5.5 | 공통 형식 0..NLBAF만 검사. LBADS=0은 unavailable, nonzero는 ≥9 |
| Metadata | NVM p65 Fig98 | NVM p90 Fig116 | 형식별 metadata 미지원이 명시된 경우만 MS=0. 누락은 UNKNOWN |
| Namespace atomic | NVM p12 Fig4, 60–61 | NVM p14 Fig4, 84–85 | NSABP=1, newer는 MAM=0. NAWUN/NAWUPF=0은 Controller 값 상속 |
| Controller atomic | NVM p66 Fig99 | NVM p91 Fig117 | AWUPF ≤ AWUN 필드 정의는 필수. 기존 Context gate를 명시적 변경으로 제거 |
| 큐 엔트리 | Base p280 Fig280 | Base p340 Fig312 | 기존 low nibble MASK와 함께 max nibble ≥6/4. 권고 max=6/4를 EXACT로 강제하지 않음 |
| RPMB / Security | Base p275, 270 | Base p334, 330 | RPMBS[2:0] nonzero이면 OACS bit0 필요. 제품의 필수 지원 정책과 별개 |
| Fused / ACWU | Base p281, NVM p66 | Base p341, NVM p92 | FUSES bit0=0일 때 ACWU=0은 명시된 zero 요구 |
| HMB | Base p274 | Base p334 | HMPRE ≥ HMMIN. 최신 HMLMS 관련 전체 Controller 범위는 미구현 |
| HIR / DST | 없음: bit1 Reserved | Base p335 | OACS bit4=0이면 DSTO bit1=0. 이전 Bundle에 zero 요구 생성하지 않음 |

기존 `requirements.json`의 `NVM_*.CURATED.CAPACITY_ORDER`, `THINP_ZERO_NCAP`,
`LBADS_NONZERO_MINIMUM`, `METADATA_ABSENT`, `AWUPF_BOUND`, `NAWUN_BASELINE`을
대조 출발점으로 사용했다. 이 원래 후보 큐는 그대로 남기고, 실행 조건/예외를 새 패키지에 기록했다.
`THINP_ZERO_NUSE_PERMISSION`은 필수 제약으로 바꾸지 않았다. `THINP_TRACKING`,
`ANA_ZERO_REPORTING`, `ALL_NS_UNSUPPORTED`는 아래 비실행 범위에 남긴다.
AWUPF_BOUND의 Figure4 mode 조건과 별도로 CNS01 필드 정의의 명시적 필수 문장을 확인했다.

새 규칙 인스턴스는 이전 Bundle 150개, 새 Bundle 151개다. 각 64개 형식의 LBADS와 MS
조건이 반복되므로 독립 요구사항 301개를 추출했다는 뜻이 아니다. 기존 6개 중 atomic 규칙
하나를 Bundle별로 근거를 남겨 수정한다. 새 필드 ID는 17/18개이며 기존 6개와 합쳐 23/24개다.
전체 구조 재추출을 수행하지 않았다. LBAF.MS/LBADS는 64개 배열 슬롯, stride=4로 관리한다.

각 후보에 실행 조건, 의무 수준, 예외, 의존 입력, document/revision/section/figure/물리·인쇄
페이지, 미해결 사람 검토를 등록한다. 결과 trace에는 실제 사용한 규칙·조건·입력·출처와
해당 DB Source hash가 연결된다. 모든 새 규칙은 candidate이며 reviewer/confirmed를 만들지 않는다.

## 실행 범위와 남은 입력

| 항목 | 분류 | 현재 처리 / 다음 필요 사항 |
|---|---|---|
| 용량·THINP 정적 관계 | 실행 가능 | CNS00 특정 Namespace. NSID 미확인이면 UNKNOWN, Controller만 입력하면 N/A |
| LBADS 및 공통 형식 개수 | 실행 가능 / 추가 정보 필요 | NLBAF는 zero-based. Host LBAFEE 미확인 조건은 UNKNOWN |
| 형식별 metadata zero | 추가 정보 필요 | `namespace.lbaf.<index>.metadata_supported`를 명시 입력. MS나 Reserved로 지원 여부를 추정하지 않음 |
| Single Atomicity 관계 | 실행 가능 | 같은 DUT/세션 Controller+Namespace 입력. 지원·상속 조건을 분기 |
| 양쪽 boundary가 nonzero인 NABO 관계 | 실행 가능 | NABO ≤ NABSN, NABSPF. 양쪽 zero면 명시 NABO=0 |
| 한쪽 boundary만 zero인 NABO | 원문 해석 재검토 | 현재 range 검사는 N/A; 전체 boundary 적용 해석 확장 전 보류 |
| 큐·HMB·RPMB·Fused·HIR 일관성 | 실행 가능 | 누락 필드는 UNKNOWN. larger queue max 허용, HIR는 새 Bundle만 |
| ANA 상태의 NUSE/NVMCAP zero 보고 | 추가 정보 필요 | 현재 ANA 상태, CMIC, NVMCAP과 관련 절의 의존 근거 확보 필요 |
| THINP allocation tracking | 동작 검사 필요 | write/deallocate 전후 이력. 단일 Identify 값으로 증명하지 않음 |
| Atomic write / power failure | 동작 검사 필요 | workload·전원 장애의 실제 데이터 관찰 필요 |
| NSID=FFFFFFFFh query 거절 | 동작 검사 필요 | NVM1.0e SHALL / 1.1 MAY 차이 유지. 일반 특정 Namespace 규칙으로 대체하지 않음 |
| Active FLBAS lookup / unique LBA formats | 미구현 | 동적 인덱스 선택, newer NLBAF+1+NULBAF, CNS09/0A의 unique 속성 |
| Multiple Atomicity Mode / NACWU | 미구현 | MAM=1, compare/write namespace 관계와 추가 의존성 별도 확장 |
| 전체 기능 지원 일관성 / 모든 필드 | 미구현 | 본 단계는 우선 필드 subset. 미등록 필드의 관찰값은 REVIEW |
| OCP/MFND·제품 정책 | 후속 6단계 | 이번에 실제 요구나 제품값을 추정·등록하지 않음 |

입력에서 확인한 `input.has_controller`, `input.has_namespace`, `namespace.query_is_specific`은
서비스가 scope/query 해석으로 만든 적용 사실이며 사용자 Context로 위조하지 못한다.
명령 종류의 해석은 수집 metadata의 확인을 대신하지 않는다. CNS/CSI/NSID/도구 버전의
미확인 상태는 기존 계약대로 보존한다. Host LBAFEE와 metadata 지원은 별도 명시 입력이며
도구 버전과 Actual 값에서 추정하지 않는다.

## DB 등록과 운영

등록은 SQLite의 현재 리비전을 확인한 명시적 작업이다. PDF hash, 후보 상태, 규칙 참조,
필드/바인딩과 기존 atomic 규칙의 원래 내용이 일치해야 한다. 사용자가 이미 수정한 내용과
충돌하면 등록을 거절한다. 예상 리비전이 오래되어도 거절하며 last-write-wins를 쓰지 않는다.
검증 후 전체 DB 사전 백업을 `data/backups/pre-stage5-r*.sqlite3`에 만들고 새 리비전으로
원본 패키지·필드·규칙을 함께 저장한다. 스키마는 v3 유지, 기존 검사 원문/결과는 불변이다.

```powershell
.\.venv\Scripts\python.exe tools/prepare_nvme_requirement_expansion.py --pdf-dir ..
.\.venv\Scripts\python.exe -m ssd_validator.cli database status
# 실제 현재 revision을 확인하여 아래 값과 일치시킨다.
.\.venv\Scripts\python.exe -m ssd_validator.cli knowledge expand-nvme --recipe candidates/nvme/executable_requirements.json --pdf-dir .. --expected-revision 1 --reason "Pinned PDF comparison; candidate expansion stage 5"
```

새 설치의 파일 bootstrap이나 기존 DB의 파일 변경은 후보 패키지를 실행 규칙으로 자동 등록하지
않는다. GUI의 `NVMe 요구사항 적용 범위`는 현재 DB 리비전의 coverage와 규칙별 원문 검토 정보를
표시한다. `not_registered`, `matches_candidate`, `edited_review_needed`를 구분하므로 등록 후
규칙이 편집되면 예전 해석을 그대로 현행 규칙의 검토 근거로 주장하지 않는다. 과거 검사 trace는
당시 리비전이며 이 패널의 현재 리비전과 구분한다. 규칙 폼에는 GE 정수 조건도 제공한다.

기존 Atomic Context는 추가 사용자 선언으로 남지만, 확대 리비전의 필수 Controller
AWUPF 관계를 해제하지 않는다. 과거 r1 검사는 당시의 Context와 옛 규칙으로 재현된다.
기존 임시 Format/FW 정책은 provisional이며 `규격 규칙만 적용`으로 제외할 수 있다.

## 검증과 완료 기준

`tests/unit/test_nvme_expansion.py`는 두 Bundle의 모든 새 규칙과 수정 규칙에 정상·위반·경계,
조건 거짓/누락, target/비교 입력 누락, candidate provenance를 검증한다. 무조건 규칙은
조건 거짓 사례가 없음을 그대로 유지한다. 합성 값은 TEST이며 실제 DUT 규격값을 추정하지 않는다.
0 상속, MAY/Reserved, MAM·HIR 버전 차이, 큐의 큰 max 허용, 배열 인덱스 구분, scope 입력 위조
거절, 실제 원문 hash 확인 등록·CAS·사전 백업·멱등 등록·옛 검사 재현도 검증한다.
`test_nvme_expansion_api_cli.py`는 같은 HTTP/CLI 서비스의 후보 판정과 GUI coverage를 확인한다.

원문 대조 후보와 비실행 범위를 공개하고 기존 경로에서 재현할 수 있는 것이 5단계 완료 기준이다.
실제 id-ns 저장 로그는 미확보이므로 Namespace 수용 검증은 TEST/FIXTURE로 수행한다.
실제 SSD 명령은 실행하지 않는다. 전체 규격 승인, 실제 atomic 동작 검증은 완료 범위가 아니다.

실행 기록: 전체 회귀 717개 통과(299.97초). 실제 DB schema v3 / r2 후보 등록, 기존 11개
결과 보존과 r1 재실행 일치. 사전 백업은
`data/backups/pre-stage5-r1-6a4acf46f897479cb5de79b7621fe8d3.sqlite3`에 있다.
첨부 Controller 로그는 PASS 10 / N/A 147 규칙이며 필드 PASS 7 / N/A 1 / REVIEW 58 /
UNKNOWN 3이다. GUI 검사 #14/#15에서도 새 HMB 원문 근거와 coverage 표시를 확인했다.
