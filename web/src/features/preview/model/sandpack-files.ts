import type { ScreenLayout, ScreenState } from "@/shared/types";

export interface PreviewFile {
  code: string;
}

export type PreviewFiles = Record<string, PreviewFile>;

/**
 * 화면 레이아웃 + State Matrix 에서 자급자족 Sandpack 프리뷰 파일을 생성 (ADR-0015).
 * - component_tree 를 라벨 박스로 렌더
 * - default/loading/empty/error 토글로 State Matrix 체감
 *
 * 보안: 모든 동적 문자열은 JSON.stringify 로 JS 문자열 리터럴화해 JSX string expression
 * `{<리터럴>}` 안에 주입 — `{`, `}`, `<`, `>`, 개행, 제어문자에 의한 JSX/JS 인젝션·파손 차단.
 */
export function buildSandpackFiles(layout: ScreenLayout, state?: ScreenState): PreviewFiles {
  return {
    "/App.tsx": { code: appCode(layout, state) },
    "/styles.css": { code: stylesCode() },
  };
}

function appCode(layout: ScreenLayout, state?: ScreenState): string {
  const tree = layout.component_tree;
  // 각 컴포넌트를 안전한 JSX string expression 으로 렌더
  const treeEntries = tree.length
    ? tree.map((c) => `      <div className="block">{${JSON.stringify(c)}}</div>`).join("\n")
    : '      <div className="block empty-block">{"(컴포넌트 없음)"}</div>';

  // State Matrix 메시지를 JSON 객체로 안전하게 임베드
  const statesObj = JSON.stringify({
    loading: state?.loading ?? "로딩 중",
    empty: state?.empty ?? "데이터가 없습니다",
    error: state?.error ?? "오류가 발생했습니다",
  });
  const titleLit = JSON.stringify(layout.screen);

  return `import React, { useState } from "react";
import "./styles.css";

const STATES = ${statesObj};

export default function App() {
  const [s, setS] = useState("default");
  return (
    <div className="app">
      <h1>{${titleLit}}</h1>
      <label className="toggle">
        상태:
        <select value={s} onChange={(e) => setS(e.target.value)}>
          <option value="default">default</option>
          <option value="loading">loading</option>
          <option value="empty">empty</option>
          <option value="error">error</option>
        </select>
      </label>
      <div className={"layout " + s}>
${treeEntries}
      </div>
      {s === "loading" && <div className="overlay">⏳ {STATES.loading}</div>}
      {s === "empty" && <div className="overlay empty">{STATES.empty}</div>}
      {s === "error" && <div className="overlay error">⚠ {STATES.error}</div>}
    </div>
  );
}
`;
}

function stylesCode(): string {
  return `body { margin: 0; font-family: system-ui, sans-serif; }
.app { padding: 16px; }
h1 { font-size: 18px; margin: 0 0 12px; }
.toggle { display: block; margin-bottom: 12px; font-size: 13px; }
.layout { display: flex; flex-direction: column; gap: 8px; }
.layout.loading .block { background: #e5e7eb; color: transparent; }
.layout.empty .block { opacity: 0.3; }
.block { border: 1px solid #d1d5db; border-radius: 8px; padding: 20px; text-align: center; color: #374151; min-height: 24px; }
.empty-block { color: #9ca3af; }
.overlay { margin-top: 12px; padding: 12px; border-radius: 8px; background: #f3f4f6; }
.overlay.empty { background: #fef3c7; color: #92400e; }
.overlay.error { background: #fee2e2; color: #991b1b; }
`;
}
