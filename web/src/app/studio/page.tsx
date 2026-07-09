"use client";

import { useReducer } from "react";
import { ConversationPanel, initialState, studioReducer } from "@/features/studio";
import { TopBar } from "@/widgets/top-bar";
import { StudioToolbar } from "@/widgets/studio-toolbar";
import { StudioCanvas } from "@/widgets/studio-canvas";
import { createSession, postSessionMessage } from "@/shared/api/sessions";

export default function StudioPage() {
  const [state, dispatch] = useReducer(studioReducer, initialState);

  async function handleSubmit(prompt: string) {
    // 생성 중 중복 전송 차단(연타 → 중복 세션 생성 방지)
    if (state.phase === "loading") return;
    dispatch({ type: "submit", prompt });
    try {
      // 첫 전송 시 세션 생성
      if (!state.sessionId) {
        const { id } = await createSession();
        dispatch({ type: "sessionCreated", sessionId: id });
        const res = await postSessionMessage(id, prompt);
        dispatch({ type: "success", agentMessage: res.agent_message, result: res.result });
      } else {
        const res = await postSessionMessage(state.sessionId, prompt);
        dispatch({ type: "success", agentMessage: res.agent_message, result: res.result });
      }
    } catch (e) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : String(e) });
    }
  }

  return (
    <main className="view">
      <TopBar active="studio" />
      <StudioToolbar onReset={() => dispatch({ type: "reset" })} hasResult={state.result !== null} />

      <div className="studio-grid grid" style={{ gridTemplateColumns: "42% 1fr" }}>
        <ConversationPanel
          phase={state.phase}
          messages={state.messages}
          pendingPrompt={state.pendingPrompt}
          error={state.error}
          onSubmit={handleSubmit}
        />
        <StudioCanvas phase={state.phase} result={state.result} />
      </div>
    </main>
  );
}
