# FSD 레이어 구조

이 디렉터리는 Feature-Sliced Design(CONVENTIONS.md)을 따른다.

```
src/
  app/        Next.js App Router 진입점(전역 스타일·레이아웃). FSD app 레이어에 해당.
  pages/      (예정) 별도 페이지 슬라이스 — 현재는 app/ 라우트가 페이지 역할.
  widgets/    (예정) 복합 UI 블록
  features/   (예정) 사용자 액션 단위
  entities/   (예정) 비즈니스 도메인 객체
  shared/     공용 유틸·타입·상수 (현재 lib만 존재)
```

불변 규칙(CONVENTIONS.md):
1. 한 레이어는 자기보다 아래 레이어만 import.
2. 같은 레이어의 슬라이스는 서로 import하지 않는다.
3. 슬라이스 외부에서는 public API(index.ts)로만 접근.

강제(센서):
- 규칙 #1(레이어 방향)은 ESLint `eslint-plugin-boundaries`(`boundaries/dependencies`)로
  자동 검사한다. `.eslintrc.json` 참조. 거꾸로 import(upward)하면 `pnpm lint`가 실패한다.
- 규칙 #2(동일 레이어 슬라이스 간 import 금지)·#3(public API)은 현재 센서 미구현 →
  향후 슬라이스 단위 element 정의로 확장 예정.

Next.js App Router와 FSD의 조정: 라우트 파일(`src/app/**`)은 FSD app 레이어의 일부로 본다.
비즈니스 로직·컴포넌트는 pages/widgets/features/entities/shared에 둔다.
