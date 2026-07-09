import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StudioCanvas } from "./studio-canvas";
import type { GenerationResult } from "@/shared/types";

const result = {
  input: { prompt: "x" },
  requirement: { features: [], users: [], screens: [], data_entities: [] },
  ux_plan: {
    screens: [],
    flows: [],
    states: {},
  },
  design_system: { tokens: { colors: {}, spacing: {}, radius: {}, typography: {}, shadows: {} } },
  ui: { layouts: [] },
  code: [],
  review: [],
  handoff: { file_tree: [], install_commands: [], todos: [], guide_md: "" },
} as unknown as GenerationResult;

describe("StudioCanvas", () => {
  it("empty 상태 플레이스홀더", () => {
    render(<StudioCanvas phase="empty" result={null} />);
    expect(screen.getByText("프롬프트로 시작하세요")).toBeInTheDocument();
  });

  it("loading 상태 스켈레톤", () => {
    const { container } = render(<StudioCanvas phase="loading" result={null} />);
    expect(container.querySelectorAll(".skeleton").length).toBeGreaterThan(0);
  });

  it("ready 상태 결과 뷰어", () => {
    render(<StudioCanvas phase="ready" result={result} />);
    // ResultViewer 탭 중 하나가 보여야
    expect(screen.getByRole("tab", { name: /Preview/ })).toBeInTheDocument();
  });
});
