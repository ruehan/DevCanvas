import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { GenerationForm } from "./generation-form";
import type { GenerationRequest } from "@/shared/types";

describe("GenerationForm", () => {
  it("폼 필드와 제출 버튼을 렌더한다", () => {
    render(<GenerationForm onSubmit={() => {}} />);
    expect(screen.getByLabelText("프롬프트")).toBeInTheDocument();
    expect(screen.getByLabelText("화면 유형")).toBeInTheDocument();
    expect(screen.getByLabelText("디자인 톤")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "생성" })).toBeInTheDocument();
  });

  it("제출 시 폼 값을 onSubmit 으로 넘긴다", () => {
    let captured: GenerationRequest | undefined;
    render(<GenerationForm onSubmit={(r) => (captured = r)} />);
    const prompt = screen.getByLabelText("프롬프트");
    fireEvent.change(prompt, { target: { value: "고객 관리" } });

    const form = screen.getByRole("form", { name: "UI 생성 요청 폼" });
    fireEvent.submit(form);

    expect(captured).toBeDefined();
    expect(captured?.prompt).toBe("고객 관리");
    expect(captured?.screen_type).toBe("dashboard");
  });
});
