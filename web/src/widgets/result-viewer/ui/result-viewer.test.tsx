import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ResultViewer } from "./result-viewer";
import type { GenerationResult } from "@/shared/types";

const sample = {
  input: { prompt: "x" },
  requirement: { features: [], users: [], screens: [], data_entities: [] },
  ux_plan: {
    screens: [
      {
        name: "고객 목록",
        purpose: "조회",
        kind: "list",
        components: ["DataTable"],
        data_columns: [],
        filters: [],
        actions: [],
      },
    ],
    flows: [],
    states: {
      "고객 목록": {
        loading: "skeleton",
        empty: "없음",
        error: "재시도",
        permission: "권한",
        mobile: "카드",
      },
    },
  },
  design_system: {
    tokens: { colors: { primary: "#000" }, spacing: {}, radius: {}, typography: {}, shadows: {} },
  },
  ui: { layouts: [{ screen: "고객 목록", layout: "표", kind: "list", component_tree: ["DataTable"] }] },
  code: [{ path: "app/customer/page.tsx", content: "export default () => null;", language: "tsx" }],
  review: [{ severity: "P1", category: "state", message: "상태 누락" }],
  handoff: { file_tree: ["app/customer/page.tsx"], install_commands: [], todos: [], guide_md: "" },
} as unknown as GenerationResult;

describe("ResultViewer", () => {
  it("7개 탭을 렌더한다", () => {
    render(<ResultViewer result={sample} />);
    expect(screen.getByRole("tab", { name: /Preview/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Export/ })).toBeInTheDocument();
  });

  it("Review 탭 클릭 시 findings 표시", () => {
    render(<ResultViewer result={sample} />);
    const reviewTab = screen.getByRole("tab", { name: /Review/ });
    fireEvent.click(reviewTab);
    expect(screen.getByText("상태 누락")).toBeInTheDocument();
  });
});
