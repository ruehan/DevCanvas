import { describe, it, expect } from "vitest";
import { generationReducer, type GenerationState } from "./reducer";
import type { GenerationResult } from "@/shared/types/schemas";

const result = { input: { prompt: "x" } } as GenerationResult;

const idle: GenerationState = { status: "idle" };

describe("features/generate-ui/model/reducer", () => {
  it("submit → loading", () => {
    expect(generationReducer(idle, { type: "submit" })).toEqual({ status: "loading" });
  });

  it("success → 결과 저장", () => {
    const state = generationReducer({ status: "loading" }, { type: "success", result });
    expect(state).toEqual({ status: "success", result });
  });

  it("error → 에러 메시지 저장", () => {
    const state = generationReducer({ status: "loading" }, { type: "error", error: "boom" });
    expect(state).toEqual({ status: "error", error: "boom" });
  });

  it("reset → idle", () => {
    const state = generationReducer({ status: "success", result }, { type: "reset" });
    expect(state).toEqual({ status: "idle" });
  });

  it("loading 중 아닐 때 success 는 무시", () => {
    expect(generationReducer(idle, { type: "success", result })).toEqual(idle);
  });
});
