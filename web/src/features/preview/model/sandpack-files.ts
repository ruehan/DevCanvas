import type { ScreenLayout, ScreenState } from "@/shared/types";

export interface SandpackFile {
  code: string;
}

export type SandpackFiles = Record<string, SandpackFile>;

/**
 * 화면 레이아웃 + State Matrix 에서 자급자족 Sandpack 프리뷰 파일을 생성 (ADR-0015).
 * - component_tree 를 라벨 박스로 렌더
 * - default/loading/empty/error 토글로 State Matrix 체감
 */
export function buildSandpackFiles(layout: ScreenLayout, state?: ScreenState): SandpackFiles {
  return {
    "/App.tsx": { code: appCode(layout, state) },
    "/styles.css": { code: stylesCode() },
  };
}

function appCode(layout: ScreenLayout, state?: ScreenState): string {
  const tree = layout.component_tree;
  const treeEntries = tree.length
    ? tree.map((c) => `      <div className="block">${c}</div>`).join("\n")
    : "      <div className=\"block empty-block\">(컴포넌트 없음)</div>";
  const esc = (s: string) => s.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  const loading = esc(state?.loading ?? "로딩 중");
  const empty = esc(state?.empty ?? "데이터가 없습니다");
  const error = esc(state?.error ?? "오류가 발생했습니다");
  const title = esc(layout.screen);

  return `import React, { useState } from "react";
import "./styles.css";

const STATES = {
  loading: "${loading}",
  empty: "${empty}",
  error: "${error}",
};

export default function App() {
  const [s, setS] = useState("default");
  return (
    <div className="app">
      <h1>${title}</h1>
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
