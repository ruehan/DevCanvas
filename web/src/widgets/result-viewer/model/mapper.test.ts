import { describe, it, expect } from "vitest";
import { buildTabs } from "./mapper";
import type { GenerationResult } from "@/shared/types/schemas";

const sample = {
  input: { prompt: "x" },
  requirement: { features: ["조회"], users: [], screens: [], data_entities: [] },
  ux_plan: {
    screens: [
      {
        name: "고객 목록",
        purpose: "조회",
        kind: "list",
        components: ["DataTable"],
        data_columns: ["고객명"],
        filters: ["상태"],
        actions: ["보기"],
      },
    ],
    flows: ["로그인 → 목록"],
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
    tokens: {
      colors: { primary: "#000" },
      spacing: { md: "16px" },
      radius: {},
      typography: {},
      shadows: {},
    },
  },
  ui: { layouts: [{ screen: "고객 목록", layout: "표", kind: "list", component_tree: ["DataTable"] }] },
  code: [{ path: "app/customer/page.tsx", content: "x", language: "tsx" }],
  review: [{ severity: "P1", category: "state", message: "상태 누락" }],
  handoff: {
    file_tree: ["app/customer/page.tsx"],
    install_commands: [],
    todos: ["API 교체"],
    guide_md: "# 가이드",
  },
} as unknown as GenerationResult;

describe("widgets/result-viewer/mapper", () => {
  it("7개 탭을 생성한다", () => {
    const tabs = buildTabs(sample);
    const labels = tabs.map((t) => t.label);
    expect(labels).toEqual([
      "Preview",
      "Screens",
      "States",
      "Design System",
      "Code",
      "Review",
      "Export",
    ]);
  });

  it("Review 탭은 findings 수를 뱃지로 갖는다", () => {
    const tabs = buildTabs(sample);
    const review = tabs.find((t) => t.label === "Review");
    expect(review?.badge).toBe(1);
  });

  it("Code 탭은 파일 수를 뱃지로 갖는다", () => {
    const tabs = buildTabs(sample);
    const code = tabs.find((t) => t.label === "Code");
    expect(code?.badge).toBe(1);
  });

  it("결과가 없는 탭도 비어있는 구조로 생성된다", () => {
    const empty = { input: { prompt: "" } } as unknown as GenerationResult;
    const tabs = buildTabs(empty);
    expect(tabs).toHaveLength(7);
  });
});
