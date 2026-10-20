# 복수 저장 Identify 응답 검사

3단계는 저장한 id-ctrl/id-ns 응답을 한 검사에 넣는다. 기존 단일 로그 입력과 Builder,
raw/JSON 정규화, Resolver와 DB 리비전 서비스를 그대로 사용한다. SSD 명령은 실행하지 않는다.

## GUI 사용

1. 파일 선택에서 여러 파일이나 id-ns·JSON·바이너리를 고르면 `응답 묶음` 표가 열린다.
2. 각 파일의 명령(id-ctrl/id-ns/identify), 형식(text/json/raw)을 확인한다. 파일명으로 명령을 추정하지 않는다.
3. 함께 검사할 응답에 같은 DUT와 수집 세션을 명시한다. Namespace 응답에는 확인한 NSID를 입력한다.
4. CNS/CSI, 시각, 도구 이름·버전·commit은 확인된 값만 입력한다. 빈 값은 UNKNOWN이다.
5. 아래 Bundle·정책·Context를 선택한 뒤 `입력 묶음 검사`를 누른다. 선택 변경 후에는 다시 누른다.
6. scope별 요약과 필드 표를 확인한다. 상세와 JSON에는 각 입력 파일 해시, 원문 바이트,
   수집 메타데이터, 사용한 매핑, Expected Profile, 규칙별 판정과 trace가 연결된다.

같은 DUT라도 세션이 다르면 합치지 않는다. DUT 또는 세션이 없으면 응답마다 분리한다.
동일 DUT/세션의 Controller 응답은 각 Namespace scope에 공유한다. NSID가 없으면 그 Namespace
응답을 별도 scope로 유지한다. 헤더/파일명에서 NSID나 세션을 만들어내지 않는다.

## 데이터 계약

`ssd-validator-captures-v1` envelope의 captures에는 capture_id, filename, command,
source_format, content_base64와 선택 메타데이터를 넣는다. 최대 16개, 각각 원본 1 MiB다.
API는 `/api/analyze-captures`이며 임의 로컬 경로를 읽지 않고 전달한 원본 바이트만 처리한다.

`captures`는 원문과 관찰값을 보존한다. actual_facts는 매핑된 관찰값이고 validation_facts는
기존 타입·폭 정규화를 통과한 실행 입력이다. 최신 도구의 추가 필드, nested JSON, 배열,
미해석 텍스트·raw 바이트도 원문 및 tool_output/unmapped_bytes에 보존한다.
중복 JSON 키는 원본과 중복 값 목록을 보존하고 전체 캡처를 판정 입력에서 제외한다.
중복 이름/별칭은 해당 FieldRef를 제외하며, 복수 같은 응답과 같은 FieldRef는 CONFLICT다.
동일한 값이어도 암묵적으로 하나를 선택하지 않는다. 누락은 UNKNOWN, 타입 오류는 ERROR다.

`metadata`는 사용자가 제공한 수집 사실이다. 텍스트/JSON의 명시적으로 선택한 명령 어댑터는
별도 `interpretation`으로 CNS/CSI 매핑을 선택할 수 있다. 이것은 원래 명령 인수가 확인됐다는
뜻이 아니다. 정규화 내부 query는 interpretation_capture에 분리하고 실제 metadata의 UNKNOWN을
바꾸지 않는다. raw는 명시적 CNS/CSI가 모두 없으면 해석하지 않는다. command/CNS 모순은 ERROR다.
도구 버전은 선택한 검사 Bundle을 바꾸지 않는다. 범용 identify 텍스트와 실제 NVM 전용 텍스트
형식은 확인된 어댑터가 없어 실행하지 않는다. 명시적 query의 raw/JSON은 등록된 필드만 해석한다.
추가 nested JSON의 동명 필드는 기존 scalar alias로 자동 해석하지 않는다. JSON scalar는
root의 명시적 이름, 배열은 단일 index와 등록 field ID에 연결된 container 경로만 사용한다.

`scopes`는 DUT/세션/NSID, 사용 capture_id, 관찰 Actual과 실행 Actual, 충돌, 적용 Context,
Expected Profile과 evaluate 결과를 가진다. FieldRef 자체의 키는 기존 계약을 유지하며
scope별로 따로 평가하므로 Namespace끼리 같은 필드 ID를 덮어쓰지 않는다.

## DB와 CLI

원본 envelope를 기존 validation_run.input에 저장하고 전체 해시를 검증한다.
옵션 input_kind=saved-captures-v1로 재실행 경로를 구분한다. 원래 단일 로그 이력은 이전 경로를 유지한다.
지식 스키마는 v3 그대로이며 migration이 필요하지 않다. 기존 전체 백업/복원에 모든 원문과
scope 결과가 포함된다. 당시 Source 리비전과 Bundle/Context/정책으로 재실행한다.

```powershell
.\.venv\Scripts\python.exe -m ssd_validator.cli actual review-captures --input tests\fixtures\saved_captures\TEST-input.json --bundle nvme-2.1-nvm-1.1 --experimental
```

예제는 합성 TEST 자료다. 실제 첨부 id-ctrl의 기존 6개 규칙을 재현했고, Namespace 필드/배열 규칙은
임시 테스트 DB에서만 등록해 정상·위반·누락·raw/JSON과 이력 재현을 검증했다. 실제 원본 DB에
id-ns 규칙이나 제품 정책을 추가하지 않았다. 실제 id-ns 로그와 추가 명령 형식, Namespace 요구사항
확대는 후속 자료·규칙 검토가 필요하다. 일부 Controller 규칙의 PASS가 Namespace 적합성을 뜻하지 않는다.
