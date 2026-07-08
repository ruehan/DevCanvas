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
    expect(code).toContain("컴포넌트 없음");
  });

  it("component_tree 에 특수문자/JSX 문자가 있어도 문자열 리터럴로 안전 처리된다", () => {
    const malicious: ScreenLayout = {
      ...layout,
      component_tree: ["DataTable{alert('xss')}", "Foo</div><script>"],
    };
    const code = buildSandpackFiles(malicious, state)["/App.tsx"]?.code ?? "";
    // 위험 페이로드가 따옴표로 감싸진 JS 문자열 리터럴 안에 존재(JSON.stringify).
    // bare JSX 표현식/요소로 주입되지 않는다.
    expect(code).toContain('"DataTable{alert(\'xss\')}"');
    expect(code).toContain('"Foo</div><script>"');
    // JSX string expression 형태: {"<리터럴>"}
    expect(code).toContain('{"DataTable{alert(\'xss\')}"');
  });

  it("title 의 특수문자가 JSX 요소/표현식이 아닌 문자열 리터럴로 들어간다", () => {
    const code = buildSandpackFiles(
      { ...layout, screen: "a<b>{evil}</b>" },
      state,
    )["/App.tsx"]?.code ?? "";
    // 따옴표 안 리터럴 → 실제 <b> 요소가 아님
    expect(code).toContain('"a<b>{evil}</b>"');
    expect(code).not.toMatch(/>\s*a<b>/);
  });

  it("state 메시지에 개행이 있어도 유효한 JS 코드를 생성한다", () => {
    const multiline: ScreenState = {
      ...state,
      empty: "줄1\n줄2",
    };
    const code = buildSandpackFiles(layout, multiline)["/App.tsx"]?.code ?? "";
    // 실제 개행이 아니라 이스케이프된 \n 으로 들어가야 JS string literal 이 깨지지 않음
    expect(code).toContain("\\n");
    // { 혹은 " 로 인한 JS SyntaxError 위험: STATES 객체가 JSON.stringify 결과이므로 닫힘
    expect(code).toMatch(/const STATES = \{[\s\S]*\};/);
  });
});
