# Test fixtures

이 디렉터리는 엔진 검증을 위한 합성 테스트 데이터 전용입니다. 모든 데이터는 이름과 메타데이터에 `fixture`, `dummy`, `example` 중 하나를 명시합니다.

합성 데이터는 실제 NVMe/OCP/MFND 정의나 내부 정책이 아니며, 실제 제품의 Expected를 만드는 Source Knowledge로 사용하지 않습니다.

실제 문서에서 유래한 데이터는 승인과 provenance 없이 테스트 데이터로 추가하지 않습니다. Golden 기대 결과는 검토하여 관리하며 구현 출력으로 무조건 갱신하지 않습니다.

`rule_pilot/`은 Source-built Snapshot과 오프라인 규칙 실행을 위한 합성 fixture입니다.
confirmed와 TEST_FIXTURE_REVIEWER는 fixture 테스트 계약만 의미하며 실제 규격 승인이 아닙니다.
입력 JSON은 조건·관계 제약·Capability 매핑·배열 항목을 다룹니다.

`actual_normalization/`은 저장 raw/JSON과 도구 metadata를 사용하는 합성 입력입니다.
response.raw는 TEST SIZE/CAPACITY/USED/LBADS 값과 미매핑 바이트를 포함한 4096-byte
입력 capture이며 실제 SSD dump나 generated Snapshot이 아닙니다. 대응하는 JSON에는
최신 도구의 추가 필드를 흉내 낸 test_newer_only_feature가 있습니다.
# 복수 저장 응답

`saved_captures/TEST-input.json`과 TEST-id-ctrl/TEST-id-ns 텍스트는 합성 입력 경로 예제다.
실제 제품 값·규격 승인·장치 출력으로 사용하지 않는다. Namespace 실행 규칙은
test_saved_captures.py가 임시 SQLite에 TEST 필드/규칙으로 등록하며 실제 DB를 수정하지 않는다.
