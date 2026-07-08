## 2026-07-08 — 핸드오프 정제(ADR-0009 갭 해소)
- 브랜치: feat/handoff-rule-based
- 한 일: handoff_agent 를 규칙 기반으로 전환(ADR-0016). build_handoff(code, review) — file_tree(코드 경로 정렬), install_commands(컴포넌트 스텁→외부 의존 tanstack/recharts 검출, shadcn 기본 제공 제외), TODO(review P1 + mock 교체 + 스텁 구현), guide_md. 오케스트레이터 토큰 병합을 handoff 호출 전으로 이동 → 토큰 파일 5종이 file_tree/guide 에 반영(ADR-0009 갭 실제 해소). naming 공용 모듈로 변환 통일.
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 50파일/pytest 108개), web(변경 없음)
- 리뷰: 통과 3라운드 — 상세: docs/reviews/2026-07-08-핸드오프-정제.md
- 가정: review_agent 는 토큰(결정적 산출) 린트 불필요 → 병합 전 code 사용. 이제 7에이전트 전부 규칙 기반(requirement만 LLM/더미).
- 관련 결정: docs/decisions/0016 (핸드오프 규칙 기반)

## 2026-07-08 — Sandpack 통합(milestone #7)
- 브랜치: feat/sandpack-preview
- 한 일: Preview 탭 Sandpack 실시간 프리뷰(ADR-0015). 자급자족 구조 프리뷰 — component_tree 박스 렌더 + State Matrix(default/loading/empty/error) 인터랙티브 토글. buildSandpackFiles 순수 함수(JSON.stringify 로 코드 인젝션 차단). next/dynamic ssr:false 로 로드. @codesandbox/sandpack-react 추가.
- 검증: verify-all.sh EXIT 0 — web(tsc/lint/vitest 27개), api(변경 없음)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-08-sandpack-프리뷰.md
- 가정: 생성 page.tsx(@/alias+shadcn 의존)은 Sandpack 직접 실행 불가 → 구조 프리뷰로 대체. 실제 shadcn 시각 프리뷰는 향후 Storybook/WebContainers. permission/mobile 토글은 향후 스토리.
- 관련 결정: docs/decisions/0015 (Sandpack 자급자족 프리뷰), 0004 (Sandpack 기반)

## 2026-07-08 — 프론트 입력 UI + 결과 뷰 + /generations 연동
- 브랜치: feat/frontend-generate-ui
- 한 일: milestone #6. FSD 구조(app/widgets/features/shared) 적용. shared/types(스키마 미러), shared/api(createGeneration), shared/config(env lazy). features/generate-ui(useReducer 순수 reducer + 폼). widgets/result-viewer(7탭: Preview/Screens/States/DesignSystem/Code/Review/Export). app/page.tsx 조립. 백엔드 CORS(ADR-0014, cors_origins 설정화). vitest jsdom + @testing-library/react.
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 46파일/pytest 101개, CORS 테스트), web(tsc/lint/vitest 17개)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-08-프론트-generate-ui.md
- 가정: Sandpack 프리뷰(#7) 전이라 Preview 탭은 코드 표시로 대체. WAI-ARIA 풀 패턴·fetch 타임아웃은 #7에서. TS 타입은 백엔드 수동 미러(향후 OpenAPI→TS 여지).
- 관련 결정: docs/decisions/0014 (프론트 FSD·generations 연동)

## 2026-07-08 — 리뷰 에이전트 상세 구현
- 브랜치: feat/review-agent
- 한 일: review_agent 를 규칙 기반 린트로 전환(ADR-0013). `pipeline/review/{checks,reviewer}.py` — check_state(P1)/check_any_type(P1, `: any`/`as any`/`<any>`)/check_a11y(P2)/check_component_stubs(P2)/check_mock_usage(P2). run_review 가 모든 파일×체크 집계. 패턴매칭 기반(위양성/위음성 한계, 향후 AST).
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 46파일/pytest 102개), web(변경 없음 통과)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-08-리뷰-에이전트.md
- 가정: LLM 맥락 판단(UX 흐름 등)은 향후 추가. 현재는 "반드시 잡을 것" 보장.
- 관련 결정: docs/decisions/0013 (리뷰 에이전트 규칙 기반 린트)

