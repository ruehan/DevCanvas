# 리뷰 기록 — UI/Code 에이전트 LLM 전환 (ADR-0024)
- 날짜: 2026-07-10
- 브랜치: feat/ui-code-llm
- 최종 판정: 통과 (2라운드)

## 1라운드
- 판정: 수정 필요
- 검증: verify 결과 요약
  - `verify.sh api/` — ruff/mypy/pytest 모두 통과 (ui 7 + code 9 = 16 신규 + 137 기존 = 152 통과, 64 파일)
  - `verify.sh web/` — vitest+tsc 통과 (44 통과)
- 지적사항:
  - [P1] `agents.py:81-90, 143-151` — `llm.generate(...)` 호출이 try/except 없이 노출. ADR-0024는 "LLM 호출 실패 → rule-based fallback, GenerationError 미전파"를 명시했으나 실제 코드는 그대로 전파 → GLM 다운/스키마 위반 시 파이프라인 500.
  - [P2] `agents.py:179-184` — `_is_valid_tsx`가 `'use client'`/`export default function` substring 검사뿐. LLM이 stub에 없는 컴포넌트(`@/components/non-existent`)를 import해도 채택 → sandpack 빌드 실패, 불필요 stub 잔존.
  - [P2] `tests/pipeline/test_*_llm.py` — LLM 호출 자체 실패(GenerationError) 시나리오 테스트 0개. P1과 짝.
  - [P3] `agents.py:84-89` — `design_system.model_dump()`을 context로 전달하나 docstring에 "현재 미사용" 명시 → 토큰 낭비.
  - [P3] `test_ui_generator_llm_tree_differs_by_kind` — 더블이 하드코딩 다른 tree를 반환하는 것만 검증, 명목적.
- 반영:
  - P1 — `ui_generator_agent`/`code_generator_agent` 둘 다 `try/except GenerationError`로 감싸고, 실패 시 `build_ui_generation`/`build_code_generation`로 fallback.
  - P2-1 — `_is_valid_tsx`에 `_TSX_IMPORT_RE`로 `@/components/<x>` 추출 후 stub 집합(`pascal_to_kebab(component_tree)`)의 부분집합 검증 추가. 위반 시 페이지 단위 fallback.
  - P2-2 — `BoomLLM`(ui)·`BoomLLM`(code)·`BadImportLLM`(code 정합성) 테스트 추가.
  - P3-1 — context에서 `design_system` 제외 (시그니처는 유지, ADR 영향 섹션에 명시).
  - P3-2 — 다양성 테스트 유지 (kind별 다른 tree 후보 보장 의도 유효).

## 2라운드
- 판정: 통과
- 검증: verify 결과 요약
  - `verify.sh api/` — ruff/mypy/pytest 모두 통과 (152 통과)
  - `verify.sh web/` — vitest+tsc 통과 (44 통과)
  - 신규 LLM 테스트 단독 실행 — ui 8 + code 11 = 19 통과
- 라운드 1 지적 반영 확인:
  - [P1] `agents.py:84-95(ui)`·`:149-160(code)` try/except GenerationError 추가. BoomLLM 테스트로 검증. ✓
  - [P2] `_is_valid_tsx` 강화 — import 정합성 검증, stub kebab 집합 도출. BadImportLLM 테스트로 페이지 단위 fallback 검증. ✓
  - [P2] LLM 실패 테스트 3개 추가(ui BoomLLM, code BoomLLM, code BadImportLLM). ✓
  - [P3-1] context에서 design_system 제거, ADR 영향 섹션에 "현재 context 미포함" 명시. ✓
  - [P3-2] 다양성 테스트 유지. ✓
- 신규 결함:
  - [P3-참고] `_is_valid_tsx` 정규식이 단일 세그먼트만 캡처. `@/components/foo/bar` 발생 시 false positive 가능. instruction이 단일 세그먼트 요구, 실제 stub 구조 flat, 발생 확률 낮음 → 비차단. 후속 관측 시 재검토.
- 회귀: 없음 (기존 0011/0012 결정성 테스트 전부 통과 — `build_*` 함수 보존).

## 참고
- 브랜치: main으로 fast-forward 병합 후 삭제 (2026-07-10)
- 커밋:
  1. `docs(adr): UI/Code 에이전트 LLM 전환(0024, 0011/0012 보완)`
  2. `feat(ui): UI generator LLM 전환 + rule-based fallback(ADR-0024)`
  3. `feat(code): code generator LLM page 골격 전환 + 템플릿 결합(ADR-0024)`
  4. `fix(ui,code): LLM 호출 실패 fallback + stub 정합성 검증 보강(ADR-0024 리뷰 반영)`