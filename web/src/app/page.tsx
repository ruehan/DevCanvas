"use client";

import { useReducer } from "react";
import { GenerationForm } from "@/features/generate-ui";
import { initialState, generationReducer } from "@/features/generate-ui";
import { createGeneration } from "@/shared/api";
import type { GenerationRequest } from "@/shared/types/schemas";
import { ResultViewer } from "@/widgets/result-viewer";

export default function HomePage() {
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
    <main className="mx-auto max-w-5xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-semibold">DevCanvas</h1>
        <p className="text-sm text-gray-600">
          개발자 중심 AI UI 설계/구현 플랫폼 — 기획을 입력하면 화면·상태·토큰·코드까지.
        </p>
      </header>

      <section className="rounded border p-4">
        <GenerationForm onSubmit={handleSubmit} disabled={state.status === "loading"} />
      </section>

      {state.status === "loading" && <p className="text-gray-500">생성 중...</p>}
      {state.status === "error" && (
        <p role="alert" className="text-red-600">
          오류: {state.error}
        </p>
      )}
      {state.status === "success" && state.result && <ResultViewer result={state.result} />}
    </main>
  );
}