## 2026-07-08 — 코드 생성 에이전트 상세 구현
- 브랜치: feat/code-generator-agent
- 한 일: code_generator_agent 를 규칙 기반 스켈레톤으로 전환(ADR-0012). `pipeline/code/{generator,templates}.py` — page.tsx(화면수) + 컴포넌트 스텁(유니크) + lib/types.ts + lib/mock-data.ts. ScreenLayout.kind 도입(ui→code 정합). 경로 규약: dashboard/list/detail, 한글 라벨 역매핑(고객→customer), 엔티티 dedup, 폴백 "항목 목록"→item. 정합 회귀망(round-trip/역방향 stub/no-duplicate).
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 42파일/pytest 88개), web(변경 없음 통과)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-08-코드-생성-에이전트.md
- 가정: 컴포넌트 본체는 TODO(향후 LLM/검증루프). page→컴포넌트 경로 정합을 테스트로 고정(0011 교훈 반영).
- 관련 결정: docs/decisions/0012 (코드 생성 에이전트 규칙 기반 스켈레톤)

## 2026-07-08 — UI 생성 에이전트 상세 구현
- 브랜치: feat/ui-generator-agent
- 한 일: ui_generator_agent 를 규칙 기반으로 전환(ADR-0011). `pipeline/ui/{generator,templates}.py` — 종류별 layout(공간 배치)·component_tree(렌더 순서). build_ui_generation: UXPlan.screens 와 1:1 ScreenLayout. 정합 규칙: component_tree ⊆ screen.components, layout 토큰 == component_tree(회귀망으로 고정).
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 38파일/pytest 72개), web(변경 없음 통과)
- 리뷰: 통과 4라운드 — 상세: docs/reviews/2026-07-08-ui-생성-에이전트.md
- 가정: 종류별 고정 템플릿(다양성 없음)은 의도적 — code_generator 입력으로 충분. LLM 정제(브랜드 맞춤 변형)는 향후.
- 관련 결정: docs/decisions/0011 (UI 생성 에이전트 규칙 기반)

## 2026-07-01 — UX/스크린/상태매트릭스 에이전트 상세 구현
- 브랜치: feat/ux-planner-agent
- 한 일: ux_planner_agent 를 규칙 기반으로 전환(ADR-0010). `pipeline/ux/{planner,templates}.py` — ScreenKind(list/detail/dashboard) 도입, 종류별 components/state 템플릿(엔티티 매개변수화). build_ux_plan: screen_type 주화면(DASHBOARD만 대시보드) + 각 data_entity×{list,detail}, 엔티티별 flows. State Matrix 5상태(loading/empty/error/permission/mobile) 전 화면 완결 보장.
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 34파일/pytest 59개), web(변경 없음 통과)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-01-ux-플래너-에이전트.md
- 가정: requirement_agent(1단계)는 여전히 LLM/더미 — 그 data_entities 소비. _entity_label 하드코딩 매핑(미지정 패스스루), 향후 LLM/매핑 확장.
- 관련 결정: docs/decisions/0010 (UX 플래너 규칙 기반)

