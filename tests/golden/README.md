# Generated TEST/FIXTURE golden artifacts

`fixture_build/`의 JSON은 실제 Builder와 Spec Diff 엔진으로 생성한 회귀 테스트 기준입니다.
원본은 `tests/fixtures/knowledge/`이며 실제 제품·Spec·정책 데이터가 아닙니다.

직접 JSON을 작성하거나 수정하지 않습니다. 프로젝트 루트에서 다음 명령으로 재생성한 뒤 변경 내용을 검토합니다.

```bash
python tests/regenerate_fixture_goldens.py --write
```

테스트는 이 명령을 자동 실행하지 않습니다. Golden은 Knowledge Source of Truth가 아닙니다.
