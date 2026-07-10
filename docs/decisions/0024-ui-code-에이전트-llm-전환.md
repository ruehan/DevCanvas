# 0024. UI/Code 에이전트 LLM 전환 (0011/0012 보완)
- 상태: 채택 (0011/0012 보완 — 기존 규칙 함수는 fallback 으로 보존)
- 날짜: 2026-07-10

## 배경
0011(ui_generator), 0012(code_generator)은 각각 rule-based. 같은 `ScreenKind`면 component_tree·page.tsx 골격이
항상 동일 → "프롬프트 무관 항상 같은 결과물" 문제. UX 플래너만 LLM 전환(0023)으로는 화면 구조 다양화 효과가
하위 단계에서 죽음.

## 결정
- **ui_generator_agent**: LLM 호출로 전환. LLM이 각 화면의 `layout` 문자열 + `component_tree` 자체 결정.
  단 `kind`는 대응 `ScreenSpec.kind` 와 일치해야 함(LLM 변경 불가 — 라우팅·템플릿 호환성).
- **code_generator_agent**: LLM 호출로 전환하되 **page.tsx 골격(content)만** LLM 생성. components/types/mock-data는
  기존 rule-based 템플릿 유지(검증·결정성 보존).
- **fallback 정책**: LLM 응답이 스키마/계약 위반 시 기존 rule-based 함수(`build_ui_generation`/`build_code_generation`)로
  graceful degradation. GenerationError 를 던지지 않는다(MVP 가용성 우선).
- **fallback 보존 이유**: GLM 키 미설정/다운/검증 실패 시 데모·테스트 경로가 항상 동작해야 함. 기존 함수 삭제 금지.

## 이유와 대안
- **ui LLM 자체 결정(component_tree)**: ADR-0023의 의도(화면마다 다른 구조)가 하위로 전달됨. UX plan의 `components`는
  참고용.
- **code page 골격만 LLM**: 컴포넌트/types/mock은 토큰 비용↑, 검증 복잡도↑. 골격만으로도 사용자에게 보이는 다양화
  (return JSX, 데이터 fetching, 조건부 렌더링) 확보.
- **fallback 우선(throw 아님)**: MVP 단계에서 LLM 다운이 사용자 작업을 막으면 안 됨. 추후 LLM 안정화되면 fallback
  폐기 검토.
- 대안(완전 LLM, page+components+types+mock 모두): 토큰 비용·검증 비용↑. 보류.
- 대안(UX plan components → tree 매핑): 다양성 부족. 기각.

## 영향
- 0011/0012는 "fallback + 레거시 테스트 호환"으로 격하. 신규 에이전트는 두 단계 모두 LLM.
- `DummyLLMAdapter`에 신규 스키마 fixture 추가 필요.
- LLM 페이지 골격은 우리가 `templates.page_path` 로 재계산한 경로에 배치 (LLM이 path 무시). LLM 응답이
  우리 경로와 다르면 fallback.
- 하위 `review_agent`/`handoff_agent`는 그대로 rule-based.
- 토큰 비용↑(LLM 호출 1→2회 추가). UX 단계 대비 출력 토큰 큼 → temperature 0.2·response_format 유지.