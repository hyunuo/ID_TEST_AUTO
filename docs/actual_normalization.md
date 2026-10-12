# 도구 버전과 제품 규격을 분리한 Identify 정규화

## 구현 범위

최신 nvme-cli/libnvme가 아는 필드 정의와 제품의 적용 규격은 서로 다른 정보다.
제품 Bundle이 필드 의미·Reserved 여부·적용 규칙을 결정하고, 도구 버전은 수집
이력으로 기록한다. 장치가 보고한 NVMe 버전도 진단 정보이며 Bundle을 바꾸지 않는다.
예를 들어 제품이 2.1 + 1.1이고 도구가 더 최신 규격을 해석하더라도 제품의 검증
기준은 그대로 유지해야 한다. 여기서 더 최신 규격 번호는 특정 CLI 릴리스의
실제 지원 수준을 주장하는 것이 아니다.

현재 구현은 **저장한 raw/JSON의 오프라인 정규화**다. 장치 명령 실행, nvme-cli 설치,
헤더 전체 재추출, 제품 Profile 자동 선택과 실제 규격 적합성 승인을 수행하지 않는다.
실제 NVMe/OCP/MFND 승인 데이터가 없는 상태에서 생산용 판정을 활성화하지 않는다.

## 실행

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli actual normalize --layout tests/fixtures/actual_normalization/layout.json --capture tests/fixtures/actual_normalization/capture.json --raw tests/fixtures/actual_normalization/response.raw
.\.venv\Scripts\python.exe -m ssd_validator.cli actual normalize --layout tests/fixtures/actual_normalization/layout.json --capture tests/fixtures/actual_normalization/capture.json --json tests/fixtures/actual_normalization/response.json
```

테스트의 도구 이름·버전·장치·필드·값은 모두 합성 데이터다. CLI는 파일을 읽고
JSON 보고서만 출력하며, 원본이나 generated 산출물을 수정하지 않는다.
raw와 JSON 중 하나를 명시적으로 선택한다. raw가 잘못되었다고 JSON으로 자동
전환하거나 잘못된 길이를 자르거나 zero-padding하지 않는다.
보고서의 ERROR/UNKNOWN은 종료 코드와 별개다. 계약/파싱 오류는 종료 코드 1,
정규화 결과가 생성되면 종료 코드 0이므로 소비자는 보고서 status를 확인한다.

## 입력과 출력 계약

Layout은 Bundle ID, Base/NVM revision, 정확한 CNS/CSI/NSID/controller 질의,
응답 크기, 필요한 필드 매핑과 근거를 담는다. 각 필드는 offset·length·endian·type,
배열 인덱스·의미 상태와 provenance를 가진다. JSON 경로는 문자열 key와 정수
index를 명시적으로 나열한다. 출력 이름이나 최신 헤더로 매핑을 추측하지 않는다.
필드 중복·겹침·경계 초과·비트 단위 wire 매핑·미검토 confirmed 근거는 거부한다.

Capture metadata는 도구 이름·버전·선택적 commit, 장치 ID와 정확한 질의를 기록한다.
입력된 도구 정보는 수집자가 제공한 기록이며 도구의 실제 설치 상태를 자동 검증한
결과가 아니다. 제품 Bundle은 이 정보로 선택되지 않는다.

raw는 Layout이 선언한 크기와 정확히 일치해야 한다. 숫자는 지정 endian으로
전체 비트를 읽고, 고정 길이 문자열은 ASCII로 읽어 끝의 space/NUL을 제거하되
원본 hex도 보존한다. bytes는 opaque hex로 보존하고 숫자로 임의 변환하지 않는다.
문자열 ASCII 검증 실패는 ERROR다.

JSON은 등록한 경로만 해석한다. 누락은 UNKNOWN, 잘못된 타입·경로 구조는 ERROR다.
bool이나 문자열 숫자를 정수로 변환하지 않는다. bytes의 JSON 인코딩은 도구별
어댑터가 필요하므로 현재 지원하지 않는다. 중복 key와 NaN/Infinity도 거부한다.
JSON의 문자열은 이미 도구가 디코딩한 값으로 취급하며 raw와 동일한 바이트 표현을
복원했다고 주장하지 않는다.

보고서는 raw/JSON·layout·metadata 입력 파일의 SHA-256과 경로를 보존한다.
raw에서 매핑되지 않은 영역은 offset·length·hex를 남긴다. 이 영역은 **unmapped**이며
Reserved나 최신 기능이라고 추정하지 않는다. JSON은 전체 tool_output을 보존하고
매핑하지 않은 최상위 key를 별도로 표시한다. 매핑한 객체 안의 사용하지 않은
하위 key도 전체 tool_output에 보존되며, 세부 경로 전체의 분류를 완료한 것은 아니다.

정규화의 OBSERVED는 값을 해석했다는 의미이고 PASS가 아니다. fixture + confirmed
매핑만 ActualFact로 연결한다. candidate/provisional 매핑은 값을 보여주되 REVIEW로
남기고 authoritative ActualFact를 만들지 않는다. data_kind=candidate인 Layout은
confirmed 표시가 있어도 실행 입력으로 승격하지 않는다.

## Resolver 연결과 버전·Reserved 처리

`layout_from_profile(profile, query, response_size=..., array_strides=..., json_paths=...)`
는 기존 Builder가 만든 Profile의 필드·근거·이력을 재사용한다. 배열 stride는 별도로
명시해야 하며 길이나 count만 보고 추정하지 않는다. 실제 stride/질의 매핑은 승인
절차를 거칠 Source 데이터여야 한다. JSON 경로는 사용하는 도구 버전의 실제 출력
샘플을 보고 확정해야 한다. 현재 fixture JSON 경로를 실제 CLI 출력에 그대로 적용하지 않는다.

`normalize_raw(layout, capture, raw)` / `normalize_json(layout, capture, payload)`
는 정규화 보고서를 만든다. `evaluate_normalized(profile, reports)`는 fixture Profile에
대해 이를 기존 Resolver에 전달하며 모든 수집 보고서와 최종 판정을 함께 보존한다.
다른 Bundle/revision, 다른 장치, 여러 Namespace, 중복 capture/fact, Context NSID
불일치, Source-built 필드 정의·근거 불일치와 정규화 ERROR를 거부한다.
candidate/unconfirmed 수집 결과는 REVIEW로 남기고 실행하지 않는다.
누락된 JSON 필드는 ActualFact에서 빠지며 기존 Resolver에서 UNKNOWN으로 유지된다.

최신 CLI에서 새 이름을 붙인 영역도 선택한 Layout의 의미로 읽는다. 이전 규격에서
Reserved인 필드/비트를 자동으로 새 기능으로 채택하거나 expected=0으로 만들지 않는다.
실제 Reserved 관련 검사는 승인된 제품 Bundle의 **명시적 요구사항**으로 작성한다.
비트 의미와 검사 여부는 Profile의 Field/Bit Schema와 규칙이 담당하고, 정규화는
전체 필드 값을 전달하므로 알 수 없는 비트를 제거하지 않는다.

## 완료한 검증과 다음 단계

최신/이전 도구 메타데이터 변경에도 같은 Bundle의 값이 유지되는 사례, 같은 바이트의
Reserved/defined 해석 차이, raw 전체 바이트 보존, 추가 JSON 필드·배열·누락·타입 오류,
raw 길이/질의 불일치와 candidate 격리를 검증했다. Source-built fixture Profile에서
raw Namespace/Controller 값을 결합해 기존 규칙 판정까지 검증했다.

다음 단계는 필요한 실제 필드의 승인된 Bundle 매핑과 대상 CLI 릴리스의 출력 샘플을
확보하는 것이다. 그 후 release/commit을 고정한 실제 수집 어댑터를 연결한다.
실제 후보 승인·OCP/MFND 요구사항·Product Profile·FW 비교·Excel·SQLite는 별도 작업이다.
