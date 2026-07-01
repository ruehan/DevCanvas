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
