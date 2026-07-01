# DevCanvas

개발자 중심 AI UI 설계/구현 플랫폼.

> 기획만 입력하면 구현 가능한 UI(화면 구조·상태별 UI·디자인 토큰·React 코드·구현 가이드)를 한 번에 생성한다.

## 핵심 가치
- **예쁜 것보다 구현 가능한 것** — 디자인 이미지가 아니라 붙일 수 있는 코드.
- **한 화면보다 전체 상태** — loading/empty/error/permission/mobile 상태 매트릭스.
- **일관된 디자인 시스템** — 토큰 자동 생성, AI 스타일 최소화.
- **결과물은 코드와 연결** — "이 파일에 이 컴포넌트를 넣으세요"까지.

## MVP 범위
화면 유형: **관리자 페이지 / SaaS 대시보드 / 내부툴 UI** (좁게).

출력 스택: Next.js App Router + TypeScript + Tailwind + shadcn/ui.

## 구조
모노레포.
- `api/` — FastAPI 백엔드 (도메인 모듈 구조). `cd api && uv sync && uv run uvicorn devcanvas_api.main:app`
- `web/` — Next.js 프론트엔드 (FSD). `cd web && pnpm install && pnpm dev`

## 검증
```bash
bash scripts/verify-all.sh   # api/ + web/ 모두
bash ~/.config/opencode/scripts/verify.sh api/   # 백엔드만
bash ~/.config/opencode/scripts/verify.sh web/   # 프론트만
```

## 문서
- 계획: [docs/plan.md](docs/plan.md)
- 결정: [docs/decisions/](docs/decisions/)
- 기획 원안: [DevCanvas.md](DevCanvas.md)
