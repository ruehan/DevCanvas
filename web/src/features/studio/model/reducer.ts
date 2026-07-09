import type { GenerationResult, Message } from "@/shared/types";

export type StudioPhase = "empty" | "loading" | "ready";

export interface StudioState {
  phase: StudioPhase;
  sessionId: string | null;
  messages: Message[];
  result: GenerationResult | null;
  error: string | null;
  pendingPrompt: string | null;
}

export type StudioAction =
  | { type: "sessionCreated"; sessionId: string }
  | { type: "submit"; prompt: string }
  | { type: "success"; agentMessage: Message; result: GenerationResult }
  | { type: "error"; error: string }
  | { type: "reset" };

export const initialState: StudioState = {
  phase: "empty",
  sessionId: null,
  messages: [],
  result: null,
  error: null,
  pendingPrompt: null,
};

export function studioReducer(state: StudioState, action: StudioAction): StudioState {
  switch (action.type) {
    case "sessionCreated":
      return { ...state, sessionId: action.sessionId };
    case "submit":
      return {
        ...state,
        phase: "loading",
        error: null,
        pendingPrompt: action.prompt,
        messages: [
          ...state.messages,
          { role: "user", content: action.prompt, steps: [] },
        ],
      };
    case "success":
      // 로딩 상태에서만 수용(경쟁 회피)
      if (state.phase !== "loading") return state;
      return {
        ...state,
        phase: "ready",
        result: action.result,
        pendingPrompt: null,
        error: null,
        messages: [...state.messages, action.agentMessage],
      };
    case "error":
      return {
        ...state,
        phase: state.result ? "ready" : "empty",
        pendingPrompt: null,
        error: action.error,
      };
    case "reset":
      return initialState;
    default:
      return state;
  }
}
