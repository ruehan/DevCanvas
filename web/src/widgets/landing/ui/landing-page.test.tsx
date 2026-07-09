import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LandingPage } from "./landing-page";

describe("LandingPage", () => {
  it("히어로 제목과 CTA를 렌더한다", () => {
    render(<LandingPage />);
    expect(screen.getByText("프롬프트")).toBeInTheDocument();
    expect(screen.getByText("스튜디오에서 시작하기")).toBeInTheDocument();
  });

  it("핵심 기능 섹션 3개가 렌더된다", () => {
    render(<LandingPage />);
    expect(screen.getByText("01 — PROCESS")).toBeInTheDocument();
    expect(screen.getByText("02 — COMPLETENESS")).toBeInTheDocument();
    expect(screen.getByText("03 — OUTPUT")).toBeInTheDocument();
  });
});
