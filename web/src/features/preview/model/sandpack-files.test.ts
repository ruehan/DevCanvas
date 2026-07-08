import { describe, it, expect } from "vitest";
import { buildSandpackFiles } from "./sandpack-files";
import type { ScreenLayout, ScreenState } from "@/shared/types";

const layout: ScreenLayout = {
  screen: "고객 목록",
  layout: "FilterBar 상단 → DataTable 본문 → Pagination 하단",
  kind: "list",
  component_tree: ["FilterBar", "DataTable", "Pagination"],
};

const state: ScreenState = {
  loading: "테이블 skeleton",
  empty: "고객이 없습니다",
  error: "로드 실패",
  permission: "권한 필요",
  mobile: "카드 전환",
};

describe("features/preview/model/sandpack-files", () => {
  it("App.tsx 와 styles.css 파일을 생성한다", () => {
    const files = buildSandpackFiles(layout, state);
    expect(files["/App.tsx"]).toBeDefined();
    expect(files["/styles.css"]).toBeDefined();
  });

  it("component_tree 가 App 코드에 반영된다", () => {
    const code = buildSandpackFiles(layout, state)["/App.tsx"]?.code ?? "";
    expect(code).toContain("FilterBar");
    expect(code).toContain("DataTable");
    expect(code).toContain("Pagination");
  });

  it("State Matrix 메시지가 코드에 반영된다", () => {
    const code = buildSandpackFiles(layout, state)["/App.tsx"]?.code ?? "";
    expect(code).toContain("고객이 없습니다");
    expect(code).toContain("로드 실패");
  });

  it("화면 이름이 제목에 반영된다", () => {
    const code = buildSandpackFiles(layout, state)["/App.tsx"]?.code ?? "";
    expect(code).toContain("고객 목록");
  });

  it("다른 레이아웃은 다른 코드를 생성한다", () => {
    const a = buildSandpackFiles(layout, state)["/App.tsx"]?.code ?? "";
    const other: ScreenLayout = { ...layout, component_tree: ["KpiCard", "Chart"] };
    const b = buildSandpackFiles(other, state)["/App.tsx"]?.code ?? "";
    expect(a).not.toBe(b);
  });

  it("빈 component_tree 도 깨지지 않는다", () => {
    const code = buildSandpackFiles({ ...layout, component_tree: [] }, state)["/App.tsx"]?.code ?? "";
    expect(code).toContain("고객 목록");
  });
});
