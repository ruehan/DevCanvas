import { describe, it, expect } from "vitest";
import { studioReducer, initialState, type StudioState } from "./reducer";
import type { GenerationResult, Message } from "@/shared/types";

const agentMsg: Message = {
  role: "agent",
  content: "생성했어요.",
  steps: ["요구사항 분석", "UX 설계"],
};
const result = { input: { prompt: "x" } } as GenerationResult;

describe("features/studio/model/reducer", () => {
  it("submit → loading + 사용자 메시지 추가", () => {
    const state = studioReducer(initialState, { type: "submit", prompt: "고객 페이지" });
    expect(state.phase).toBe("loading");
    expect(state.messages).toHaveLength(1);
    expect(state.messages[0]!.role).toBe("user");
    expect(state.messages[0]!.content).toBe("고객 페이지");
    expect(state.pendingPrompt).toBe("고객 페이지");
  });

  it("success → ready + 에이전트 메시지·결과 저장", () => {
    const loading: StudioState = {
      ...initialState,
      phase: "loading",
      messages: [{ role: "user", content: "x", steps: [] }],
      pendingPrompt: "x",
    };
    const state = studioReducer(loading, { type: "success", agentMessage: agentMsg, result });
    expect(state.phase).toBe("ready");
    expect(state.messages).toHaveLength(2);
    expect(state.messages[1]).toEqual(agentMsg);
    expect(state.result).toBe(result);
    expect(state.pendingPrompt).toBeNull();
  });

  it("error(결과 없음) → empty 로 복귀 + 에러", () => {
    const loading: StudioState = {
      ...initialState,
      phase: "loading",
      messages: [{ role: "user", content: "x", steps: [] }],
      pendingPrompt: "x",
    };
    const state = studioReducer(loading, { type: "error", error: "boom" });
    expect(state.phase).toBe("empty");
    expect(state.error).toBe("boom");
  });

  it("error(기존 결과 있음) → ready 유지 + 에러", () => {
    const ready: StudioState = { ...initialState, phase: "ready", result };
    const state = studioReducer(ready, { type: "error", error: "boom" });
    expect(state.phase).toBe("ready");
    expect(state.error).toBe("boom");
  });

  it("sessionCreated → sessionId 저장", () => {
    const state = studioReducer(initialState, { type: "sessionCreated", sessionId: "abc" });
    expect(state.sessionId).toBe("abc");
  });

  it("reset → 초기화(새 대화)", () => {
    const state = studioReducer(
      { ...initialState, phase: "ready", sessionId: "s", messages: [agentMsg], result },
      { type: "reset" },
    );
    expect(state).toEqual(initialState);
  });

  it("로딩 외 success 는 무시", () => {
    expect(studioReducer(initialState, { type: "success", agentMessage: agentMsg, result })).toEqual(
      initialState,
    );
  });
});
