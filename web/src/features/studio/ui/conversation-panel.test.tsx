import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConversationPanel } from "./conversation-panel";

describe("ConversationPanel", () => {
  it("empty 상태에서 예시 프롬프트 칩을 렌더한다", () => {
    render(
      <ConversationPanel phase="empty" messages={[]} pendingPrompt={null} error={null} onSubmit={() => {}} />,
    );
    expect(screen.getByText("무엇을 만들까요?")).toBeInTheDocument();
    expect(screen.getByText("정기결제 SaaS 관리자 페이지")).toBeInTheDocument();
  });

  it("예시 칩 클릭 시 onSubmit 호출", () => {
    const fn = vi.fn();
    render(
      <ConversationPanel phase="empty" messages={[]} pendingPrompt={null} error={null} onSubmit={fn} />,
    );
    fireEvent.click(screen.getByText("채용 플랫폼 공고 목록"));
    expect(fn).toHaveBeenCalledOnce();
    expect(fn.mock.calls[0]![0]).toContain("채용 플랫폼");
  });

  it("ready 상태에서 메시지 스레드를 렌더한다", () => {
    const messages = [
      { role: "user" as const, content: "고객 페이지 만들어줘", steps: [] },
      { role: "agent" as const, content: "생성했어요.", steps: ["요구사항 분석"] },
    ];
    render(
      <ConversationPanel phase="ready" messages={messages} pendingPrompt={null} error={null} onSubmit={() => {}} />,
    );
    expect(screen.getByText("고객 페이지 만들어줘")).toBeInTheDocument();
    expect(screen.getByText("생성했어요.")).toBeInTheDocument();
    expect(screen.getByText(/요구사항 분석/)).toBeInTheDocument();
  });
});
