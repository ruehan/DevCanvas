# DevCanvas 개발 계획

- 날짜: 2026-07-01
- 상태: 계획 (구현 착수 전)

## 한 문장 성공 기준
개발자가 서비스 설명 프롬프트 + 폼 입력을 넣으면, Next.js + Tailwind + shadcn/ui 기반의
**화면 구조, 상태별 UI(loading/empty/error), 디자인 토큰, 복사 가능한 React 코드, 구현 가이드**를
1회 생성으로 받을 수 있다.

## 기술 스택
| 영역 | 선택 | 비고 |
|---|---|---|
| 프론트 | Next.js App Router + TS + Tailwind + shadcn/ui | MVP 출력 스택과 동일 → 자기 자신에서 렌더/검증 |
| 코드 프리뷰 | Sandpack | 클라이언트 컴포넌트 한정, ADR-0004 |
| 백엔드 | Python FastAPI | 제로원 표준, 도메인 모듈 구조 |
| DB | PostgreSQL + Redis | 프로젝트/히스토리 + 작업 큐 |
| AI | GLM 5 Turbo (텍스트) | 어댑터로 추상화, ADR-0005 |
| 검증 | tsc + ESLint + Prettier + Lighthouse CI | 생성 코드 자동 품질 보증 |

## MVP 범위
**포함**: 프롬프트 + 폼 입력 → UI 구조 → 상태 매트릭스 → 디자인 토큰 → React 코드 → Sandpack 프리뷰 → 코드 복사/ZIP → UI 리뷰. 익명 세션(계정 없음, ADR-0003).

**제외 (Phase 2+)**: GitHub 연동, 코드베이스 분석, 협업, 결제, 팀 권한.

**도메인 집중**: 관리자 페이지 / SaaS 대시보드 / 내부툴 UI.

## 아키텍처
```
브라우저 (Next.js, FSD)
  ├── 입력: 프롬프트 + 폼(화면유형/서비스/역할/데이터/톤/스택)
  ├── 결과 뷰 탭: Preview | Screens | States | DesignSystem | Code | Review | Export
  └── Sandpack (생성 코드 실시간 렌더, client-only)

FastAPI (도메인 모듈)
  ├── projects, generations  (라우터 얇게, service에 로직)
  ├── pipeline/  ← 7단계 에이전트 오케스트레이션
  │     requirement → ux_planner → design_system → ui_generator
  │     → code_generator → review → handoff
  ├── validators/  ← tsc/eslint/build 검증 + 재생성 루프
  └── adapters/glm.py  ← GLM 5 Turbo 호출 추상화

PostgreSQL: project, generation, design_token, screen, state, code_file
Redis: 비동기 파이프라인 작업 큐
Object Storage: ZIP 산출물, 스크린샷
```

## 데이터 모델 (초안)
- `Project`: 설정(스택/톤/도메인), 익명 세션 키
- `Generation`: 1회 실행, 단계별 상태 + 중간 산출물(JSON)
- `DesignSystem`: 토큰(colors/spacing/radius/typography/components)
- `Screen[]`: 목적 + 컴포넌트 트리
- `StateMatrix`: screen × {default/loading/empty/error/permission/mobile}
- `CodeFile[]`: 경로/내용/언어 (Export 트리)
- `Review`: 린트 결과 + UX 리뷰 항목

## 작업 순서 (TDD 마일스톤)
1. **레포 세팅** — 모노레포(`web/`, `api/`), verify.sh(검증 센서), FSD/도메인 구조. ADR-0001.
2. **GLM 어댑터 + 파이프라인 뼈대** — 7단계 에이전트 인터페이스, end-to-end 목업 테스트.
3. **디자인 시스템 에이전트** — 토큰 생성(JSON/tokens.ts/tailwind.config). 독립적·검증 쉬움 → 선행.
4. **UX/스크린/상태매트릭스 에이전트** — 화면 목록 + State Matrix JSON.
5. **코드 생성 에이전트 + 검증 루프** — shadcn/ui 기반 컴포넌트/페이지, tsc/eslint 실패시 재생성.
6. **프론트 입력 UI + 결과 뷰(탭)** — FSD.
7. **Sandpack 통합** — 생성 코드 실시간 렌더.
8. **UI 리뷰 에이전트 + Export(ZIP)**.
9. **E2E**: 프롬프트 → 전 파이프라인 → ZIP 산출물.

## 리스크
- **GLM API**: 키/엔드포인트/레이트리밋 — 어댑터로 추상화, 더미로 선행(ADR-0005).
- **Sandpack 한계**: Next.js 서버컴포넌트 미지원 → client-only 프리뷰(ADR-0004).
- **검증 루프 비용**: 재생성 횟수/비용 정책 — 향후 ADR.
- **AI 스타일 범람**: 도메인/브랸드 톤 반영 프롬프트 설계 필요.
