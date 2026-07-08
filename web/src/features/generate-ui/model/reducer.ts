import type { GenerationResult } from "@/shared/types/schemas";

export type GenerationStatus = "idle" | "loading" | "success" | "error";

export interface GenerationState {
  status: GenerationStatus;
  result?: GenerationResult;
  error?: string;
}

export type GenerationAction =
  | { type: "submit" }
  | { type: "success"; result: GenerationResult }
  | { type: "error"; error: string }
  | { type: "reset" };

export function generationReducer(
  state: GenerationState,
  action: GenerationAction,
): GenerationState {
  switch (action.type) {
    case "submit":
      return { status: "loading" };
    case "success":
      // loading 상태에서만 수용(경쟁 회피)
      if (state.status !== "loading") return state;
      return { status: "success", result: action.result };
    case "error":
      return { status: "error", error: action.error };
    case "reset":
      return { status: "idle" };
    default:
      return state;
  }
}

export const initialState: GenerationState = { status: "idle" };
