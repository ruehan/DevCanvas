# 0015. Sandpack 프리뷰는 자급자족 구조 프리뷰
- 상태: 채택
- 날짜: 2026-07-08

## 배경
ADR-0004 로 Sandpack 기반 프리뷰를 결정했으나, code_generator(0012) 산출물은
`@/components/*` 별칭과 shadcn/ui 컴포넌트(스텁)에 의존한다. Sandpack 번들러는 이 별칭과
shadcn 의존을 해석하지 못해 실제 page.tsx 를 그대로 실행하면 런타임 에러가 난다.

## 결정
- Preview 탭의 Sandpack 은 생성 page.tsx 를 직접 실행하지 않고, **자급자족(self-contained)
  구조 프리뷰 컴포넌트**를 생성해 실행한다.
- `features/preview/model/sandpack-files.ts` 의 `buildSandpackFiles(layout, state)` 가
  순수하게 Sandpack 파일 맵(`/App.tsx`, `/styles.css`)을 생성:
  - component_tree 의 각 컴포넌트를 라벨링된 박스로 렌더(공간 배치 시각화).
  - State Matrix 를 시각화하기 위해 default/loading/empty/error 토글을 App 내에 두어
    사용자가 상태별 UI 를 인터랙티브하게 확인(킬러 기능 13.1 의 체감).
- 실제 shadcn/ui 컴포넌트 시각 프리뷰는 향후 Storybook/WebContainers 등 별도 경로.

## 이유와 대안
- 자급자족 프리뷰: 의존 없이 Sandpack 에서 즉시 실행, 결정적, State Matrix 체감 가치.
- 대안(실 page.tsx 실행): 별칭/의존 해석 불가 → 번들 에러. Sandpack 에 alias/skip 처리를
  넣어도 shadcn 스텁은 본체가 없어 의미 없는 렌더. 기각.
- 대관(정적 박스 그리기, Sandpack 없이): 브라우저에서 직접 그리는 게 단순하나, ADR-0004
  "Sandpack 기반" 의도와 실제 React 코드 실행(토글 등 인터랙션) 가치를 살리기 위해 Sandpack 유지.

## 영향
- Preview 탭이 Sandpack iframe 으로 실시간 렌더. Next.js SSR 호환을 위해 Sandpack 컴포넌트는
  `next/dynamic`(ssr:false) 으로 로드.
- buildSandpackFiles 는 순수 함수(테스트 용이). 컴포넌트 트리·상태 메시지가 파일 코드에 반영.
- Sandpack 번들(~iframe)이 추가돼 프리뷰 탭 진입 시 로드 비용 발생.