## 2026-07-01 — 디자인 토큰 산출물 파이프라인 연결
- 브랜치: feat/design-export-wiring
- 한 일: exporter.to_code_files 로 토큰 파일 5종(tokens.ts/tailwind.config.json/tokens/design.json/styles/tokens.css/docs/design.md)을 CodeFile 로 생성, orchestrator 에서 앱 코드와 병합해 GenerationResult.code 에 포함(ADR-0009). 경로 충돌 가드(_merge_code: 토큰 우선 + 경고 로깅, RESERVED_TOKEN_PATHS).
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 30파일/pytest 41개), web(변경 없음 통과)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-01-디자인-토큰-산출물-파이프라인-연결.md
- 가정: handoff_agent 가 병합 전 code 를 받아 file_tree·install·guide 에 토큰 파일이 미반영 → handoff 정제 시 해결(ADR-0009에 이관 명시).
- 관련 결정: docs/decisions/0009 (토큰 산출물 코드 연결 위치)

## 2026-07-01 — 디자인 시스템 에이전트 상세 구현
- 브랜치: feat/design-system-agent
- 한 일: design_system_agent 를 규칙 기반(톤 프리셋)으로 전환(ADR-0008). `pipeline/design/presets.py`(5톤 B2B/minimal/enterprise/startup/friendly) + `exporter.py`(tokens.ts/tailwind.config.json/design.json/tokens.css/design.md 5포맷, 순수함수). DesignTokens.shadows 추가. Tone StrEnum 도입 + 양 스키마(GenerationInput·GenerationRequest) 대소문자 무관 정규화.
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 30파일/pytest 36개), web(변경 없음 통과)
- 리뷰: 통과 3라운드 — 상세: docs/reviews/2026-07-01-디자인시스템-에이전트.md
- 가정: LLM 정제(브랜드 키워드→맞춤 색상)는 향후 확장. exporter 산출을 GenerationResult.code/handoff 에 연결하는 것은 다음 단계.
- 관련 결정: docs/decisions/0008 (디자인 시스템 에이전트 규칙 기반)

## 2026-07-01 — GLM 어댑터 + 파이프라인 뼈대
- 브랜치: feat/glm-adapter-pipeline
- 한 일: `LLMAdapter` 포트(Protocol) + `DummyLLMAdapter`(deep copy 격리) + `GLMAdapter`(stub) 구현. 7단계 에이전트(requirement/ux_planner/design_system/ui_generator/code_generator/review/handoff) + orchestrator로 end-to-end 파이프라인 구성. `generations` 도메인(FastAPI 도메인 모듈 구조)에 `POST /generations` 엔드포인트 추가 — 더미로 완전한 GenerationResult 생산.
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 25파일/pytest 11개), web(변경 없음 통과)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-01-glm-어댑터-파이프라인.md
- 가정: GLM 실구현체는 키 확보 후 추가(현재 stub). 응답 검증/재시도 정책은 ADR-0007 보류로 3단계 GLM 스파이크 후 확정.
- 관련 결정: docs/decisions/0005 (GLM 어댑터 추상화, 부분 대체), 0006 (파이프라인·어댑터 위치), 0007 (포트 시그니처·응답검증정책)

## 2026-07-01 — 레포 세팅
- 브랜치: feat/repo-setup
- 한 일: 모노레포 뼈대 세팅. `api/`(FastAPI 도메인 모듈 구조 + uv/ruff/mypy strict/pytest)와 `web/`(Next.js 14 App Router + TS + Tailwind v3 + FSD + vitest) 생성. 루트 `scripts/verify-all.sh` 래퍼 추가. web에 `eslint-plugin-boundaries`로 FSD 레이어 방향(upward import) 자동 강제.
- 검증: verify-all.sh EXIT 0 — api(ruff/mypy strict 10파일/pytest 3개), web(tsc/next lint/vitest 1개)
- 리뷰: 통과 2라운드 — 상세: docs/reviews/2026-07-01-레포세팅.md
- 가정: shadcn/ui 컴포넌트는 실제 기능에서 필요할 때 추가(스캐폴드엔 미포함). FSD 규칙 #2/#3 강제는 향후 슬라이스 단위로 확장.
- 관련 결정: docs/decisions/0001 (기술스택·아키텍처), 0004 (Sandpack), 0005 (GLM 어댑터 추상화)
