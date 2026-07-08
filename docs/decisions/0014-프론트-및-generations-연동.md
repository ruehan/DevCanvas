# 0014. 프론트엔드 FSD 구조 및 /generations 연동
- 상태: 채택
- 날짜: 2026-07-08

## 배경
지금까지 백엔드 파이프라인만 구축. milestone #6 로 처음으로 사용자에게 보이는 산출(입력→결과)
을 만든다. CONVENTIONS.md 의 FSD 구조를 실제 코드에 적용하고, 백엔드 `/generations` 와 연동.

## 결정
- **FSD 레이어 배치**:
  - `app/` — Next.js App Router 진입(page.tsx 가 폼+결과 위젯 조립). app 레이어.
  - `widgets/result-viewer/` — 결과 탭 복합 뷰(Preview/Screens/States/DesignSystem/Code/Review/Export).
  - `features/generate-ui/` — "UI 생성" 사용자 액션. ui(폼) + model(reducer 상태기계).
  - `shared/` — api(generations 클라이언트), config(env), types(백엔드 스키마 미러), lib.
  - `entities/`, `pages/` — 현재 사용 안 함(Next 라우트가 app/ 에서 처리).
- **상태 관리**: `useReducer` 기반 순수 reducer(idle/loading/success/error). 부작용(fetch)은
  컴포넌트/effects 에서, 순수 로직은 테스트 가능.
- **API 클라이언트**: `shared/api/generations.ts` 의 `createGeneration(req)`. base URL 은
  `NEXT_PUBLIC_API_BASE_URL`(기본 http://localhost:8000).
- **백엔드 CORS**: FastAPI `CORSMiddleware` 추가(dev 에서 Next 3000 → API 8000 허용).
- **테스트 환경**: vitest environment 를 jsdom 으로 전환, @testing-library/react 추가.
  순수 로직(reducer/api/mapper)은 단위 테스트, 컴포넌트는 렌더 스모크 테스트.

## 이유와 대안
- FSD: CONVENTIONS 표준. eslint boundary(0001/이전)가 이미 강제 중.
- useReducer 순수 reducer: 비동기(fetch)와 상태 전이를 분리해 테스트 용이.
  대안(React Query/SWR): 과한 추상. MVP 는 로컬 상태로 충분, 향후 교체 가능.
- jsdom: React 컴포넌트 테스트에 필요. 기존 node 환경 테스트도 jsdom 에서 동작.

## 영향
- web/ 에 features/widgets/shared 가 본격 도입. FSD boundary 가 실제 코드에 적용됨.
- 백엔드 main.py 에 CORS 미들웨어 추가(모든 origin 허용 — dev 용, 프로덕션은 별도 제한 필요).
- 타입은 백엔드 Pydantic 스키마를 수동 미러. 향후 코드생성(OpenAPI → TS) 도입 여지.
- Sandpack 프리뷰(milestone #7)는 아님 — Preview 탭은 코드 표시로 대체(향후 Sandpack 교체).
