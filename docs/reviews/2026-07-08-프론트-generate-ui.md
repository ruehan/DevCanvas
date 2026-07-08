# 리뷰 기록 — 프론트 입력 UI + 결과 뷰 + /generations 연동
- 날짜: 2026-07-08
- 브랜치: feat/frontend-generate-ui
- 최종 판정: 통과 (2라운드)

## 1라운드
- 판정: 수정 필요
- 검증: verify-all.sh EXIT 0. api ruff/mypy strict/pytest. web tsc/lint/vitest 17개.
- 지적사항:
  - [P1-1] CORS 미들웨어 회귀 테스트 없음.
  - [P2-1] CORS origins 환경 분리 없음(하드코딩 ["*"]).
  - [P2-2] shared/types barrel 부재 → deep import.
  - [P2-3] reducer error 케이스 success 와 비대칭.
  - [P2-4] WAI-ARIA Tabs 풀 패턴 불완전.
  - [P2-5] fetch 타임아웃/AbortController 없음.
  - [P2-6] key={i}/{t} 중복 위험.
  - [P2-7] web/.env.example 부재.
- 반영: 커밋 4181eef, b2fc4d3.

## 2라운드
- 판정: 통과 (사소한 보완 권장)
- 검증: verify-all.sh EXIT 0. api ruff/mypy strict(46파일)/pytest 101개(드CORS 테스트). web tsc/lint/vitest 17개.
- 신규 결함: 없음
- 보완(P-A/B) 즉시 반영: error 가드 대칭 테스트, ADR-0014 CORS origins 설명 갱신.

### 1라운드 반영 상세
- P1-1: tests/test_main.py test_cors_allows_dev_origin(preflight OPTIONS, allow-origin 단정).
- P2-1: settings.cors_origins(list[str], 기본 ["*"]). main.py allow_origins=settings.cors_origins. .env.example DEVCANVAS_CORS_ORIGINS.
- P2-2: shared/types/index.ts barrel, 13파일 `@/shared/types` 통일.
- P2-3: reducer error 가드(loading 시만 수용, success 와 대칭).
- P2-6: ReviewPanel/ExportPanel key 안정화.
- P2-7: web/.env.example 추가.

### 이월(P2-4/5, milestone #7 Sandpack 진입 시)
- WAI-ARIA Tabs 풀 패턴(tabpanel/aria-controls/roving tabindex).
- fetch AbortController/타임아웃. 더미 파이프라인 수초 응답이라 현재 위험 낮음, 실제 LLM 연동 시 처리.

## 커밋 내역
- e4318b6 docs(adr): 프론트 FSD 및 generations 연동(0014)
- b2bb1d1 feat(api): CORS 미들웨어 추가(프론트 연동)
- b78f896 feat(web): 입력 폼·결과 탭 뷰·generations API 연동 추가
- 4181eef test(api): CORS 회귀 테스트 추가 및 cors_origins 설정화
- b2fc4d3 refactor(web): 1라운드 반영 — types barrel·import 통일·reducer error 가드·key 안정화·.env.example
- (보완 커밋: error 가드 테스트 + ADR 갱신)
