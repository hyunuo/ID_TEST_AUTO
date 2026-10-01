# Test fixtures

이 디렉터리는 엔진 검증을 위한 합성 테스트 데이터 전용입니다. 모든 데이터는 이름과 메타데이터에 `fixture`, `dummy`, `example` 중 하나를 명시합니다.

합성 데이터는 실제 NVMe/OCP/MFND 정의나 내부 정책이 아니며, 실제 제품의 Expected를 만드는 Source Knowledge로 사용하지 않습니다.

실제 문서에서 유래한 데이터는 승인과 provenance 없이 테스트 데이터로 추가하지 않습니다. Golden 기대 결과는 검토하여 관리하며 구현 출력으로 무조건 갱신하지 않습니다.
