"use client";

import { useReducer } from "react";
import { GenerationForm, initialState, generationReducer } from "@/features/generate-ui";
import { createGeneration } from "@/shared/api";
import type { GenerationRequest } from "@/shared/types";
import { ResultViewer } from "@/widgets/result-viewer";
import { TopBar } from "@/widgets/top-bar";

export default function StudioPage() {
  const [state, dispatch] = useReducer(generationReducer, initialState);

  async function handleSubmit(request: GenerationRequest) {
    dispatch({ type: "submit" });
    try {
      const result = await createGeneration(request);
      dispatch({ type: "success", result });
    } catch (e) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : String(e) });
    }
  }

  return (
    <main className="view">
      <TopBar active="studio" />
      <div className="mx-auto max-w-5xl space-y-6 p-6">
        <header>
          <h1 className="font-serif text-2xl text-text">스튜디오</h1>
          <p className="text-sm text-text-muted">
            기획을 입력하면 화면·상태·토큰·코드까지. (대화형 프롬프트는 곧 추가)
          </p>
        </header>

        <section className="rounded-lg border border-border bg-surface p-4">
          <GenerationForm onSubmit={handleSubmit} disabled={state.status === "loading"} />
        </section>

        {state.status === "loading" && <p className="text-text-muted">생성 중...</p>}
        {state.status === "error" && (
          <p role="alert" className="text-danger">
            오류: {state.error}
          </p>
        )}
        {state.status === "success" && state.result && <ResultViewer result={state.result} />}
      </div>
    </main>
  );
}
